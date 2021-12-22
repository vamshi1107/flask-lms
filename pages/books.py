from flask import Blueprint
from flask import *
from flask.json import JSONDecoder, JSONEncoder, jsonify
import requests
from flask_cors import CORS
import pymongo
import datetime
import time
from vars import uri


books = Blueprint("books_blueprint", __name__)

client = pymongo.MongoClient(uri)
db = client["lms"]


@books.route("/searchbooks", methods=["GET"])
def searchBooks():
    url = request.args.get("url", "")
    return requests.get(url).content


@books.route("/addbooks", methods=["POST"])
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


@books.route("/getbooks", methods=["GET"])
def getBooks():
    col = db["books"]
    v = []
    for i in col.find({}):
        del i["_id"]
        v.append(i)
    return jsonify({"data": v})


@books.route("/removebook", methods=["GET"])
def removeBook():
    bid = request.args.get("bid", "")
    col = db["books"]
    x = col.delete_one({"bid": bid})
    return str(x.deleted_count)


@books.route("/getbookById", methods=["GET"])
def getBookById():
    bid = request.args.get("bid", "")
    col = db["books"]
    v = []
    for i in col.find({"bid": bid}):
        del i["_id"]
        v.append(i)
    return jsonify({"data": v})
