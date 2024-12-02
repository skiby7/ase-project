import sys
from typing import Literal
import uuid
import os
import time
from logging import getLogger
from sqlalchemy import create_engine, or_, desc
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from routers.transactions.models import AuctionTransactionModel, PurchaseTransactionModel, RollTransactionModel
from libs.db.utils import transactional
from libs.db.tables import Base, RollTransaction, TuxPurchaseTransaction, InterUserTransaction, UserBalance, GameBalance, FreezedTux
from libs.exceptions import UserNotFound, AlreadySettled, InsufficientFunds, WrongOperation, AuctionNotFound, LowerBidException

unix_time = lambda: int(time.time())

logger = getLogger("uvicorn.error")

DATABASE_IP = os.getenv("DATABASE_IP")
DATABASE_PORT = os.getenv("DATABASE_PORT")
DATABASE_SCHEMA = os.getenv("DATABASE_SCHEMA")

with open("/run/secrets/tux_db_user") as f:
    DATABASE_USER = f.read().strip("\n").strip()

with open("/run/secrets/tux_db_password") as f:
    DATABASE_PASSWORD = f.read().strip("\n").strip()

DATABASE_URL = f"{DATABASE_SCHEMA}{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_IP}:{DATABASE_PORT}"

TEST_RUN = os.getenv("TEST_RUN", "false") == "true"
if TEST_RUN:
    import subprocess
    temp_dir = subprocess.run(["mktemp -d"], shell=True, text=True, capture_output=True).stdout
    DATABASE_URL = f"sqlite:///{temp_dir}"

if not DATABASE_URL:
    sys.exit(-1)

logger.info(f"Configured url {DATABASE_URL}")
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()



def create_tables():
    Base.metadata.create_all(engine)


@transactional
def create_user_balance(session, starting_fiat_balance: float, user_id: str):
    if starting_fiat_balance < 0:
        raise ValueError("The starting balance cannot be a negative number!")
    new_account = UserBalance(
        user_id=user_id,
        tux_amount=0.0,
        fiat_amount=starting_fiat_balance
    )
    session.add(new_account)


@transactional
def delete_user_balance(session, user_id: str):
    to_delete = session.query(UserBalance).filter_by(user_id=user_id).first()
    if not to_delete: return

    session.delete(to_delete)



@transactional
def create_purchase_transaction(session, purchased_tux: float, amount_fiat: float, amount_tux: float, user_id: str, filled: bool):
    if purchased_tux < 0:
        raise ValueError("The purchased tux amount cannot be a negative number!")
    logger.debug(f"Inserting purchase transaction {purchased_tux} {amount_fiat} {amount_tux} {user_id} {filled}")
    new_transaction = TuxPurchaseTransaction(
        transaction_id=str(uuid.uuid4()),
        purchased_tux=purchased_tux,
        amount_fiat=amount_fiat,
        amount_tux=amount_tux,
        timestamp=unix_time(),
        user_id=user_id,
        filled=filled
    )
    session.add(new_transaction)


@transactional
def create_roll_transaction(session, amount_tux: float, user_id: str, filled: bool):
    if amount_tux < 0:
        raise ValueError("The tux amount cannot be a negative number!")
    new_transaction = RollTransaction(
        transaction_id=str(uuid.uuid4()),
        amount_tux=amount_tux,
        timestamp=unix_time(),
        user_id=user_id,
        filled=filled
    )
    session.add(new_transaction)


@transactional
def create_user_transaction(session, auction_id: str, tux_amount: float, from_id: str, to_id: str):
    if tux_amount < 0:
        raise ValueError("The tux amount cannot be a negative number!")
    if get_user_tux_balance(session, from_id) < tux_amount:
        raise InsufficientFunds(f"Cannot transfer {tux_amount} from {from_id} to {to_id}, insufficient funds")
    new_transaction = InterUserTransaction(
        transaction_id=str(uuid.uuid4()),
        auction_id=auction_id,
        amount_tux=tux_amount,
        timestamp=unix_time(),
        from_user_id=from_id,
        to_user_id=to_id
    )
    session.add(new_transaction)
    update_user_tux_balance(session, from_id, "withdraw", tux_amount)
    update_user_tux_balance(session, to_id, "deposit", tux_amount)


def user_exists(session, user_id: str):
    return session.query(UserBalance).filter_by(user_id=user_id).first() is not None

def auction_exists(session, auction_id: str):
    return session.query(FreezedTux).filter_by(auction_id=auction_id).first() is not None

def get_user_purchase_transactions(session,user_id: str) -> list[PurchaseTransactionModel]:
    transactions = []
    for t in session.query(TuxPurchaseTransaction).filter_by(user_id=user_id).all():
        transactions.append(PurchaseTransactionModel(
            purchased_tux=t.purchased_tux,
            transaction_id=t.transaction_id,
            amount_fiat=t.amount_fiat,
            amount_tux=t.amount_tux,
            timestamp=t.timestamp,
            user_id=t.user_id,
            filled=t.filled))
    return transactions


def get_user_auction_transactions(session, user_id: str) -> list[AuctionTransactionModel]:
    transactions = []
    for t in session.query(InterUserTransaction).filter(or_(
        InterUserTransaction.from_user_id==user_id,
        InterUserTransaction.to_user_id==user_id)).all():
        transactions.append(AuctionTransactionModel(
            transaction_id=t.transaction_id,
            auction_id=t.auction_id,
            amount_tux=t.amount_tux,
            timestamp=t.timestamp,
            from_user_id=t.from_user_id,
            to_user_id=t.to_user_id))
    return transactions


def get_user_roll_transactions(session, user_id: str) -> list[RollTransactionModel]:
    transactions = []
    for t in session.query(RollTransaction).filter_by(user_id=user_id).all():
        transactions.append(RollTransactionModel(
            transaction_id=t.transaction_id,
            amount_tux=t.amount_tux,
            timestamp=t.timestamp,
            user_id=t.user_id,
            filled=t.filled))
    return transactions


def get_user_fiat_balance(session, user_id: str) -> float:
    balance = session.query(UserBalance.fiat_amount).filter_by(user_id=user_id).first()
    if balance is None:
        raise UserNotFound(f"{user_id} not found")
    return balance[0]



def get_user_tux_balance(session, user_id: str) -> float:
    balance = session.query(UserBalance.tux_amount).filter_by(user_id=user_id).first()
    if balance is None:
        raise UserNotFound(f"{user_id} not found")
    return balance[0]



@transactional
def buy_tux(session, user_id: str, tux_amount: float, fiat_amount: float):
    if tux_amount < 0 or fiat_amount < 0:
        raise ValueError("The tux amount and the fiat amount cannot be a negative number!")
    row: UserBalance = session.query(UserBalance).filter_by(user_id=user_id).first()
    if row:
        if row.fiat_amount < fiat_amount:  # type: ignore
            raise InsufficientFunds(f"{user_id} cannot afford to pay {fiat_amount} fiat value")
        row.fiat_amount -= fiat_amount  # type: ignore
        row.tux_amount += tux_amount  # type: ignore
    else:
        raise UserNotFound(f"{user_id} not found")
    create_purchase_transaction(session, tux_amount, row.tux_amount, row.fiat_amount, user_id, True)  # type: ignore
    update_game_balance(session, tux_amount, 0, fiat_amount)



@transactional
def roll_gacha(session, user_id: str, roll_price: float):
    update_user_tux_balance(session, user_id, "withdraw", roll_price)
    update_game_balance(session, 0, roll_price, 0)
    create_roll_transaction(session, roll_price, user_id, True)



@transactional
def increase_user_fiat_balance(session, user_id: str, amount: float):
    if amount < 0:
        raise ValueError("The amount cannot be a negative number!")
    row: UserBalance = session.query(UserBalance).filter_by(user_id=user_id).first()
    if row:
            row.fiat_amount += amount  # type: ignore
    else:
        raise UserNotFound(f"{user_id} not found")


@transactional
def update_user_tux_balance(session, user_id: str, operation: Literal["withdraw", "deposit"], tux_amount: float):

    if tux_amount < 0:
        raise ValueError("The tux amount cannot be a negative number!")
    row: UserBalance = session.query(UserBalance).filter_by(user_id=user_id).first()
    if row:
        if operation == "withdraw":
            if row.tux_amount < tux_amount:  # type: ignore
                raise InsufficientFunds(f"Cannot withdraw more than {row.tux_amount} tux!")
            row.tux_amount -= tux_amount  # type: ignore
        elif operation == "deposit":
            row.tux_amount += tux_amount  # type: ignore
        else:
            raise WrongOperation(f"Operation {operation} not supported!")
        logger.debug(f"{operation} -> ({user_id}, {tux_amount} tux)")
    else:
        raise UserNotFound(f"{user_id} not found")



@transactional
def update_game_balance(session, emitted_tux: float, tux_spent: float, fiat: float):
    if emitted_tux < 0 or tux_spent < 0 or fiat < 0:
        raise ValueError("The tux amount, the fiat amount and the emitted_tux cannot be a negative number!")
    try:
        balance: GameBalance = session.query(GameBalance).order_by(GameBalance.timestamp.desc()).first()
        if not balance:
            new_balance = GameBalance(timestamp=unix_time(), tux_emitted=emitted_tux, fiat_earned=fiat)
        else:
            new_balance = GameBalance(
                timestamp=unix_time(),
                tux_emitted=balance.tux_emitted + emitted_tux,
                tux_spent=balance.tux_spent + tux_spent if balance.tux_spent is not None else tux_spent,
                fiat_earned=balance.fiat_earned + fiat,
            )

        session.add(new_balance)
    except SQLAlchemyError as e:
        logger.error(f"Cannot update game balance: {e}")


def get_highest_bidder(session, auction_id: str):
    highest_bidder = session.query(FreezedTux).filter_by(auction_id=auction_id).order_by(desc(FreezedTux.tux_amount)).first()
    if highest_bidder is None:
        raise AuctionNotFound(f"Cannot find auction {auction_id}")
    logger.debug(f"Highest bidder: {highest_bidder.user_id} - Bid: {highest_bidder.tux_amount}")
    return highest_bidder.user_id, highest_bidder.tux_amount


@transactional
def update_freezed_tux(session, auction_id: str, user_id: str, new_tux_amount: float):
    """
        Only the higher betting player should be freezed, so every time I receive a
        freeze request, I unfreeze all the other players
    """
    logger.debug(f"updating bid of auction {auction_id} -> ({user_id}, {new_tux_amount} tux)")
    if new_tux_amount < 0:
        raise ValueError("The new tux amount cannot be a negative number!")
    try:
        try:
            highest_bidder_id, highest_bid = get_highest_bidder(session, auction_id)
        except:
            highest_bidder_id, highest_bid = (None, 0)
        if highest_bid >= new_tux_amount:
            raise LowerBidException(f"Current bid is {highest_bid}, cannot bid {new_tux_amount}")

        bidder = session.query(FreezedTux).filter_by(auction_id=auction_id, user_id=user_id).first()
        if bidder:
            if bidder.settled:
                raise AlreadySettled(f"Already settled {auction_id} for user {user_id}")

            user_current_balance = get_user_tux_balance(session, user_id)
            user_current_balance += bidder.tux_amount

            if new_tux_amount > user_current_balance: # Here you exit without changing anything
                logger.error(f"Trying to freeze {new_tux_amount} tux with {user_current_balance} tux available")
                raise InsufficientFunds(f"Trying to freeze {new_tux_amount} tux with {user_current_balance} tux available")

        else:
            user_current_balance = get_user_tux_balance(session, user_id)
            if new_tux_amount > user_current_balance: # Here you exit without changing anything
                logger.error(f"Trying to freeze {new_tux_amount} tux with {user_current_balance} tux available")
                raise InsufficientFunds(f"Trying to freeze {new_tux_amount} tux with {user_current_balance} tux available")

            bidder = FreezedTux(
                auction_id=auction_id,
                user_id=user_id,
                tux_amount=0,
                last_update=unix_time(),
                settled=False
            )
            session.add(bidder)

        if highest_bid > 0 and highest_bidder_id is not None:
            update_user_tux_balance(session, highest_bidder_id, "deposit", highest_bid)
        update_user_tux_balance(session, user_id, "withdraw", new_tux_amount)
        bidder.tux_amount = new_tux_amount  # type: ignore
        bidder.last_update = unix_time()  # type: ignore


    except SQLAlchemyError as e:
        logger.error(f"Cannot update freezed tux amount ({new_tux_amount} tux) of auction_id::user_id {auction_id}::{user_id}: {e}")
        raise


@transactional
def delete_auction(session, auction_id: str):
    try:
        bidders = session.query(FreezedTux).filter_by(auction_id=auction_id).all()

        if bidders is None:
            raise AuctionNotFound(f"Cannot find {auction_id}")

        for b in bidders:
            if b.settled: continue
            b.settled = True
            if b.tux_amount > 0:
                update_user_tux_balance(session, b.user_id, "deposit", b.tux_amount)


    except SQLAlchemyError as e:
        logger.error(f"Cannot update settle payments for auction {auction_id}: {e}")
        raise

@transactional
def settle_auction_payments(session, auction_id: str, winner_id: str, auctioneer_id: str):
    try:
        bidder = session.query(FreezedTux).filter_by(auction_id=auction_id, user_id=winner_id).first()
        if bidder is None:
            raise UserNotFound(f"User {winner_id} is not bidding in auction {auction_id}")
        if bidder.settled:
            raise AlreadySettled(f"Already settled {auction_id} for user {winner_id}")

        update_user_tux_balance(session, bidder.user_id, "deposit", bidder.tux_amount)
        create_user_transaction(session, auction_id, bidder.tux_amount, winner_id, auctioneer_id)
        bidder.settled = True

        other_bidders = session.query(FreezedTux).filter_by(auction_id=auction_id)
        for b in other_bidders:
            b.settled = True


    except SQLAlchemyError as e:
        logger.error(f"Cannot update settle payments for auction {auction_id}: {e}")
        raise
