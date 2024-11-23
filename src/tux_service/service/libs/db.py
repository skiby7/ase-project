import sys
import uuid
import os
import time
from logging import getLogger
from sqlalchemy import create_engine, Column, Float, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.util import to_set
from sqlalchemy.exc import SQLAlchemyError
from routers.transactions.models import PurchaseTransactionModel
from libs.mocks import MockSession, use_mocks
from tux_service.service.routers.payments import payments

unix_time = lambda: int(time.time())

logger = getLogger("uvicorn.error")


DATABASE_URL = os.getenv("DATABASE_URL")
TEST_RUN = os.getenv("TEST_RUN", "false") == "true"
logger.debug(f"Is test run: {TEST_RUN}")

Base = declarative_base()
if not DATABASE_URL and not TEST_RUN:
    sys.exit(-1)

if DATABASE_URL:
    logger.info(f"Configured url {DATABASE_URL}")
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
else:
    Session = MockSession


class TuxPurchaseTransaction(Base):  # type: ignore
    __tablename__ = 'tux_purchase_transactions'
    transaction_id = Column(String, primary_key=True)
    amount_fiat = Column(Float, nullable=False)
    amount_tux = Column(Float, nullable=False)
    timestamp = Column(Integer, nullable=False)
    user_id = Column(String, nullable=False, index=True)
    filled = Column(Boolean, nullable=False)

class InterUserTransaction(Base):  # type: ignore
    __tablename__ = 'inter_use_transactions'
    transaction_id = Column(String, primary_key=True)
    auction_id = Column(String, nullable=False, index=True)
    amount_tux = Column(Float, nullable=False)
    timestamp = Column(Integer, nullable=False)
    from_user_id = Column(String, nullable=False, index=True)
    to_user_id = Column(String, nullable=False, index=True)

class UserBalance(Base):  # type: ignore
    __tablename__ = 'user_balances'
    user_id = Column(String, primary_key=True)
    tux_amount = Column(Float, nullable=False)
    fiat_amount = Column(Float, nullable=False)

class GameBalance(Base):
    __tablename__ = 'game_balance'
    tux_emitted = Column(Float, nullable=False)
    fiat_earned = Column(Float, nullable=False)

class FreezedTux(Base):
    __tablename__ = 'freezed_tuxs'
    auction_id = Column(String, primary_key=True)
    auctioneer_id = Column(String, nullable=False, index=True)
    user_id = Column(String, nullable=False, index=True)
    tux_amount = Column(Float, nullable=False)
    last_update = Column(Integer, nullable=False)

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
    session.commit()
    return new_transaction


@use_mocks
def create_user_transaction(session, amount_fiat: float, amount_tux: float, from_id: str, to_id: str):
    new_transaction = InterUserTransaction(
        transaction_id=str(uuid.uuid4()),
        amount_fiat=amount_fiat,
        amount_tux=amount_tux,
        timestamp=unix_time(),
        from_user_id=from_id,
        to_user_id=to_id
    )
    session.add(new_transaction)
    session.commit()
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
def update_user_tux_balance(session, user_id: str, tux_amount: Float, new_balance: float):
    with session.begin()
        row: UserBalance = session.query(UserBalance).filter_by(user_id=user_id).first()
        if row:
            row.fiat_amount = new_balance  # type: ignore
            row.tux_amount = tux_amount  # type: ignore
            session.commit()


@use_mocks
def update_game_balance(session, emitted_tux: float, fiat: float):
    try:
        with session.begin():
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


def _get_freezed_payments(freezed: list[FreezedTux], winner_id: str) -> list[dict]:
    payments = []
    for f in freezed:
        payments.append({
            "user_id" : f.user_id,
            "amount" : f.tux_amount,
            "is_winner" : winner_id == f.user_id
        })
    return payments

@use_mocks
def settle_auction_payments(session, auction_id: str, winner_id: str, auctioneer_id: str):
    try:
        with session.begin():
            auction_freezed_tux = session.query(FreezedTux).filter_by(auction_id=auction_id)
            payments = _get_freezed_payments(auction_freezed_tux, winner_id)

            for p in payments:
                row: UserBalance = session.query(UserBalance).filter_by(user_id=p["user_id"]).first()
                if not row:
                    logger.debug(f"Cannot settle payments {p}")
                    continue
                if p["is_winner"] or p["is_auctioneer"]:  #
                    continue
                else:
                    row.tux_amount += p[""]


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
