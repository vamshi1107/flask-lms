from flask import Blueprint
from flask import *
from flask.json import JSONDecoder, JSONEncoder, jsonify
import requests
from flask_cors import CORS
import pymongo
import datetime
import time
from vars import uri

members = Blueprint("members_blueprint", __name__)

client = pymongo.MongoClient(uri)
db = client["lms"]


def membercount(q):
    col = db["members"]
    v = [1 for i in col.find(q)]
    return sum(v)


@members.route("/addmembers", methods=["POST"])
def addMember():
    num = 1000
    if request.method == "POST":
        req = dict(request.json)
        s = sum([1 for i in ["ssn", "name", "phone"] if i in req.keys()])
        if s == 3:
            col = db["members"]
            mid = num + membercount({})
            req["mid"] = "M" + str(mid)
            x = col.insert_one(req)
            return {"status": str(x.acknowledged), "mid": mid}
        else:
            return "missing parameters".upper()
    else:
        return "method not allowed".upper()


@members.route("/updatemember", methods=["POST"])
def updateMember():
    if request.method == "POST":
        req = dict(request.json)
        s = sum([1 for i in ["ssn", "name", "phone"] if i in req.keys()])
        if s == 3:
            col = db["members"]
            x = col.update_one({"ssn": req.ssn}, {req})
            return str(x.acknowledged)
        else:
            return "missing parameters".upper()
    else:
        return "method not allowed".upper()


@members.route("/getmembers", methods=["GET"])
def getMembers():
    col = db["members"]
    v = []
    for i in col.find({}):
        del i["_id"]
        v.append(i)
    return jsonify({"data": v})


@members.route("/getmemberById", methods=["GET"])
def getMemberById():
    mid = request.args.get("mid", "")
    col = db["members"]
    v = []
    for i in col.find({"mid": mid.upper()}):
        del i["_id"]
        v.append(i)
    return jsonify({"data": v})


@members.route("/getMemberbyidwithdue", methods=["GET"])
def getBookByIdWithDue():
    bid = request.args.get("bid", "")
    col = db["books"]
    v = []
    for i in col.find({"bid": bid}):
        del i["_id"]
        i["due"] = getDue(i["bid"])
        v.append(i)
    return jsonify({"data": v})


@members.route("/removemember", methods=["GET"])
def removeMember():
    mid = request.args.get("mid", "")
    col = db["members"]
    x = col.delete_one({"mid": mid})
    return str(x.deleted_count)
