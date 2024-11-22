from pymongo import MongoClient
import json

#TODO user on db

class database:
    def __init__(self,distrofile):
        self.distrofile = distrofile
        self.client = MongoClient("db", 27017, maxPoolSize=50)
        self.db = self.client["mydatabase"]
        if "distros" in self.db.list_collection_names():
            print("initialize db")
        else: 
            self.db_inizialization()

    def db_inizialization(self):
        self.db.create_collection("distros")
        self.db.create_collection("users")
        distros = self.db["distros"]
        distros_list = []
        with open(self.distrofile, "r") as file:
            lines = file.readlines()
            for line in lines:
                line = line.strip()
                if ',' in line:
                    name, rarity = line.split(",", 1)
                    distros_list.append({
                        "name": name.strip(),
                        "rarity": int(rarity.strip())
                    })
        distros.insert_many(distros_list)

    def get_all_distros(self):
        distros = self.db["distros"]
        all_distros = list(distros.find())
        all = [{"name": distros["name"], "rarity": distros["rarity"]} for distros in all_distros]
        return json.dumps(all, default=str, indent=4)