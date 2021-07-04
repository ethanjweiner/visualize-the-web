from web_visualizer import app
import random
import urllib.request
import json
from flask import jsonify, request, g
from web_visualizer.classes import Router, LandingPoint, Point, Path
from web_visualizer.database import Database
from web_visualizer import db
from web_visualizer.helpers import *
import os
from itertools import combinations

# Constants
IP_ADDRESSES_PATH = './web_visualizer/data/ip_addresses.sqlite3'
LANDING_POINTS_PATH = '/Users/ethanweiner/Downloads/www.submarinecablemap.com-master/public/api/v2/landing-point'
CABLES_PATH = '/Users/ethanweiner/Downloads/www.submarinecablemap.com-master/public/api/v2/cable'


# Routers: Generates GeoJSON locations of _num_routers_ routers


@app.route("/routers")
def routers():
    # Randomly select ip addresses from table to represent the routers
    num_routers = request.args.get("num_routers")

    # Delete any existing routers
    print(Router.query.first())

    if Router.query.first() != None:
        Router.query.delete()

    # Generate and store routers in database

    store_routers(num_routers)
    store_paths()

    # Query this new set of points from the database
    return jsonify(list(map(lambda point: point.toJson(), Point.query.all())))

# store_routers : Number -> [List-of Router]
# Uses the ip_addresses database to generate a list of Routers, of size _num_routers_


def store_routers(num_routers):
    print("Storing routers...")
    ip_addresses_db = Database(IP_ADDRESSES_PATH)
    routers = []

    # Change to insert num_routers as argument instead (to avoid database manipulation)
    for ip in ip_addresses_db.query_db('SELECT * FROM ip_addresses ORDER BY RANDOM() LIMIT ?',
                                       [num_routers]):
        db.session.add(
            Router(ip=ip["ip"], latitude=ip["latitude"], longitude=ip["longitude"],
                   continent_code=ip["continent_id"]))

    db.session.commit()


# store_paths
# TEMPORARY FUNCTION: Used to initially store the paths into a table
def store_paths():
    print("Storing paths...")

    for file in os.listdir(CABLES_PATH):
        with open(CABLES_PATH + '/' + file) as cable_file:
            try:
                landing_points = json.load(cable_file)["landing_points"]
                cable_paths = paths(landing_points)
                for path in cable_paths:
                    db.session.add(path)
            except KeyError:
                continue
    db.session.commit()


# paths
# Given the _landing_points_ of a cable, generate all the 2-way cable paths (as point id's) that a packet could take
def paths(landing_points):
    point_ids = map(lambda landing_point: landing_point["id"], landing_points)
    # Generate all 2-sized subsets of the landing points
    point_combinations = combinations(point_ids, 2)
    paths = []
    for combination in point_combinations:
        # Add the path and reverse of that path
        paths.append(
            Path(start_point_id=combination[0], end_point_id=combination[1]))
        paths.append(
            Path(start_point_id=combination[1], end_point_id=combination[0]))

    return paths

# store_landing_points
# TEMPORARY FUNCTION: Used to initially store the landing points


def store_landing_points():
    print("Storing landing points...")
    # Iterate through all landing point JSON files
    for file in os.listdir(LANDING_POINTS_PATH):
        if file == "all.json":
            continue
        with open(LANDING_POINTS_PATH + '/' + file) as landing_point_file:
            data = json.load(landing_point_file)
            try:
                continent_code = parse_continent(data["name"])
                landing_point = LandingPoint(latitude=data["latitude"], longitude=data["longitude"],
                                             point_id=data["id"], continent_code=continent_code, type="landing_point")
                db.session.add(landing_point)
            # Disregard landing points with invalid countries
            except KeyError:
                continue

    db.session.commit()
