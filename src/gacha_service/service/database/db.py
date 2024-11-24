from pymongo import MongoClient
import json
import uuid
import random


#TODO user on db
class database:
    def __init__(self,distrofile):
        self.distrofile = distrofile
        self.client = MongoClient("db", 27017, maxPoolSize=50)
        self.db = self.client["mydatabase"]
        if "gachas" in self.db.list_collection_names():
            print(" \n\n SONO VIVO  \n\n")
        else: 
            self.db_inizialization()
        if "users" in self.db.list_collection_names():
            print(" \n\n falso  \n\n")
        else: 
            self.db.create_collection("users")

    # convert to json distro.txt
    def db_inizialization(self):
        self.db.create_collection("gachas")
        gachas = self.db["gachas"]

        with open(self.distrofile, "r") as file:
            data = json.load(file)

        for gacha in data:
            gacha["id"] = str(uuid.uuid4())

        gachas.insert_many(data)

    def get_all_gachas_name(self):
        gachas = self.db["gachas"]
        all_distros = list(gachas.find())
        all = [{"name": gachas["name"]} for gachas in all_distros]
        return all

    def add_user_gacha(self,user_id,gacha_name):
        gachas = self.db["gachas"]
        users = self.db["users"]
        gacha = gachas.find_one({"name": gacha_name})

        if not gacha:
            raise ValueError(f"Gacha with name '{gacha_name}' not found.")

        gacha_id = gacha["id"]
        user = users.find_one({"id": user_id})

        if not user:
            print("\n\n USER NON PRESENTE \n\n")
            user = {
                "id": user_id,
                "gacha_list": [
                                {"gacha_id": gacha_id, "value" : 1}
                ]
            }
            users.insert_one(user)
        else : 
            existing_gacha = next((item for item in user["gacha_list"] if item["gacha_id"] == gacha_id), None)
    
            if existing_gacha:
                users.update_one(
                    {"id": user_id, "gacha_list.gacha_id": gacha_id},
                    {"$inc": {"gacha_list.$.value": 1}}
                )
            else:
                users.update_one(
                    {"id": user_id},
                    {"$push": {"gacha_list": {"gacha_id": gacha_id, "value": 1}}}
                )

    def get_user_gacha(self,user_id):
        gachas = self.db["gachas"]
        users = self.db["users"]
        user = users.find_one({"id": user_id})
        if not user: 
            return {} #TODO: check this
        user_gachas = list(user["gacha_list"])
        return user_gachas 

    def get_random_gacha(self):
        gachas = self.db["gachas"]
        list_gachas = list(gachas.find())
        n_gachas = len(list_gachas) 
        rand = random.randint(1, n_gachas);
        gacha_name = list_gachas[rand]["name"]
        self.add_user_gacha(1,gacha_name) #TODO: uuid
        return gacha_name







