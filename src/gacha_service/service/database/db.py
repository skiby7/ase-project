from pymongo import MongoClient
import json
import uuid
import random
import base64

def convert_image(image):
        with open("utils/images/" + image + ".png", "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

#TODO user on db
class database:
    def __init__(self,distrofile : str):
        self.distrofile = distrofile
        self.client = MongoClient("db", 27017, maxPoolSize=50)
        self.db = self.client["mydatabase"]
        if "gachas" not in self.db.list_collection_names():
            self.db_inizialization()
        if "users" not in self.db.list_collection_names():
            self.db.create_collection("users")

    def db_inizialization(self):
        self.db.create_collection("gachas")
        gachas = self.db["gachas"]

        with open(self.distrofile, "r") as file:
            data = json.load(file)

        for gacha in data:
            gacha["id"] = str(uuid.uuid4())
            gacha["image"] = convert_image(gacha["name"])

        gachas.insert_many(data)

    def get_all_gachas_user(self):
        gachas = self.db["gachas"]
        all_distros = list(gachas.find())
        res = [{"name": gachas["name"],"image" : gachas["image"]} for gachas in all_distros]
        return res
    
    def get_all_gachas_admin(self):
        gachas = self.db["gachas"]
        all_gachas = list(gachas.find())
        res = [{"id": gachas["id"], "name": gachas["name"], "rarity" : gachas["rarity"], "image" : gachas["image"]} for gachas in all_gachas]
        return res

    def get_specific_gacha(self,gacha_name : str):
        gachas = self.db["gachas"]
        gacha = gachas.find_one({"name": gacha_name})
        if not gacha: 
            return
        res = {"name": gacha["name"], "image": gacha["image"]}
        return res

    def add_user_gacha(self,id : str,gacha_name : str):
        gachas = self.db["gachas"]
        users = self.db["users"]
        gacha = gachas.find_one({"name": gacha_name})

        if not gacha:
            return None

        gacha_id = gacha["id"]
        user = users.find_one({"id": id})

        if not user:
            return None
            #user = {
            #    "id": id,
            #    "gacha_list": [
            #                    {"gacha_id": gacha_id, "value" : 1}
            #    ]
            #}
            #users.insert_one(user)
        else : 
            existing_gacha = next((item for item in user["gacha_list"] if item["gacha_id"] == gacha_id), None)
    
            if existing_gacha:
                users.update_one(
                    {"id": id, "gacha_list.gacha_id": gacha_id},
                    {"$inc": {"gacha_list.$.value": 1}}
                )
            else:
                users.update_one(
                    {"id": id},
                    {"$push": {"gacha_list": {"gacha_id": gacha_id, "value": 1}}}
                )

    def remove_user_gacha(self,id : str,gacha_name : str):
        gachas = self.db["gachas"]
        users = self.db["users"]
        gacha = gachas.find_one({"name": gacha_name})

        if not gacha:
            return None

        gacha_id = gacha["id"]
        user = users.find_one({"id": id})

        existing_gacha = next(
                (item for item in user["gacha_list"] if item["gacha_id"] == gacha_id), None
        )

        if existing_gacha:
            if existing_gacha["value"] > 1:
                # value--
                users.update_one(
                    {"id": id, "gacha_list.gacha_id": gacha_id},
                    {"$inc": {"gacha_list.$.value": -1}}
                )
                print(f"Valore del gacha {gacha_id} diminuito di 1.")
            else:
                # delete if value = 0
                users.update_one(
                    {"id": id},
                    {"$pull": {"gacha_list": {"gacha_id": gacha_id}}}
                )
                print(f"Gacha {gacha_id} rimosso dalla lista.")
        else:
            return None

    def get_user_gacha(self,user_id : str):
        gachas = self.db["gachas"]
        users = self.db["users"]
        user = users.find_one({"id": user_id})
        if not user: 
            return None 
        user_gachas = list(user["gacha_list"])
        res = []
        for gacha_u in user_gachas:
            gacha = gachas.find_one({"id": gacha_u["gacha_id"]})
            res.append({"value" : gacha_u["value"], "name" : gacha["name"], "image" : gacha["image"]})
        return res 

    def get_roll_gacha(self):
        gachas = self.db["gachas"]
        list_gachas = list(gachas.find())
        n_gachas = len(list_gachas) 
        rand = random.randint(0, n_gachas-1);
        gacha_name = list_gachas[rand]["name"]
        self.add_user_gacha(1,gacha_name) #TODO: uuid
        return gacha_name

    def modify_gacha(self,name : str,rarity : str,image : str):
        gachas = self.db["gachas"]
        gacha = gachas.find_one({"name": name})
        if not gacha:
            return None
        gacha.rarity = rarity
        gacha.image = image
        return gacha

    def add_gacha(self,name : str,rarity : str,image: str):
        gachas = self.db["gachas"]
        gacha = gachas.find_one({"name": name})
        if gacha:
            return None
        gachas.insert_one({"id": str(uuid.uuid4()),"name": name,"rarity": rarity,"image": image})
        return {"id": str(uuid.uuid4()),"name": name,"rarity": rarity,"image": image}
        
    def remove_gacha(self,name: str):
        gachas = self.db["gachas"]
        gacha = gachas.find_one({"name": name})
        if not gacha:
            return None
        gachas.delete_one({"name": name})
        return {"name" : name}
    
    def add_user(self,id):
        users = self.db["users"] 
        if users.find_one({"id": id}):
            return None
        user = {
               "id": id,
               "gacha_list": []
           }
        users.insert_one(user)
        return id

    def remove_user(self,id):
        users = self.db["users"] 
        if not users.find_one({"id": id}):
            return None
        users.delete_one({"id": id})
        return id