from flask import Flask, render_template, request, jsonify
from flaskext.mysql import MySQL

import pymysql  # mysql error handling
import itertools
import json
import pandas as pd
import numpy as np

from db_helper import DbHelper
from rec_utils import *

# para generar pdf
from flask import render_template, make_response
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
    return db.get_products_info(iids.tolist(), extra_info={'valoro': 'n'})

def safe_return(fun, *args):
    try:
        res = fun(*args)
        res['ok'] = True 
        return res
    except Exception as e:
        print(e)
        return {'ok': False, 'err': str(e)}

def safe_apply(fun, *args):
    try:
        fun(*args)
        return {'ok': True}
    except Exception as e:
        print(e)
        return {'ok': False, 'err': str(e)}

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

@app.route("/update_user", methods=["POST"])
def update_user():
    s = request.json
    nombre, apPaterno, apMaterno, idSocio = s['nombre'], s['apPaterno'], s['apMaterno'], s['idSocio']
    return safe_apply(db.update_user, nombre, apPaterno, apMaterno, idSocio)

@app.route("/insert_hist", methods=["POST"])
def insert_hist():
    """Inserta las compras realizadas al historial
        {idSocio: str, idProductos: list<str>, cantidades: list<int>}
    Returns:
        {success: bool}: True en caso de poder escribir en la base.
    """
    req = request.json
    uid, iids, amounts = req["idSocio"], req["idProductos"], req["cantidades"]
    return safe_return(db.insert_hist, uid, iids, amounts)

@app.route("/get_purchases", methods=["GET", "POST"])
def get_purchases():
    """Regresa los valores de historial dado el uid.

    Returns:
        dict{idSocio: list, idProducto: list, fecha_hora: list, cantidad: list}
    """
    uid = request.json['idSocio']
    return safe_return(db.get_purchases, uid)

@app.route("/insert_pendiente", methods=["POST"])
def insert_pendiente():
    """Inserta un pendiente de compra de un usuario
        {idSocio: str, idProductos: str}
    Returns:
        {success: bool}: True en caso de poder escribir en la base.
    """
    req = request.json
    uid, iid = req["idSocio"], req["idProducto"]
    return safe_apply(db.insert_pendiente, uid, iid)

@app.route("/get_pendientes", methods=["GET", "POST"])
def get_pendientes():
    """Inserta un pendiente de compra de un usuario
        {idSocio: str, idProductos: str}
    Returns:
        {success: bool}: True en caso de poder escribir en la base.
    """
    uid = request.json['idSocio']
    return safe_return(db.get_pendientes, uid)

@app.route("/get_products_info", methods=["GET", "POST"])
def get_products_info():
    """Dado {idProducto: list} regresamos los productos cuyo id en estos valores. 
    Si ningun iid esta en la base, se regresa una lista vacia.

    Returns:
        {productsInfo: list<producto>}
    """
    iids = request.json["idProducto"]
    return safe_return(db.get_products_info, iids)

@app.route("/get_product_info", methods=["GET", "POST"])
def get_product_info():
    """Obten la informacion de un producto. Si el producto no existe ok=False. 
    Si se provee uid se sabra si el usuario ya ha valorado el producto (y/n).

    Returns:
        dict: {ok: bool[, err: str][, informacion del producto]}
    """
    iid = request.json["idProducto"]  # item id 
    uid = request.json.get("idSocio", None)  # user id
    return safe_return(db.get_product_info, iid, uid)

@app.route("/insert_rating", methods=["POST"])
def insert_rating():
    req = request.json
    uid, iid, rating = req['idSocio'], req['idProducto'], req['rating']
    return safe_apply(db.insert_rating, uid, iid, rating)

@app.route("/get_ratings", methods=["POST"])
def get_ratings():
    """Obten los ratings de el usuario.

    Returns:
        dict(iids: list, ratings: list)
    """
    req = request.json
    uid = req['idSocio']
    return safe_return(db.get_ratings, uid)

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
        res['productsInfo'] = db.get_products_info(iid_recs, extra_info={'valoro': 'n'})
        res['was_possible'] = True
    except ValueError as e:
        res['productsInfo'] = get_top_global(good_ratings_df)
    return res

@app.route("/dev_read", methods=["POST"])
def dev_read():
    '''FOR DEV ONLY, execute any query remotely. '''
    query = request.json['query']
    res = dict()
    try:
        res['resultset'] = db.read(query)
        return res
    except Exception as e:
        res['err'] = str(e)
    return res

@app.route("/dev_write", methods=["POST"])
def dev_write():
    '''FOR DEV ONLY, execute any query remotely. '''
    query = request.json['query']
    res = {"ok": True}
    try:
        db.write(query)
    except Exception as e:
        res['ok'] = False
        res['err'] = str(e)
    return res

@app.route("/api/v1/receipts/", methods=["GET", "POST"])
def tickets():
    
    uid = request.json["idSocio"]     
    res = {"Tickets": True}
    tot=0
    try:
        tickets=db.get_tickets_info(uid)
        res['Tickets']=tickets
        return res
    except Exception as e:
        res['ok'] = False
        res['err'] = str(e)
    return res

@app.route("/api/v1/receipt/", methods=["GET", "POST"])
def index():
    '''Generar ticket de compra.'''
    options = { "enable-local-file-access": None }
    name = "images/fondo.jpg"

    uid = request.json["idSocio"] 
    iid = request.json["idProducto"]  # item id 
    date = request.json["fecha_hora"]
    
    products=db.get_ticket_info(uid,iid,date)

    html = render_template("ticket.html", name=name)
    html = html.replace('[CLIENT]',str(products[0][0]))
    html = html.replace('[DATE]',str(date))

    p = float("{:.2f}".format(products[0][3]))
    u = products[0][2]
    tot = p*u
    html = html.replace('[DESCRIPTION]', products[0][1][0:30])
    html = html.replace('[UNIT]', str(u))
    html = html.replace('[COST]', str(p))
    html = html.replace('[TOTAL_COST]', str(tot))
    total = tot
    if len(products) > 1:
        add_product = ''
        for i in range(len(products)):
            html_to_add='''
                    <tr>
                        <td width="50%">
                            <b>[DESCRIPTION]</b>
                        </td>
                        <td width="10%">
                            <b>[UNIT]</b>
                        </td>
                        <td width="25%">
                            <b>[COST]</b>
                        </td>
                        <td width="50%">
                            <b>[TOTAL_COST]</b>
                        </td>
                    </tr>'''
            p=float("{:.2f}".format(products[i][3]))
            u=products[i][2]
            tot=p*u
            html_to_add=html_to_add.replace('[DESCRIPTION]',str(products[i][1])[0:30])
            html_to_add=html_to_add.replace('[UNIT]',str(u))
            html_to_add=html_to_add.replace('[COST]',str(p))
            html_to_add=html_to_add.replace('[TOTAL_COST]',str(tot))
            add_product+=html_to_add
            total+=tot
        html=html.replace('[ADD_PRODUCT]',add_product)
    total=float("{:.2f}".format(total))
    html=html.replace('[TOTAL]',str(total))

    pdf = pdfkit.from_string(html, False, options=options)
    response = make_response(pdf)
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = "inline; filename=ticket_compra.pdf"
    return html


@app.route("/api/v1/receipt2/", methods=["GET", "POST"])
def ticket2():
    '''Generar ticket de compra.'''
    options = { "enable-local-file-access": None }
    name = "images/fondo.jpg"
    res={"Ticket": False}
    uid = request.json["idSocio"] 
    iid = request.json["idProducto"]  # item id 
    date = request.json["fecha_hora"]
    
    products=db.get_ticket_info(uid,iid,date)
    if not products:
        return res
    html = render_template("ticket.html", name=name)
    html = html.replace('[CLIENT]',str(products[0][0]))
    html = html.replace('[DATE]',str(date))

    p = float("{:.2f}".format(products[0][3]))
    u = products[0][2]
    tot = p*u
    html = html.replace('[DESCRIPTION]', products[0][1][0:30])
    html = html.replace('[UNIT]', str(u))
    html = html.replace('[COST]', str(p))
    html = html.replace('[TOTAL_COST]', str(tot))
    total = tot
    add_product = ''
    if len(products) > 1:
        for i in range(len(products)-1): 
            if i==0:
                i+=1           
            html_to_add='''
                    <tr>
                        <td width="50%">
                            <b>[DESCRIPTION]</b>
                        </td>
                        <td width="10%">
                            <b>[UNIT]</b>
                        </td>
                        <td width="25%">
                            <b>[COST]</b>
                        </td>
                        <td width="50%">
                            <b>[TOTAL_COST]</b>
                        </td>
                    </tr>'''
            p=float("{:.2f}".format(products[i][3]))
            u=products[i][2]
            tot=p*u
            html_to_add=html_to_add.replace('[DESCRIPTION]',str(products[i][1]))
            html_to_add=html_to_add.replace('[UNIT]',str(u))
            html_to_add=html_to_add.replace('[COST]',str(p))
            html_to_add=html_to_add.replace('[TOTAL_COST]',str(tot))
            add_product+=html_to_add
            total+=tot
    html=html.replace('[ADD_PRODUCT]',add_product)
    total=float("{:.2f}".format(total))
    html=html.replace('[TOTAL]',str(total))

    pdf = pdfkit.from_string(html, 'C://Program Files (x86)//Apache Software Foundation//Tomcat 8.5//webapps//api//recibos//out.pdf', options=options)

    #response = make_response(pdf)
    #response.headers["Content-Type"] = "application/pdf"
    #response.headers["Content-Disposition"] = "inline; filename=ticket_compra.pdf"
    #res['Ticket']=html
    res={"Ticket": "http://189.189.230.82:8080/api/recibos/out.pdf"}
    return res

if __name__ == "__main__":
    app.run(debug=True, port=5001)
