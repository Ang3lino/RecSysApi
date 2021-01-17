from flask import Flask, render_template, request, jsonify
from flaskext.mysql import MySQL

import pymysql  # mysql error handling
import itertools
import json
import pandas as pd
import numpy as np

from db_helper import DbHelper
from rec_utils import *

#para generar pdf
from flask import render_template
from flask import make_response
import pdfkit
 

app = Flask(__name__)
    
app.config.from_pyfile("config.py")

mysql = MySQL()

mysql.init_app(app)

conn = mysql.connect()
cursor = conn.cursor()

db = DbHelper(conn, cursor)
algo, sims, trainset, testset = get_rec_sys_resources()
df = pd.read_csv('./model/software_reviews_no_outliers.csv')
good_ratings_df = df[df['overall'] >= 4]


def get_top_global(good_ratings_df, n=7):
    # select those good ratings. group them by iid, sum their values and sort them desc
    top_global_grp = good_ratings_df.groupby('asin')['overall'].sum().sort_values(ascending=False)
    total = len(top_global_grp)
    iids = np.random.choice(top_global_grp.index.values[:total // 10], n)  # from the 10% most rated, pick 10
    return db.get_products_info(iids)

@app.route("/ping", methods=['GET', 'POST'])
def ping():
    return "pong!"

@app.route("/register", methods=["POST"])
def register():
    """Registra a un usuario. Los atributos del json son:
        ('apPaterno', 'apMaterno', 'nombre', 'edad', 'genero', 'email', 'passwd')
    
    Returns:
        {'email_used': bool, 'success': bool[, socio: dict]}
    """
    socio = request.json
    return db.register(socio)

@app.route("/login", methods=["POST"])
def login():
    """Determina si las credenciales estan en la base, si lo estan se regresa el uid.

    Returns:
        {'ok': bool[, 'usuario': dict]}: 
    """
    email, passwd = request.json['email'], request.json['passwd']
    return db.login(email, passwd)

@app.route("/insert_hist", methods=["POST"])
def insert_hist():
    """Inserta las compras realizadas al historial
        {idSocio: str, idProductos: list<str>, cantidades: list<int>}
    Returns:
        {success: bool}: True en caso de poder escribir en la base.
    """
    return db.insert_hist(request.json)

@app.route("/get_purchases", methods=["GET"])
def get_purchases():
    """Regresa los valores de historial dado el uid.

    Returns:
        dict{idSocio: list, idProducto: list, fecha_hora: list, cantidad: list}
    """
    uid = request.json['idSocio']
    return db.get_purchases(uid) 

@app.route("/insert_pendiente", methods=["POST"])
def insert_pendiente():
    """Inserta un pendiente de compra de un usuario
        {idSocio: str, idProductos: str}
    Returns:
        {success: bool}: True en caso de poder escribir en la base.
    """
    return db.insert_pendiente(request.json)
    
@app.route("/get_pendientes", methods=["GET", "POST"])
def get_pendientes():
    """Inserta un pendiente de compra de un usuario
        {idSocio: str, idProductos: str}
    Returns:
        {success: bool}: True en caso de poder escribir en la base.
    """
    uid = request.json['idSocio']
    return db.get_pendientes(uid)

@app.route("/get_products_info", methods=["GET"])
def get_products_info():
    """Dado {idProducto: list} regresamos los productos cuyo id en estos valores.

    Returns:
        {productsInfo: list<producto>}
    """
    iids = request.json["idProducto"]
    return db.get_products_info(iids)

@app.route("/get_product_info", methods=["GET"])
def get_product_info():
    iid = request.json["idProducto"]  # item id 
    return db.get_product_info(iid)

@app.route("/insert_rating", methods=["POST"])
def insert_rating():
    req = request.json
    uid, iid, rating = req['idSocio'], req['idProducto'], req['rating']
    try:
        db.insert_rating(uid, iid, rating)
        return {'ok': True}
    except Exception as e :
        print(e)
        return {'ok': False}

@app.route("/get_ratings", methods=["POST"])
def get_ratings():
    """Obten los ratings de el usuario.

    Returns:
        dict(iids: list, ratings: list)
    """
    req = request.json
    uid = req['idSocio']
    res = {'ok': True}
    try:
        res = db.get_ratings(uid)
    except Exception as e :
        print(e)
        res['ok'] = False
    finally:
        return res

@app.route("/get_recs", methods=["POST"])
def get_recs():
    """Generacion de recomendacion usando filtros colaborativos basados en productos
    usando la similiradidad de pearson.

    Returns:
        {was_possible: bool, productsInfo: list<{idProducto, nombre, marca, precioUnitario, idSubCat}>}: 
            was_possible = True Si fue posible generar una recomendacion   
            products: Lista de atributos de productos.
    """
    uid = request.json['uid']
    res = {'was_possible': False}
    try:
        iid_recs = get_top_item_based(algo, uid, trainset, sims)  # if raw_id not in trainset it raises error
        res['productsInfo'] = db.get_products_info(iid_recs)
        res['was_possible'] = True
    except ValueError as e:
        res['productsInfo'] = get_top_global(good_ratings_df)
    return res


    #generar ticket de compra
@app.route("/api/v1/receipts/")
def index():
    options = {
  "enable-local-file-access": None
    }
    name = "images/fondo.jpg"
    html = render_template(
        "ticket.html"
        ,name=name)
    pdf = pdfkit.from_string(html, False,options=options)
    response = make_response(pdf)
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = "inline; filename=ticket_compra.pdf"
    return response

if __name__ == "__main__":
    app.run(debug=True, port=5001)
