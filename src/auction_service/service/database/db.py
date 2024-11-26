from pymongo import MongoClient
import json
import uuid
import random

#auctions and bids schemas
#both init together


#TODO user on db
class database:
    def __init__(self,auctionsFile):
        self.auctionsFile = auctionsFile
        self.bidsFile = bidsFile
        self.client = MongoClient("db", 27017, maxPoolSize=50)
        self.db = self.client["mydatabase"]
        if "auctions" in self.db.list_collection_names():
            print(" \n\n DB ACTIVE  \n\n")
        else: 
            self.db_inizialization()
        

    # convert to json distro.txt
    def db_init_supp(collection,file):
        with open(file, "r") as file:
            data = json.load(file)
            gachas.insert_many(data)

    def db_inizialization(self):
        self.db.create_collection("auctions")
        auctions = self.db["auctions"]

        self.db.create_collection("bids")
        bids = self.db["bids"]

        db_init_supp(auctions,self.auctionsFile)
        db_init_supp(bids,self.bidsFile)


    def get_user_auction_history(uuid):
        return list( self.db["bids"].find({"uuid":uuid}) )
    
    def create_auction(user_id,gacha_id,starting_price,end_time):
        #control if gacha is already in bid
        if(!self.gacha_available(gacha_id)){
            return 1
        }
        while(True){
            id=uuid.uuid4()
            if(!self.db["auctions"].find_one({"auction_id":id}))break
        }
        auction={
            "auction_id":id,
            "user_id":user,"gacha_id":gacha_id,
            "starting_price":starting_price,
            "current_winning_player_id":None,
            "current_winning_bid":0
            "end_time":end_time
            "active":True
            }

        self.db["auctions"].insert_one(auction)
        return 0

    def bid(auction_id,player_id,bid):
        auction = self.db["auctions"].find_one({"auction_id":id,"active":True})
        if auction is None:return -1
        if player_id == auction["player_id"]: return -1
        if bid <= auction["current_winning_bid"]:return -1
        auction["current_winning_player_id"]=player_id
        auction["current_winning_bid"]=bid

        self.db["bids"].insert_one({"player_id":player_id,"auction_id":auction_id,"bid":bid})

    #SUPPORT
    #every gacha is unique so controlling if it has a current auction on it is sufficient
    def gacha_available(gacha_id):
        return self.db["auctions"].find_one[{"gacha_id":gacha_id,"active":True}]?False:True

    
        






