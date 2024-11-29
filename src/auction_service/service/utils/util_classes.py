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
    auction_id:UUID
    player_id:UUID
    gacha_id:UUID
    starting_price :int
    current_winning_player_id:UUID
    current_winning_bid:int
    end_time:int
    active:bool

class AuctionModifier(BaseModel):
    auction_id:Optional[UUID]
    player_id:Optional[UUID]
    gacha_id:Optional[UUID]
    starting_price :Optional[UUID]
    current_winning_player_id:Optional[UUID]
    current_winning_bid:Optional[UUID]
    end_time:Optional[UUID]
    active:Optional[UUID]

class Bid(BaseModel):
    bid_id:UUID
    auction_id:UUID
    player_id:UUID
    bid:int
    time:int

class BidModifier(BaseModel):
    bid_id:Optional[UUID]
    auction_id:Optional[UUID]
    player_id:Optional[UUID]
    bid:Optional[int]
    time:Optional[int]