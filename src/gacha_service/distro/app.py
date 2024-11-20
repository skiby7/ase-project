from flask import Flask, request, make_response, jsonify
import random, time, os, threading, requests
from pymongo import MongoClient
import json

def db_inizialization():
    db.create_collection("distros")
    distros = db["distros"]
    distros_list = []
    with open(distrofile, "r") as file:
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

#TODO user on db

#DB initialization 
distrofile = "distros.txt"
client = MongoClient("db", 27017, maxPoolSize=50)
db = client["mydatabase"]
app = Flask(__name__)
if "distros" in db.list_collection_names():
    print( "DISTRO PRESENTE ")
else: 
    db_inizialization()
distros = db["distros"]

#TODO: check for admin and user (?)
#This function return all the gachas in the system 
@app.route('/all')
def all():
   all_distros = list(distros.find())
   all = [{"name": distros["name"], "rarity": distros["rarity"]} for distros in all_distros]
   json_array = json.dumps(all, default=str, indent=4)
   return make_response(json_array,200) 

#testing porpuses
@app.route('/add')
def add():
    a = request.args.get('a', type=float)
    b = request.args.get('b', type=float)
    if a and b:
        return make_response(jsonify(s=a+b), 200) 
    else:
        return make_response('Invalid input\n', 400) 

if __name__ == '__main__':
    app.run(debug=True)