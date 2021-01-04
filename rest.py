from flask import Flask, render_template, request, jsonify
from flaskext.mysql import MySQL

import itertools
import json


app = Flask(__name__)
app.config.from_pyfile('config.py')

mysql = MySQL()
mysql.init_app(app)

conn = mysql.connect()
cursor = conn.cursor()




if __name__ == "__main__":
    app.run(debug=True)