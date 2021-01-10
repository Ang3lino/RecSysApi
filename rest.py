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
    """Registra a un usuario. Los atributos del json son:
        ('apPaterno', 'apMaterno', 'nombre', 'edad', 'genero', 'email', 'passwd')
    
    Returns:
        {'email_used': bool, 'success': bool}
        Si el email ya ha sido usado email_used = True
        success es True si se pudo ingresar al usuario.
    """
    socio = request.json
    return db.register(socio)

@app.route("/login", methods=["POST"])
def login():
    """Determina si las credenciales estan en la base, si lo estan se regresa el uid.

    Returns:
        {'email_found': bool, 'correct_passwd': bool[, 'idSocio': str]?}: 
            email_found: True si este esta en la base
            correct_passwd = True si este coincide con el correo
            idSocio es agregado si ambas anteriores son verdad.
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

@app.route("/insert_pendiente", methods=["POST"])
def insert_pendiente():
    """Inserta un pendiente de compra de un usuario
        {idSocio: str, idProductos: str}
    Returns:
        {success: bool}: True en caso de poder escribir en la base.
    """
    return db.insert_pendiente(request.json)

@app.route("/get_products_info", methods=["GET"])
def get_products_info():
    iids = request.json["idProducto"]
    return db.get_products_info(iids)

@app.route("/get_product_info", methods=["GET"])
def get_product_info():
    iid = request.json["idProducto"]  # item id 
    return db.get_product_info(iid)

# TODO
# def insert_rating():
#     res = request.json
#     uid, iid, rating = res['idSocio'], req['idProducto'], req['rating']



@app.route("/get_recs", methods=["POST"])
def get_recs():
    """Generacion de recomendacion usando filtros colaborativos basados en productos
    usando la similiradidad de pearson.


    Returns:
        {was_possible: bool[, products: list<{idProducto, nombre, marca, precioUnitario, idSubCat}>]}: 
            was_possible = True Si fue posible generar una recomendacion   
            products: Lista de atributos de productos.
    """
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
