from web_visualizer import app
import sqlite3
import random
import urllib.request
import json
from flask import jsonify, request, g

# Data Definitions

# INTERPREATION: A router with _ip_ located at [_latitude_, _longitude_]


def Router(ip, latitude, longitude):
    return {
        "ip": ip,
        "latitude": latitude,
        "longitude": longitude
    }

# INTERPREATION: A landing point for an oceanic cable, defining a path from _start_router_ to _end_router_ via _inner_nodes_


def OceanicRouter(start_router, inner_nodes, end_router):
    return {
        "start_router:": start_router,
        "inner_nodes": inner_nodes,
        "end_router": end_router
    }

# INTERPREATION: A node along an oceanic cable, located at [_latitude_, _longitude_]


def Node(latitude, longitude):
    return {
        "latitude": latitude,
        "longitude": longitude
    }


DATABASE_PATH = './web_visualizer/data/ip_addresses.sqlite3'
oceanic_routers = []

# Routers: Generates GeoJSON locations of _num_routers_ routers


@app.route("/routers")
def routers():
    # Randomly select ip addresses from table to represent the routers
    num_routers = request.args.get("num_routers")

    routers = []

    for ip in query_db('SELECT * FROM ip_addresses ORDER BY RANDOM() LIMIT ' + num_routers, one=False):
        routers.append(Router(ip["ip"], ip["latitude"], ip["longitude"]))

    routers = routers + oceanic_routers

    return jsonify(routers)

# Oceanic Cables: Called on load; Generate GeoJSON data of all oceanic cables


@app.route("/oceanic_cables")
def oceanic_cables():
    return jsonify("Placeholder")


# DATABASE HELPERS

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
