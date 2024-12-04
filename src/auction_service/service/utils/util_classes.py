from pydantic import BaseModel
from uuid import UUID
from typing import Optional
from enum import Enum
class IdStrings(Enum):
    AUCTION_ID = "auction_id"
    PLAYER_ID = "player_id"
    BID_ID = "bid_id"
    GACHA_ID = "gacha_id"


class Auction(BaseModel):
    player_id:UUID
    gacha_name:str
    starting_price :int
    end_time:int


class AuctionOptional(BaseModel):
    player_id:Optional[UUID]
    gacha_name:Optional[str]
    starting_price:Optional[int]
    current_winning_player_id:Optional[int]
    current_winning_bid:Optional[int]
    end_time:Optional[int]
    active:Optional[bool]


class Bid(BaseModel):
    auction_id:UUID
    player_id:UUID
    bid:int


class BidOptional(BaseModel):
    bid_id:Optional[UUID]
    auction_id:Optional[UUID]
    player_id:Optional[UUID]
    bid:Optional[int]
    time:Optional[int]

class AuthId(BaseModel):
    uid:str