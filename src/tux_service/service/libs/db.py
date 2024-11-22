import sys
import uuid
import os
from sqlalchemy import create_engine, Column, Float, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from routers.transactions.models import TransactionModel
from tux_service.service.libs.db_mocks import use_mocks

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    sys.exit(-1)

Base = declarative_base()


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
