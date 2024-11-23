import sys
from typing import Literal
import uuid
import os
import time
from functools import wraps
from logging import getLogger
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.util import to_set
from sqlalchemy.exc import SQLAlchemyError
from libs.db.utils import transactional
from libs.db.tables import Base, TuxPurchaseTransaction, InterUserTransaction, UserBalance, GameBalance, FreezedTux
from routers.transactions.models import PurchaseTransactionModel
from libs.mocks import MockSession, use_mocks
from tux_service.service.routers.payments import payments

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
    return new_transaction


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
        # try to raise an exception and check that the operation rollsback

    return new_transaction


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
    return session.query(UserBalance.fiat_amount).filter_by(user_id=user_id).first()


@use_mocks
def get_user_tux_balance(session, user_id: str) -> float:
    return session.query(UserBalance.tux_amount).filter_by(user_id=user_id).first()


@use_mocks
@transactional
def buy_tux(session, user_id: str, tux_amount: float, fiat_amount: float):
    row: UserBalance = session.query(UserBalance).filter_by(user_id=user_id).first()
    if row:
        row.fiat_amount -= new_balance  # type: ignore
        row.tux_amount += tux_amount  # type: ignore
    else:
        raise Exception(f"{user_id} not found")
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
            raise Exception(f"Operation {operation} not supported!")
    else:
        raise Exception(f"{user_id} not found")

@use_mocks
@transactional
def update_game_balance(session, emitted_tux: float, fiat: float):
    try:
        balance: GameBalance = session.query(GameBalance).first()

        if not balance:
            balance = GameBalance(tux_emitted=emitted_tux, fiat_earned=fiat)
            session.add(balance)
        else:
            balance.fiat_earned += fiat  # type: ignore
            balance.tux_emitted += emitted_tux  # type: ignore

    except SQLAlchemyError as e:
        logger.error(f"Cannot update game balance: {e}")

@use_mocks
def update_freezed_tux(session, auction_id: str, user_id: str, new_tux_amount: float) -> bool:
    try:
        with session.begin():
            user_current_balance = get_user_tux_balance(session, user_id)
            if new_tux_amount > user_current_balance:
                logger.error(f"Trying to freeze {new_tux_amount} tux with {user_current_balance} tux available")
                return False

            user_balance: UserBalance = session.query(UserBalance).filter_by(user_id=user_id).first()
            if user_balance:
                user_balance.fiat_amount = new_balance  # type: ignore
                user_balance.tux_amount = tux_amount  # type: ignore
            else:
                logger.error(f"Cannot find user balance for user_id {user_id}")
                return False


            freezed: FreezedTux = session.query(FreezedTux).filter_by(auction_id=auction_id, user_id=user_id).first()
            if freezed:
                freezed = FreezedTux(auction_id=auction_id, user_id=user_id, tux_amount=new_tux_amount, last_update=unix_time())
                session.add(freezed)
            else:
                freezed.tux_amount += new_tux_amount  # type: ignore
                freezed.last_update += unix_time()  # type: ignore

    except SQLAlchemyError as e:
        logger.error(f"Cannot update freezed tux amount ({new_tux_amount} tux) of auction_id::user_id {auction_id}::{user_id}: {e}")
        return False
    return True


def _get_freezed_payments(freezed: list[FreezedTux], winner_id: str) -> tuple[list[dict], float]:
    payments = []
    winning_amount = 0.0
    for f in freezed:
        payments.append({
            "user_id" : f.user_id,
            "amount" : f.tux_amount,
            "is_winner" : winner_id == f.user_id
        })
        if winner_id == f.user_id:
            winning_amount = f.tux_amount
    return payments, winning_amount #  type: ignore

@use_mocks
@transactional
def settle_auction_payments(session, auction_id: str, winner_id: str, auctioneer_id: str):
    try:
        auction_freezed_tux = session.query(FreezedTux).filter_by(auction_id=auction_id)
        payments, winning_amount = _get_freezed_payments(auction_freezed_tux, winner_id)

        for p in payments:
            row: UserBalance = session.query(UserBalance).filter_by(user_id=p["user_id"]).first()
            if not row:
                logger.debug(f"Cannot settle payments {p}")
                continue
            if p["is_winner"] or p["is_auctioneer"]:  #  handle the transaction later
                continue
            else:
                row.tux_amount += p["amount"]

        create_user_transaction(session, winning_amount, winner_id, auctioneer_id)

    except SQLAlchemyError as e:
        logger.error(f"Cannot update settle payments for auction {auction_id}: {e}")
        return False
    return True
