from pymongo import MongoClient
import json
import uuid
import time

from pymongo.results import InsertOneResult, DeleteResult
from utils.util_classes import AuctionCreate, AuctionStatus, Bid, AuctionOptional, BidOptional, AuctionPublic
from fastapi import HTTPException
from uuid import UUID
import requests

unix_time = lambda: int(time.time())


class database:
    def __init__(self, auctionsFile, bidsFile, usersFile):
        self.auctionsFile = auctionsFile
        self.bidsFile = bidsFile
        self.usersFile = usersFile

        with open('/run/secrets/admin_account', 'r') as file:
            self.admin_account = json.load(file)["admin"]

        username = "root"
        host = "auction_db"
        port = "27017"
        db = "admin"
        database = "mydatabase"
        with open('/run/secrets/auction_pw', 'r') as file:
            password = file.read().strip()
        uri = f"mongodb://{username}:{password}@{host}:{port}/{database}?authSource={db}&tls=true&tlsAllowInvalidCertificates=true"

        self.client = MongoClient(uri)

        self.db = self.client["mydatabase"]

        if "auctions" in self.db.list_collection_names():
            print(" \n\n DB ACTIVE  \n\n")
        else:
            self.db_inizialization()

    def db_init_supp(self, collection, file):
        with open(file, "r") as file:
            data = json.load(file)
            if data: collection.insert_many(data)

    def db_inizialization(self):
        self.db.create_collection("auctions")
        auctions = self.db["auctions"]

        self.db.create_collection("bids")
        bids = self.db["bids"]

        self.db.create_collection("users")
        users = self.db["users"]

        self.db_init_supp(auctions, self.auctionsFile)
        self.db_init_supp(bids, self.bidsFile)
        self.db_init_supp(users, self.usersFile)

    ### SCHEDULED CHECK ###

    def checkAuctionExpiration(self, mock_check):
        current_time = unix_time()

        expired_auctions_cursor = self.db["auctions"].find({
            "end_time": {"$lt": current_time},
            "active": True
        })

        for auction in expired_auctions_cursor:
            self.edit_auction_status(mock_check, auction["auction_id"], False)

    ######### PLAYER #########

    ##### AUCTION #####

    # AUCTION_CREATE
    def auction_create(self, auction: AuctionCreate, mock_check: bool) -> AuctionPublic:

        # Player existence
        #if not mock_check:
        if not self.player_exists(str(auction.player_id)):
            raise HTTPException(400, "Player is not existent according knowledge base")


        if auction.starting_price < 0:
            raise HTTPException(status_code=400, detail="Invalid starting_price")
        if auction.end_time < unix_time():
            raise HTTPException(status_code=400, detail="Invalid time")

        # Distro check
        if not mock_check:
            access_token = self.auth_get_admin_token()
            self.gacha_remove_gacha(str(auction.player_id),
                                    auction.gacha_name, access_token)

        #if mock_check:
        #    id = str(UUID("00000000-0000-4000-8000-000000000000"))
        #else:
        id = str(uuid.uuid4())

        auction_to_insert = {
            "auction_id": str(id),
            "player_id": str(auction.player_id),
            "gacha_name": auction.gacha_name,
            "starting_price": auction.starting_price,
            "current_winning_player_id": None,
            "current_winning_bid": 0,
            "end_time": auction.end_time,
            "active": True
        }

        self.db["auctions"].insert_one(auction_to_insert)
        return AuctionPublic(**auction_to_insert)


    def get_auction_by_id(self, auction_id: UUID):
        auction = self.db["auctions"].find_one({"auction_id": str(auction_id)})
        if auction is None:
            raise HTTPException(status_code=404, detail="Auction does not exist")
        return auction

    # DONE
    # AUCTION_DELETE
    # HP auction presence == True (check app-side)
    def auction_delete(self, auction_id: str, mock_check: bool):
        auction = self.db["auctions"].find_one({"auction_id": auction_id})
        if not auction:
            return False

        if auction["end_time"] < unix_time() or not auction["active"]:
            raise HTTPException(status_code=400, detail="You cannot delete an expired or inactive auction")

        if not mock_check:
            token_data = self.auth_get_admin_token()
            self.gacha_add_gacha(str(auction["player_id"]), auction["gacha_name"], token_data)
            if auction["current_winning_player_id"] is not None:
                self.tux_delete_auction(str(auction_id), token_data)

        self.db["auctions"].delete_one({"auction_id": auction_id})
        self.db["bids"].delete_many({"auction_id": auction_id})

        return True

    def edit_auction_status(self, mock_check, auction_id: UUID, status: bool):
        if status:
           raise HTTPException(status_code=400, detail="Cannot activate an inactive auction")
        auction = self.db["auctions"].find_one({"auction_id": str(auction_id), "active": True})
        if not auction:
            raise HTTPException(status_code=404, detail="Auction does not exist or is not active")
        was_active = auction["active"]
        updated_field = {"active": status}
        result = self.db["auctions"].update_one(
            {"auction_id": str(auction_id)},
            {"$set": updated_field}
        )
        if result.modified_count <= 0:
            raise HTTPException(status_code=404, detail="Auction does not exist or is not active")
        if was_active and not status:
            self.close_auction(auction, mock_check)

    # DONE
    # AUCTION_FILTER
    def auction_filter(self, auction_filter: AuctionOptional):
        if auction_filter.starting_price is not None and auction_filter.starting_price < 0:
            raise HTTPException(status_code=400, detail="starting_price must be >=0")
        if auction_filter.current_winning_bid is not None and auction_filter.current_winning_bid < 0:
            raise HTTPException(status_code=400, detail="current_winning_bid must be >=0")
        if auction_filter.end_time is not None and auction_filter.end_time < 0:
            raise HTTPException(status_code=400, detail="end_time must be >=0")

        filtered_dict = {
            key: (str(value) if isinstance(value, UUID) else value)
            for key, value in auction_filter.model_dump().items()
            if value is not None
        }
        return list(self.db["auctions"].find(filtered_dict, {"_id": 0}))

    ##### BID #####

    # DONE
    # BID
    def bid(self, bid: Bid, auction_id: UUID, mock_check: bool):
        time_supp = unix_time()
        auction = self.db["auctions"].find_one({"auction_id": str(auction_id), "active": True})
        if auction is None:
            raise HTTPException(status_code=404, detail="Auction does not exist or is not active")
        if time_supp > auction["end_time"]:
            raise HTTPException(status_code=400, detail="Bid was made after the end of the auction")
        if str(bid.player_id) == auction["player_id"]:
            raise HTTPException(status_code=400, detail="Player is owner of auction")
        if bid.bid < auction["starting_price"]:
            raise HTTPException(status_code=400, detail="Bid must be higher than starting price")
        if bid.bid <= auction["current_winning_bid"]:
            raise HTTPException(status_code=400, detail="Bid must be higher than currently winning bid")

        # Player existence
        if not self.player_exists(str(bid.player_id)):
            raise HTTPException(400, "Player does not exists")

        # Tux freeze
        if not mock_check:
            access_token = self.auth_get_admin_token()
            self.tux_freeze_tux(str(bid.auction_id), str(bid.player_id), bid.bid, access_token)

        update = {}
        update["current_winning_player_id"] = str(bid.player_id)
        update["current_winning_bid"] = bid.bid

        self.db["auctions"].update_one({"auction_id": auction["auction_id"]}, {"$set": update})

        bidInsert = {}
        if mock_check:
            id = str(UUID("00000000-0000-4000-8000-000000000000"))
        else:
            id = str(uuid.uuid4())

        bidInsert["bid_id"] = id
        bidInsert["player_id"] = str(bid.player_id)
        bidInsert["time"] = unix_time()
        bidInsert["auction_id"] = auction["auction_id"]
        bidInsert["value"] = bid.bid

        self.db["bids"].insert_one(bidInsert)
        return {"bid_id" : bidInsert["bid_id"], "player_id" : bidInsert["player_id"], "time": bidInsert["time"], "auction_id" : bidInsert["auction_id"], "value" : bidInsert["value"]}


    def bid_filter(self, bid_filter: BidOptional):
        if bid_filter.bid is not None and bid_filter.bid < 0:
            raise HTTPException(status_code=400, detail="bid must be >=0")
        if bid_filter.time is not None and bid_filter.time < 0:
            raise HTTPException(status_code=400, detail="time must be >=0")

        filtered_dict = {
            key: (str(value) if isinstance(value, UUID) else value)
            for key, value in bid_filter.model_dump().items()
            if value is not None
        }

        return list(self.db["bids"].find(filtered_dict, {"_id": 0}))

    ######### ADMIN #########

    def market_activity(self):
        twenty_four_hours_ago = unix_time() - 86400
        auctions = self.db["bids"].find({"time": {"$gte": twenty_four_hours_ago}}, {"_id": 0})
        pipelineAvg = [
            {
                "$match": {
                    "time": {"$gte": twenty_four_hours_ago}
                }
            },
            {
                "$group": {
                    "_id": None,
                    "average_bid": {"$avg": "$bid"}
                }
            }
        ]

        pipelineCount = [
            {
                "$match": {
                    "time": {"$gte": twenty_four_hours_ago}
                }
            },
            {
                "$count": "total_bids"
            }
        ]


        avg_result = self.db["bids"].aggregate(pipelineAvg)
        count_result = self.db["bids"].aggregate(pipelineCount)

        avg = list(avg_result)
        count = list(count_result)


        avg_bid = avg[0]["average_bid"] if avg else 0
        total_bids = count[0]["total_bids"] if count else 0


        return {
            "avg": avg_bid,
            "count": total_bids,
            "bids": list(auctions)
        }

    ######### SUPPORT #########

    def add_user(self, player_id):
        if self.player_exists(player_id):
            raise HTTPException(400, f"uuid {player_id} already exists")

        res: InsertOneResult = self.db["users"].insert_one({"player_id": player_id})
        if res.inserted_id is None:
            raise HTTPException(400, "Auction_service was not able to add the player to its colleciton")

    def remove_user(self, player_id):
        if not self.player_exists(player_id):
            return

        res: DeleteResult = self.db["users"].delete_one({"player_id": player_id})
        if res.deleted_count == 0:
            raise HTTPException(400, "Auction_service was not able to remove the player to its colleciton")

    def auction_owner(self, auction_id: str):
        owner = self.db["auctions"].find_one({"auction_id": auction_id}, {"player_id": 1})
        if owner is None: raise HTTPException(status_code=400, detail="No auction found with specified criteria")
        return owner["player_id"]

    def bid_owner(self, bid_id: str):
        owner = self.db["bids"].find_one({"bid_id": bid_id}, {"bid_id": 1})
        if owner is None: raise HTTPException(status_code=400, detail="No bid found with specified criteria")
        return owner["bid_id"]

    def player_exists(self, player_id: str):
        if self.db["users"].find_one({"player_id": player_id}) is None:
            return False
        return True

    def gacha_remove_gacha(self, uid, gacha_name, access_token):
        header = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        data = {
            "uid": uid,
            "gacha_name": gacha_name
        }
        try:
            response = requests.delete("https://distro:9190/admin/remove/user/gacha", headers=header,
                                       json=data, verify=False, timeout=5)
            if not response.status_code == 200:
                raise HTTPException(status_code=400, detail="User's gacha cannot be found.")
        except (requests.RequestException, ConnectionError):
            raise HTTPException(status_code=400, detail="Internal Server Error")

    def gacha_add_gacha(self, player_uid, gacha_name, access_token):
        header = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        data = {
            "uid": player_uid,
            "gacha_name": gacha_name
        }
        try:
            response = requests.post("https://distro:9190/admin/add/user/gacha",
                                     headers=header, json=data, verify=False, timeout=5)
            if not response.status_code == 200:
                raise HTTPException(status_code=400, detail="Gacha cannot be added to its collection")
        except (requests.RequestException, ConnectionError):
            raise HTTPException(status_code=400, detail="Internal Server Error")

    def tux_freeze_tux(self, auction_id, user_id, tux_amount, access_token):
        header = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        data = {
            "user_id": user_id,
            "tux_amount": tux_amount
        }
        try:
            response = requests.post(f"https://tux_service:9290/admin/auctions/{auction_id}/freeze", headers=header,
                                     json=data, verify=False, timeout=5)
            if response.status_code == 402:
                raise HTTPException(status_code=402, detail="Insufficient tux balance to place the bid")
            if not response.status_code == 200:
                raise HTTPException(status_code=400, detail="Cannot retrieve tux from bidder account.")
        except (requests.RequestException, ConnectionError):
            raise HTTPException(status_code=400, detail="Internal Server Error")

    def tux_delete_auction(self, auction_id, access_token):
        header = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        try:
            response = requests.delete(f"https://tux_service:9290/admin/auctions/{auction_id}", headers=header, verify=False, timeout=5)
            if not response.status_code == 200:
                raise HTTPException(status_code=400, detail="Tux_service error from deletion of auction")
        except (requests.RequestException, ConnectionError):
            raise HTTPException(status_code=400, detail="Internal Server Error")


    def tux_settle_auction(self, auction_id, winner_id, auctioneer_id, access_token):
        header = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        data = {
            "winner_id": winner_id,
            "auctioneer_id": auctioneer_id
        }
        try:
            response = requests.post(f"https://tux_service:9290/admin/auctions/{auction_id}/settle-auction",
                                     headers=header, json=data, verify=False, timeout=5)
            if not response.status_code == 200:
                raise HTTPException(status_code=400, detail="Tux_service error from ending auction")
        except (requests.RequestException, ConnectionError):
            raise HTTPException(status_code=400, detail="Internal Server Error")


    def auth_get_admin_token(self) -> str:
        data = {
            'username': self.admin_account["username"],
            'password': self.admin_account["password"],
        }
        try:
            response = requests.post("https://authentication:9090/auth/token", data=data, verify=False, timeout=5)
            if not response.status_code == 200:
                raise HTTPException(status_code=400, detail="Tux_service error from ending auction")
        except (requests.RequestException, ConnectionError):
            raise HTTPException(status_code=400, detail="Internal Server Error")
        return response.json()["access_token"]

    def close_auction(self, auction, mock_check):
        if mock_check:
            return
        token_data = self.auth_get_admin_token()

        if auction["current_winning_player_id"] is not None:
            self.gacha_add_gacha(str(auction["current_winning_player_id"]), str(auction["gacha_name"]), token_data)
            self.tux_settle_auction(str(auction["auction_id"]), str(auction["current_winning_player_id"]),
                                  str(auction["player_id"]), token_data)
        else:
            self.gacha_add_gacha(str(auction["player_id"]), str(auction["gacha_name"]), token_data)
