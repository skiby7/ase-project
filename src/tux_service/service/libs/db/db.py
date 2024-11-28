import sys
from typing import Literal
import uuid
import os
import time
from logging import getLogger
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from libs.db.utils import transactional
from libs.db.tables import Base, TuxPurchaseTransaction, InterUserTransaction, UserBalance, GameBalance, FreezedTux
from routers.transactions.models import PurchaseTransactionModel
from libs.mocks import MockSession, use_mocks
from libs.exceptions import UserNotFound, AlreadySettled, InsufficientFunds, WrongOperation

unix_time = lambda: int(time.time())

logger = getLogger("uvicorn.error")


DATABASE_URL = os.getenv("DATABASE_URL")
TEST_RUN = os.getenv("TEST_RUN", "false") == "true"
logger.debug(f"Is test run: {TEST_RUN}")

if not DATABASE_URL and not TEST_RUN:
    sys.exit(-1)

if DATABASE_URL:
    logger.info(f"Configured url {DATABASE_URL}")
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
else:
    Session = MockSession


def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()


@use_mocks
def create_tables():
    Base.metadata.create_all(engine)

@use_mocks
@transactional
def create_user_balance(session, starting_fiat_balance: float, user_id: str):
    new_account = UserBalance(
        user_id=user_id,
        tux_amount=0.0,
        fiat_amount=starting_fiat_balance
    )
    session.add(new_account)

@use_mocks
@transactional
def delete_user_balance(session, user_id: str):
    to_delete = session.query(UserBalance).filter_by(user_id=user_id).first()
    if not to_delete:
        raise UserNotFound(f"Cannot find {user_id}")

    session.delete(to_delete)


@use_mocks
@transactional
def create_purchase_transaction(session, amount_fiat: float, amount_tux: float, user_id: str, filled: bool):
    new_transaction = TuxPurchaseTransaction(
        transaction_id=str(uuid.uuid4()),
        amount_fiat=amount_fiat,
        amount_tux=amount_tux,
        timestamp=unix_time(),
        user_id=user_id,
        filled=filled
    )
    session.add(new_transaction)


@use_mocks
@transactional
def create_user_transaction(session, tux_amount: float, from_id: str, to_id: str):
    if get_user_tux_balance(session, from_id) < tux_amount:
        raise Exception(f"Cannot transfer {tux_amount} from {from_id} to {to_id}, insufficient funds")
    new_transaction = InterUserTransaction(
        transaction_id=str(uuid.uuid4()),
        amount_tux=tux_amount,
        timestamp=unix_time(),
        from_user_id=from_id,
        to_user_id=to_id
    )
    session.add(new_transaction)
    update_user_tux_balance(session, from_id, "withdraw", tux_amount)
    update_user_tux_balance(session, to_id, "deposit", tux_amount)
    # TODO:
        # try to raise an exception and check that the operation rolls back


@use_mocks
def get_transaction_by_id(session, transaction_id: str):
    transaction = session.query(TuxPurchaseTransaction).filter_by(transaction_id=transaction_id).first()
    return PurchaseTransactionModel(
                transaction_id=transaction.transaction_id,
                amount_fiat=transaction.amount_fiat,
                amount_tux=transaction.amount_tux,
                timestamp=transaction.timestamp,
                user_id=transaction.user_id,
                filled=transaction.filled)


@use_mocks
def get_user_transactions(session, user_id: str) -> list[PurchaseTransactionModel]:
    transactions = []
    for t in session.query(TuxPurchaseTransaction).filter_by(user_id=user_id).all():
        transactions.append(PurchaseTransactionModel(
            transaction_id=t.transaction_id,
            amount_fiat=t.amount_fiat,
            amount_tux=t.amount_tux,
            timestamp=t.timestamp,
            user_id=t.user_id,
            filled=t.filled))
    return transactions


@use_mocks
def get_user_fiat_balance(session, user_id: str) -> float:
    balance = session.query(UserBalance.fiat_amount).filter_by(user_id=user_id).first()
    if balance is None:
        raise UserNotFound(f"{user_id} not found")
    return balance


@use_mocks
def get_user_tux_balance(session, user_id: str) -> float:
    balance = session.query(UserBalance.tux_amount).filter_by(user_id=user_id).first()
    if balance is None:
        raise UserNotFound(f"{user_id} not found")
    return balance


@use_mocks
@transactional
def buy_tux(session, user_id: str, tux_amount: float, fiat_amount: float):
    row: UserBalance = session.query(UserBalance).filter_by(user_id=user_id).first()
    if row:
        row.fiat_amount -= fiat_amount  # type: ignore
        row.tux_amount += tux_amount  # type: ignore
    else:
        raise UserNotFound(f"{user_id} not found")
    update_game_balance(session, tux_amount, fiat_amount)


@use_mocks
@transactional
def update_user_tux_balance(session, user_id: str, operation: Literal["withdraw", "deposit"], tux_amount: float):
    row: UserBalance = session.query(UserBalance).filter_by(user_id=user_id).first()
    if row:
        if operation == "withdraw":
            row.tux_amount -= tux_amount  # type: ignore
        elif operation == "deposit":
            row.tux_amount += tux_amount  # type: ignore
        else:
            raise WrongOperation(f"Operation {operation} not supported!")
    else:
        raise UserNotFound(f"{user_id} not found")


@use_mocks
@transactional
def update_game_balance(session, emitted_tux: float, fiat: float):
    try:
        balance: GameBalance = session.query(GameBalance).order_by(GameBalance.timestamp.desc()).first()
        if not balance:
            new_balance = GameBalance(timestamp=unix_time(), tux_emitted=emitted_tux, fiat_earned=fiat)
        else:
            new_balance = GameBalance(
                timestamp=unix_time(),
                tux_emitted=balance.emitted_tux + emitted_tux,
                fiat_earned=balance.fiat_earned + fiat,
            )

        session.add(new_balance)
    except SQLAlchemyError as e:
        logger.error(f"Cannot update game balance: {e}")


@use_mocks
@transactional
def update_freezed_tux(session, auction_id: str, user_id: str, new_tux_amount: float):
    """
        Only the higher betting player should be freezed, so every time I receive a
        freeze request, I unfreeze all the other players
    """
    try:
        user_current_balance = get_user_tux_balance(session, user_id)
        bidder = session.query(FreezedTux).filter_by(auction_id=auction_id, user_id=user_id)
        if bidder:
            if bidder.settled:
                raise AlreadySettled(f"Already settled {auction_id} for user {user_id}")
            user_current_balance += bidder.tux_amount
        else:
            raise UserNotFound(f"User {user_id} is not bidding in auction {auction_id}")
        if new_tux_amount > user_current_balance: # Here you exit without changing anything
            logger.error(f"Trying to freeze {new_tux_amount} tux with {user_current_balance} tux available")
            raise InsufficientFunds(f"Trying to freeze {new_tux_amount} tux with {user_current_balance} tux available")

        bidding_users: list[FreezedTux] = session.query(FreezedTux).filter_by(auction_id=auction_id)
        for bidder in bidding_users:
            if bidder.tux_amount != 0:  # type: ignore
                update_user_tux_balance(session, bidder.user_id, "deposit", bidder.tux_amount)  # type: ignore
            if bidder.user_id == user_id:  # type: ignore
                update_user_tux_balance(session, bidder.user_id, "withdraw", new_tux_amount)  # type: ignore

    except SQLAlchemyError as e:
        logger.error(f"Cannot update freezed tux amount ({new_tux_amount} tux) of auction_id::user_id {auction_id}::{user_id}: {e}")
        raise


@use_mocks
@transactional
def settle_auction_payments(session, auction_id: str, winner_id: str, auctioneer_id: str):
    try:
        bidder = session.query(FreezedTux).filter_by(auction_id=auction_id, user_id=winner_id)
        if bidder is None:
            raise UserNotFound(f"User {winner_id} is not bidding in auction {auction_id}")
        if bidder.settled:
            raise AlreadySettled(f"Already settled {auction_id} for user {winner_id}")

        update_user_tux_balance(session, bidder.user_id, "deposit", bidder.tux_amount)
        create_user_transaction(session, bidder.tux_amount, winner_id, auctioneer_id)
        bidder.settled = True

    except SQLAlchemyError as e:
        logger.error(f"Cannot update settle payments for auction {auction_id}: {e}")
        raise
