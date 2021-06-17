import os
import jsmin
import csv
import random
import itertools
import sqlite3
from flask import Flask, jsonify, request, render_template, g
from flask_assets import Environment, Bundle

# IP-related imports:
# import socket
# import ipinfo

# App configuration
app = Flask(__name__)
assets = Environment(app)

# Bundle javascript files into minified "bundle.js"
js = Bundle('js/jquery.min.js', 'js/store.js', 'js/animation.js', 'js/helpers.js', 'js/index.js',
            filters='jsmin', output='bundle.js')
assets.register('js_all', js)

# CONSTANTS
KEY = "AIzaSyCCl7-ieDSLRydryyQ1JaypI_dKuBhqfOc"
DATABASE_PATH = './data/ip_addresses.sqlite3'


# ROUTES


# Index: Displays a static map on load
@app.route("/")
def index():
    return render_template("index.html", key=KEY)


# Routers: Generates GeoJSON locations of _num_routers_ routers
@app.route("/routers")
def routers():
    # Randomly select ip addresses from table to represent the routers
    num_routers = request.args.get("num_routers")
    routers = []

    for ip in query_db('SELECT * FROM ip_addresses ORDER BY RANDOM() LIMIT ' + num_routers, one=False):
        routers.append(ip)

    return jsonify(routers)


# Animate: Sends the request asynchronously, and runs an animation
@app.route("/animate")
def animate():
    # Run the AJAX request
    requestData = request.args.get("request_data")

    # Provide the response data to the template
    return jsonify("animate")


# Database Helpers

# get_db
# Retrieves ip address database for usage
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE_PATH)
        db.row_factory = dict_factory
    return db


# dict_factory
# Converts the given _row_ from the to a dictionary
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


# query_db
# Once created, queries the ip address database
def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


# close_connection
# Closes the database when finished
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


# Run app
if __name__ == "__main__":
    app.run(debug=True)
