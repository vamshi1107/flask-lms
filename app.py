from flask import *
from flask.json import JSONDecoder, JSONEncoder, jsonify
import requests
from flask_cors import CORS
import pymongo
import datetime
import time


client = pymongo.MongoClient(
    "mongodb://vamshi:qwertyuiop@cluster0-shard-00-00.uayjw.mongodb.net:27017,cluster0-shard-00-01.uayjw.mongodb.net:27017,cluster0-shard-00-02.uayjw.mongodb.net:27017/lms?ssl=true&replicaSet=atlas-v0a7u6-shard-0&authSource=admin&retryWrites=true&w=majority"
)
db = client["lms"]

app = Flask(__name__)
CORS(app)


@app.route("/")
def index():
    return "<h1>Hi</h1>"


@app.route("/addbooks", methods=["POST"])
def addBook():
    if request.method == "POST":
        req = dict(request.json)
        s = sum([1 for i in ["name", "bid", "author", "quantity"] if i in req.keys()])
        if s == 4:
            col = db["books"]
            x = col.insert_one(req)
            return str(x.acknowledged)
        else:
            return "missing parameters".upper()
    else:
        return "method not allowed".upper()


@app.route("/getbooks", methods=["GET"])
def getBooks():
    col = db["books"]
    v = []
    for i in col.find({}):
        del i["_id"]
        v.append(i)
    return jsonify({"data": v})


@app.route("/removebook", methods=["GET"])
def removeBook():
    bid = request.args.get("bid", "")
    col = db["books"]
    x = col.delete_one({"bid": bid})
    return str(x.deleted_count)


@app.route("/addmembers", methods=["POST"])
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


@app.route("/updatemember", methods=["POST"])
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


@app.route("/getmembers", methods=["GET"])
def getMembers():
    col = db["members"]
    v = []
    for i in col.find({}):
        del i["_id"]
        v.append(i)
    return jsonify({"data": v})


@app.route("/getmemberById", methods=["GET"])
def getMemberById():
    mid = request.args.get("mid", "")
    col = db["members"]
    v = []
    for i in col.find({"mid": mid.upper()}):
        del i["_id"]
        v.append(i)
    return jsonify({"data": v})


@app.route("/getbookById", methods=["GET"])
def getBookById():
    bid = request.args.get("bid", "")
    col = db["books"]
    v = []
    for i in col.find({"bid": bid}):
        del i["_id"]
        v.append(i)
    return jsonify({"data": v})


@app.route("/issuebook", methods=["POST"])
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


@app.route("/getbookissue", methods=["GET"])
def getbookissue():
    mid = request.args.get("bid", "")
    col = db["issues"]
    v = []
    for i in col.find({"bid": mid.upper()}):
        del i["_id"]
        v.append(i)
    return jsonify({"data": v})


def current_time():
    return round(time.time() * 1000)


@app.route("/getdue", methods=["GET"])
def getDue():
    mid = request.args.get("mid", "")
    col = db["issues"]
    d = 0
    m = current_time()
    for i in col.find({"mid": mid.upper()}):
        c = int((m - i["time"]) / (1000 * 60 * 60 * 24))
        d += c if c > 0 else 1
    return {"due": d * 5}


@app.route("/getMemberbyidwithdue", methods=["GET"])
def getBookByIdWithDue():
    bid = request.args.get("bid", "")
    col = db["books"]
    v = []
    for i in col.find({"bid": bid}):
        del i["_id"]
        i["due"] = getDue(i["bid"])
        v.append(i)
    return jsonify({"data": v})


@app.route("/getmemberissue", methods=["GET"])
def getmemberissue():
    mid = request.args.get("mid", "")
    col = db["issues"]
    v = []
    for i in col.find({"mid": mid.upper()}):
        del i["_id"]
        b = book(i["bid"])
        del b["_id"]
        v.append({**i, **b})
    return {"data": v}


def membercount(q):
    col = db["members"]
    v = [1 for i in col.find(q)]
    return sum(v)


def book(bid):
    return db["books"].find_one({"bid": bid})


@app.route("/returnbook", methods=["POST"])
def returnBook():
    req = dict(request.json)
    col = db["issues"]
    q = {"bid": req["bid"], "mid": req["mid"], "date": req["date"], "time": req["time"]}
    x = col.delete_one(q)
    n = db["books"].find_one({"bid": req["bid"]})["quantity"]
    bres = db["books"].update_one(
        {"bid": req["bid"]}, {"$set": {"quantity": int(n) + 1}}
    )
    return jsonify({"status": x.deleted_count, "n": bres.modified_count})


@app.route("/removemember", methods=["GET"])
def removeMember():
    mid = request.args.get("mid", "")
    col = db["members"]
    x = col.delete_one({"mid": mid})
    return str(x.deleted_count)


@app.route("/searchbooks", methods=["GET"])
def searchBooks():
    url = request.args.get("url", "")
    return requests.get(url).content


if __name__ == "__main__":
    app.run()
