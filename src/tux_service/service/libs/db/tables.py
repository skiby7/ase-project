from sqlalchemy import Column, Float, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class TuxPurchaseTransaction(Base):  # type: ignore
    __tablename__ = 'tux_purchase_transactions'
    transaction_id = Column(String, primary_key=True)
    purchased_tux = Column(Float, nullable=False)
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
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(Integer, nullable=False)
    tux_emitted = Column(Float, nullable=False)
    tux_spent = Column(Float, nullable=True)
    fiat_earned = Column(Float, nullable=False)

class FreezedTux(Base):
    __tablename__ = 'freezed_tuxs'
    auction_id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False, index=True)
    tux_amount = Column(Float, nullable=False)
    last_update = Column(Integer, nullable=False)
    settled = Column(Boolean, nullable=False)
