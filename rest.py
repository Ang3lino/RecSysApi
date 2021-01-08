from flask import Flask, render_template, request, jsonify
from flaskext.mysql import MySQL

import pymysql  # mysql error handling
import itertools
import json

from db_helper import DbHelper
from rec_utils import *


app = Flask(__name__)
app.config.from_pyfile("config.py")

mysql = MySQL()
mysql.init_app(app)

conn = mysql.connect()
cursor = conn.cursor()

db = DbHelper(conn, cursor)
algo, sims, trainset, testset = get_rec_sys_resources()


@app.route("/ping", methods=['GET', 'POST'])
def ping():
    return "pong!"

@app.route("/register", methods=["POST"])
def register():
    socio = request.json
    return db.register(socio)

@app.route("/login", methods=["POST"])
def login():
    email, passwd = request.json['email'], request.json['passwd']
    return db.login(email, passwd)

@app.route("/get_recs", methods=["POST"])
def get_recs():
    uid = request.json['uid']
    res = {'was_possible': False}
    try:
        iid_recs = get_top_item_based(algo, uid, trainset, sims)  # if raw_id not in trainset it raises error
        res['products'] = db.get_products_info(iid_recs)
        res['was_possible'] = True
    except ValueError as e:
        pass
    return res


if __name__ == "__main__":
    app.run(debug=True, port=5001)
