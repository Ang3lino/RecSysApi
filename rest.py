from flask import Flask, render_template, request, jsonify
from flaskext.mysql import MySQL

import itertools
import json


app = Flask(__name__)
app.config.from_pyfile("config.py")

mysql = MySQL()
mysql.init_app(app)

conn = mysql.connect()
cursor = conn.cursor()


@app.route("/ping")
def ping():
    return "pong!"

@app.route("/register", methods=["POST"])
def register():
    socio = request.json
    print(socio)
    # args_order = ('apPaterno', 'apMaterno', 'nombre', 'edad', 'genero', 'email', 'passwd')
    # args = tuple(socio[arg] for arg in args_order)
    # cursor.callproc('insert_socio', args)
    # conn.commit()   
    return jsonify({'ok': True})

@app.route("/login", methods=["POST"])
def login():
    email, passwd = request.json['email'], request.json['passwd']
    cursor.execute('select passwd, idSocio from socio where email = %s ', email)
    passwd_id_from_db = cursor.fetchone()
    res = {'email_found': False, 'correct_passwd': False, 'idSocio': False}
    if passwd_id_from_db:
        res['email_found'] = True
        res['correct_passwd'] = passwd == passwd_id_from_db[0]
        if res['correct_passwd']:
            res['idSocio'] = passwd_id_from_db[1]
    return res


if __name__ == "__main__":
    app.run(debug=True, port=5001)
