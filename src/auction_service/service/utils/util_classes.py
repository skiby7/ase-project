from pydantic import BaseModel
from uuid import UUID
from typing import Optional
from enum import Enum


class IdStrings(Enum):
    AUCTION_ID = "auction_id"
    PLAYER_ID = "player_id"
    BID_ID = "bid_id"
    GACHA_ID = "gacha_id"


class AuctionCreate(BaseModel):
    player_id: UUID
    gacha_name: str
    starting_price: int
    end_time: int

class AuctionPublic(BaseModel):
    auction_id: str
    player_id: UUID
    gacha_name: str
    starting_price: int
    end_time: int


class AuctionOptional(BaseModel):
    player_id: Optional[UUID] = None
    gacha_name: Optional[str] = None
    starting_price: Optional[int] = None
    current_winning_player_id: Optional[int] = None
    current_winning_bid: Optional[int] = None
    end_time: Optional[int] = None
    active: Optional[bool] = None


class Bid(BaseModel):
    auction_id: UUID
    player_id: UUID
    bid: int


class BidOptional(BaseModel):
    bid_id: Optional[UUID]
    auction_id: Optional[UUID]
    player_id: Optional[UUID]
    bid: Optional[int]
    time: Optional[int]


class AuthId(BaseModel):
    uid: str
