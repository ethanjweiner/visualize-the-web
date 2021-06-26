from web_visualizer import app
import sqlite3
import random
import urllib.request
import json
from flask import jsonify, request, g
from web_visualizer.classes import Router, LandingPoint
from web_visualizer.store import *

# Constants


DATABASE_PATH = './web_visualizer/data/ip_addresses.sqlite3'
LANDING_POINTS_DATA = './web_visualizer/data/landing_points.json'

# Data Definitions

# Routers: Generates GeoJSON locations of _num_routers_ routers
@app.route("/routers")
def routers():
    # Randomly select ip addresses from table to represent the routers
    num_routers = request.args.get("num_routers")

    ROUTERS = router_points(num_routers)
    LANDING_POINTS = landing_points()

    points = ROUTERS + LANDING_POINTS

    return jsonify(points)


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

# router_points : Number -> [List-of Router]
# Uses the ip_addresses database to generate a list of Routers, of size _num_routers_
def router_points(num_routers):
    routers = []

    # Change to insert num_routers as argument instead (to avoid database manipulation)
    for ip in query_db('SELECT * FROM ip_addresses ORDER BY RANDOM() LIMIT ' + num_routers, one=False):
        routers.append(Router(ip["latitude"], ip["longitude"], ip["continent_id"], ip["ip"]).jsonify())
    
    return routers


# landing_points : _ -> [List-of LandingPoint]
# Uses the data on oceanic cables to generate a list of LandingPoints
def landing_points():
    # Try loading from JSON file, and test speed
    with open(LANDING_POINTS_DATA) as landing_points_file:
        landing_points_data = json.load(landing_points_file)

    landing_points = []

    for landing_point in landing_points_data["features"]:
        landing_points.append(LandingPoint(landing_point["geometry"]["coordinates"][1], landing_point["geometry"]["coordinates"][0], landing_point["properties"]["id"]).jsonify())

    # Temporary solution: Just return the landing points themselves, without cable data
    return landing_points


# Distance: Node Node -> Number
# Determine the distance from _p1_ to _p2_
# Research how to determine distance w/ latitude & longitude (just the hypotenuse of pythagorean theorem?)
def distance(p1, p2):
    return 0