from flask import Blueprint
from flask import *
from flask.json import JSONDecoder, JSONEncoder, jsonify
import requests
from flask_cors import CORS
import pymongo
import datetime
import time
from vars import uri


returns = Blueprint("returns_blueprint", __name__)


client = pymongo.MongoClient(uri)
db = client["lms"]


@returns.route("/getallreturns", methods=["GET"])
def getallreturns():
    col = db["returns"]
    v = []
    for i in col.find({}):
        del i["_id"]
        v.append({**i})
    return {"data": v}


@returns.route("/returnbook", methods=["POST"])
def returnBook():
    req = dict(request.json)
    col = db["issues"]
    ret = db["returns"]
    q = {"bid": req["bid"], "mid": req["mid"], "date": req["date"], "time": req["time"]}
    x = col.update_one(q, {"$set": {"paid": "true"}})
    re = ret.insert_one({**q, **{"rtime": current_time(), "amount": req["amount"]}})
    n = db["books"].find_one({"bid": req["bid"]})["quantity"]
    bres = db["books"].update_one(
        {"bid": req["bid"]}, {"$set": {"quantity": int(n) + 1}}
    )
    return jsonify({"status": x.modified_count, "n": bres.modified_count})


def current_time():
    return round(time.time() * 1000)
