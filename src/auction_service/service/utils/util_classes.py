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
    #auction_id:UUID created bd side
    player_id:UUID
    gacha_id:UUID
    starting_price :int
    #current_winning_player_id:UUID created bd side
    #current_winning_bid:int created bd side
    end_time:int
    #active:bool created bd side


class AuctionOptional(BaseModel):
    player_id:Optional[UUID]
    gacha_id:Optional[UUID]
    starting_price:Optional[int]
    current_winning_player_id:Optional[int]
    current_winning_bid:Optional[int]
    end_time:Optional[int]
    active:Optional[bool]


class Bid(BaseModel):
    #bid_id:UUID created db side
    auction_id:UUID
    player_id:UUID
    bid:int
    #time:int created bd side


class BidOptional(BaseModel):
    bid_id:Optional[UUID]
    auction_id:Optional[UUID]
    player_id:Optional[UUID]
    bid:Optional[int]
    time:Optional[int]
