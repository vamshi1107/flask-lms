from flask import Blueprint
from flask import *
from flask.json import JSONDecoder, JSONEncoder, jsonify
import requests
from flask_cors import CORS
import pymongo
import datetime
import time
from vars import uri


issues = Blueprint("issues_blueprint", __name__)

client = pymongo.MongoClient(uri)
db = client["lms"]


def membercount(q):
    col = db["members"]
    v = [1 for i in col.find(q)]
    return sum(v)


def member(mid):
    return db["members"].find_one({"mid": mid})


def current_time():
    return round(time.time() * 1000)


def book(bid):
    return db["books"].find_one({"bid": bid})


@issues.route("/getallissues", methods=["GET"])
def getallissues():
    col = db["issues"]
    v = []
    for i in col.find({}):
        del i["_id"]
        v.append({**i})
    return {"data": v}


@issues.route("/getmemberissue", methods=["GET"])
def getmemberissue():
    mid = request.args.get("mid", "")
    col = db["issues"]
    v = []
    for i in col.find({"mid": mid.upper(), "paid": "false"}):
        del i["_id"]
        b = book(i["bid"])
        del b["_id"]
        v.append({**i, **b})
    return {"data": v}


@issues.route("/issuebook", methods=["POST"])
def issueBook():
    num = 1000
    if request.method == "POST":
        req = dict(request.json)
        s = sum([1 for i in ["mid", "bid", "time", "date"] if i in req.keys()])
        if s == 4:
            col = db["issues"]
            q = db["books"].find_one({"bid": req["bid"]})["quantity"]
            if int(q) > 0:
                x = col.insert_one(req)
                bres = db["books"].update_one(
                    {"bid": req["bid"]}, {"$set": {"quantity": int(q) - 1}}
                )
                return {"status": str(x.acknowledged), "up": bres.modified_count}
            else:
                {"status": "false", "msg": "not enough"}
        else:
            return {"status": "false", "msg": "missing parameters".upper()}
    else:
        return {"status": "false", "msg": "method not allowed".upper()}


@issues.route("/getbookissue", methods=["GET"])
def getbookissue():
    mid = request.args.get("bid", "")
    col = db["issues"]
    v = []
    for i in col.find({"bid": mid.upper()}):
        del i["_id"]
        v.append(i)
    return jsonify({"data": v})


@issues.route("/issues", methods=["GET"])
def missues():
    col = db["issues"]
    r = col.aggregate([{"$group": {"_id": "$bid", "count": {"$sum": 1}}}])
    v = []
    for i in r:
        b = book(i["_id"])
        del i["_id"]
        del b["_id"]
        k = {**i, **b}
        v.append(k)
    return {"data": v}


@issues.route("/amount", methods=["GET"])
def amount():
    col = db["returns"]
    r = col.aggregate(
        [
            {
                "$group": {
                    "_id": "$mid",
                    "totalAmount": {"$sum": {"$sum": ["$amount"]}},
                }
            },
        ]
    )
    v = []
    for i in r:
        k = member(i["_id"])
        del k["_id"]
        v.append({**i, **k})
    return {"data": v}


@issues.route("/getdue", methods=["GET"])
def getDue():
    mid = request.args.get("mid", "")
    col = db["issues"]
    d = 0
    m = current_time()
    for i in col.find({"mid": mid.upper(), "paid": "false"}):
        c = int((m - i["time"]) / (1000 * 60 * 60 * 24))
        d += c if c > 0 else 1
    return {"due": d * 5}
