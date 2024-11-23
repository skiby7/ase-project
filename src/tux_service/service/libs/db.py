import sys
import uuid
import os
from logging import getLogger
from sqlalchemy import create_engine, Column, Float, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from routers.transactions.models import TransactionModel
from libs.mocks import MockSession, use_mocks

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


class Transaction(Base):  # type: ignore
    __tablename__ = 'transactions'

    transaction_id = Column(String, primary_key=True)
    amount_fiat = Column(Float, nullable=False)
    amount_tux = Column(Float, nullable=False)
    timestamp = Column(Integer, nullable=False)
    user_id = Column(String, nullable=False, index=True)
    filled = Column(Boolean, nullable=False)


class Balance(Base):  # type: ignore
    __tablename__ = 'balances'
    user_id = Column(String, primary_key=True)
    tux_amount = Column(Float, nullable=False)
    fiat_amount = Column(Float, nullable=False)

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
def create_transaction(session, amount_fiat, amount_tux, timestamp, user_id, filled):
    new_transaction = Transaction(
        transaction_id=str(uuid.uuid4()),
        amount_fiat=amount_fiat,
        amount_tux=amount_tux,
        timestamp=timestamp,
        user_id=user_id,
        filled=filled
    )
    session.add(new_transaction)
    session.commit()
    return new_transaction


def get_transaction_by_id(session, transaction_id):
    transaction = session.query(Transaction).filter_by(transaction_id=transaction_id).first()
    return TransactionModel(
                transaction_id=transaction.transaction_id,
                amount_fiat=transaction.amount_fiat,
                amount_tux=transaction.amount_tux,
                timestamp=transaction.timestamp,
                user_id=transaction.user_id,
                filled=transaction.filled)


def get_user_transactions(session, user_id) -> list[TransactionModel]:
    transactions = []
    for t in session.query(Transaction).filter_by(user_id=user_id).all():
        transactions.append(TransactionModel(
            transaction_id=t.transaction_id,
            amount_fiat=t.amount_fiat,
            amount_tux=t.amount_tux,
            timestamp=t.timestamp,
            user_id=t.user_id,
            filled=t.filled))
    return transactions

@use_mocks
def get_fiat_balance(session, user_id) -> float:
    return session.query(Balance).filter_by(user_id=user_id).first()

@use_mocks
def save_tux_transfer(session, user_id, tux_amount, new_balance):
    row: Balance = session.query(Balance).filter_by(user_id=user_id).first()
    if row:
        row.fiat_amount = new_balance
        row.tux_amount = tux_amount
        session.commit()
