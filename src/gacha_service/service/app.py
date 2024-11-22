#from flask import Flask, request, make_response, jsonify
from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import JSONResponse
#import random, time, os, threading, requests
#import json
from db import database

#DB initialization 
#app = Flask(__name__)
#db = database("distros.txt")

#TODO: check for admin and user (?)
#This function return all the gachas in the system 
#@app.route('/all')
#def all():
#   return make_response(db.get_all_distros(),200) 

#TODO: check user 
#@app.route('/roll')
#def roll():
#   return make_response(NULL,200) 
#
##TODO: check user 
#@app.route('/modify')
#def modify():
#   return make_response(NULL,200) 

#testing porpuses
#@app.route('/add')
#def add():
#    a = request.args.get('a', type=float)
#    b = request.args.get('b', type=float)
#    if a and b:
#        return make_response(jsonify(s=a+b), 200) 
#    else:
#        return make_response('Invalid input\n', 400) 
#
#if __name__ == '__main__':
#    app.run(debug=True)


# Inizializzazione DB
app = FastAPI()
db = database("distros.txt")

# Funzione per restituire tutti i gachas nel sistema
@app.get("/all", status_code=200)
def get_all():
    return JSONResponse(content=db.get_all_distros())

# Funzione di aggiunta per test
@app.get("/add", status_code=200)
def add(a: int, b: int):
    if a is not int and b is not int:
        return {"s": a + b}
    else:
        raise HTTPException(status_code=400, detail="Invalid input")