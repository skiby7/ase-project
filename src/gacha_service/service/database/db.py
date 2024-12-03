from pymongo import MongoClient
import json
import uuid
import random
import base64

def convert_image(image):
        with open("utils/images/" + image + ".png", "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

class database:
    def __init__(self,distrofile : str):
        self.distrofile = distrofile
        username = "root"
        host = "gacha_db"
        port = "27017"
        db = "admin"
        database = "mydatabase"
        #tsl_certificate_file = "/run/secrets/cert"
        with open('/run/secrets/pw', 'r') as file:
            password = file.read().strip()
        uri = f"mongodb://{username}:{password}@{host}:{port}/{database}?authSource={db}&tls=true&tlsAllowInvalidCertificates=true"
        self.client = MongoClient(uri)
        #self.client = MongoClient("db", 27017, maxPoolSize=50)
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

    def get_all_gachas_admin(self,mock_id):
        gachas = self.db["gachas"]
        all_gachas = list(gachas.find())
        if mock_id:
            res = [{"name": gachas["name"], "rarity" : gachas["rarity"], "image" : gachas["image"]} for gachas in all_gachas]
        else:
            res = [{"id": gachas["id"], "name": gachas["name"], "rarity" : gachas["rarity"], "image" : gachas["image"]} for gachas in all_gachas]
        return res

    def get_specific_gacha(self, gacha_name: str, mock_id):
        gachas = self.db["gachas"]
        gacha = gachas.find_one({"name": gacha_name})
        if not gacha:
            return
        if mock_id:
            return {"name": gacha["name"], "rarity": gacha["rarity"], "image": gacha["image"]}
        else:
            return {"id": gacha["id"], "name": gacha["name"], "rarity": gacha["rarity"], "image": gacha["image"]}

    def add_user_gacha(self, id: str, gacha_name: str):
        id = str(id)
        gachas = self.db["gachas"]
        users = self.db["users"]
        gacha = gachas.find_one({"name": gacha_name})

        if not gacha:
            return 1

        gacha_id = gacha["id"]
        user = users.find_one({"id": id})

        if not user:
            return None
        else:
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

        return {"name": gacha_name, "image": gacha["image"]}

    def remove_user_gacha(self, id: str, gacha_name: str):
        id = str(id)
        gachas = self.db["gachas"]
        users = self.db["users"]
        gacha = gachas.find_one({"name": gacha_name})

        if not gacha:
            return None

        gacha_id = gacha["id"]
        user = users.find_one({"id": id})

        if not user:
            return 2

        existing_gacha = next(
                (item for item in user["gacha_list"] if item["gacha_id"] == gacha_id), None
        )

        if existing_gacha:
            if existing_gacha["value"] > 1:
                users.update_one(
                    {"id": id, "gacha_list.gacha_id": gacha_id},
                    {"$inc": {"gacha_list.$.value": -1}}
                )
            else:
                users.update_one(
                    {"id": id},
                    {"$pull": {"gacha_list": {"gacha_id": gacha_id}}}
                )
            return {"name": gacha_name}
        else:
            return 1

    def get_user_gacha(self, id: str):
        id = str(id)
        gachas = self.db["gachas"]
        users = self.db["users"]
        user = users.find_one({"id": id})
        if not user:
            return 1
        user_gachas = list(user["gacha_list"])
        res = []
        for gacha_u in user_gachas:
            gacha = gachas.find_one({"id": gacha_u["gacha_id"]})
            res.append({"value" : gacha_u["value"], "name" : gacha["name"], "image" : gacha["image"]})
        return res

    def get_user_collection_gacha(self, id: str, name: str):
        id = str(id)
        gachas = self.db["gachas"]
        users = self.db["users"]
        user = users.find_one({"id": id})
        gacha = gachas.find_one({"name": name})
 
        if not user:
            return 1

        user_gachas = list(user["gacha_list"])

        for gacha_u in user_gachas:
            gacha = gachas.find_one({"id": gacha_u["gacha_id"]})
            if gacha["name"] == name:
                return ({"value" : gacha_u["value"], "name" : gacha["name"], "image" : gacha["image"], "rarity" : gacha["rarity"]})
        
        return 2

    def get_roll_gacha(self, id: str, mock):
        id = str(id)
        gachas = self.db["gachas"]
        gacha_list = list(gachas.find())

        weights = [6 - int(gacha["rarity"]) for gacha in gacha_list]
        rand = random.choices(gacha_list, weights=weights, k=1)[0]

        if mock:
            res = self.add_user_gacha(id,"Ubuntu")
        else:
            res = self.add_user_gacha(id,rand["name"])
        return res

    def modify_gacha(self, name: str, rarity: str, image: str):
        gachas = self.db["gachas"]
        gacha = gachas.find_one({"name": name})

        if not gacha:
            return None

        gachas.update_one(
            {"name": name},
            {"$set": {"rarity": rarity, "image": image}}
        )

        return {"name": name, "rarity": rarity, "image": image}

    def add_gacha(self, name: str, rarity: str, image: str,mock_id):
        gachas = self.db["gachas"]
        gacha = gachas.find_one({"name": name})
        if gacha:
            return None
        id = str(uuid.uuid4())
        gachas.insert_one({"id": id,"name": name,"rarity": rarity,"image": image})
        if mock_id:
            return {"name": name,"rarity": rarity,"image": image}
        else:
            return {"id": id,"name": name,"rarity": rarity,"image": image}

    def remove_gacha(self, name: str):
        gachas = self.db["gachas"]
        gacha = gachas.find_one({"name": name})
        if not gacha:
            return None

        users = self.db["users"]
        user_list = list(users.find())
        for user in user_list:
            self.remove_user_gacha(user["id"], name)

        gachas.delete_one({"name": name})
        return {"name" : name}

    def add_user(self, id: str):
        id = str(id)
        users = self.db["users"]
        if users.find_one({"id": id}):
            return None
        user = {
               "id": id,
               "gacha_list": []
           }
        users.insert_one(user)
        return {"uid": id}

    def remove_user(self, id: str):
        id = str(id)
        users = self.db["users"]
        if not users.find_one({"id": str(id)}):
            return None
        users.delete_one({"id": id})
        return {"uid": id}
