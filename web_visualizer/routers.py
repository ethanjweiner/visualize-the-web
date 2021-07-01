from web_visualizer import app
import random
import urllib.request
import json
from flask import jsonify, request, g
from web_visualizer.classes import Router, LandingPoint
from web_visualizer.database import Database

# Constants


IP_ADDRESSES_PATH = './web_visualizer/data/ip_addresses.sqlite3'
POINTS_PATH = './web_visualizer/data/points.sqlite3'
LANDING_POINTS_DATA = './web_visualizer/data/landing_points.json'

# Data Definitions

# Routers: Generates GeoJSON locations of _num_routers_ routers


@app.route("/routers")
def routers():
    # Randomly select ip addresses from table to represent the routers
    num_routers = request.args.get("num_routers")

    routers = router_points(num_routers)
    points = landing_points()

    store_points(routers, points)

    # Provide a jsonified version for the client to render
    return jsonify(list(map(lambda point: point.__dict__, routers+points)))

# router_points : Number -> [List-of Router]
# Uses the ip_addresses database to generate a list of Routers, of size _num_routers_


def router_points(num_routers):

    ip_addresses_db = Database(IP_ADDRESSES_PATH)
    routers = []

    # Change to insert num_routers as argument instead (to avoid database manipulation)
    for ip in ip_addresses_db.query_db('SELECT * FROM ip_addresses ORDER BY RANDOM() LIMIT ?',
                                       [num_routers]):
        routers.append(
            Router(ip["ip"], ip["latitude"], ip["longitude"],
                   continent_code=ip["continent_id"]))
    return routers


# landing_points : _ -> [List-of LandingPoint]
# Uses the data on oceanic cables to generate a list of LandingPoints
def landing_points():
    # Try loading from JSON file, and test speed
    with open(LANDING_POINTS_DATA) as landing_points_file:
        landing_points_data = json.load(landing_points_file)

    landing_points = []

    for landing_point in landing_points_data["features"]:
        latitude = landing_point["geometry"]["coordinates"][1]
        longitude = landing_point["geometry"]["coordinates"][0]
        landing_points.append(LandingPoint(
            latitude, longitude, landing_point["properties"]["id"]))

    # Temporary solution: Just return the landing points themselves, without cable data
    return landing_points


# get_continent : Number Number -> String
# Retrieves the continent code associated with the continent in which [_latitude_, _longitude_] is located
def get_continent(latitude, longitude):
    return 'Continent'


# store_points : [List-of Router] [List-of LandingPoint] -> _
# Stores the points in sqlite3 database for later access
def store_points(routers, landing_points):
    # Initialize databases
    points_db = Database(POINTS_PATH)
    cursor = points_db.db.cursor()

    # Clear the database
    points_db.clear('routers')
    points_db.clear('landing_points')

    # Insert into the database
    for router in routers:
        # Begin and end a trasncation for efficiency
        cursor.execute("BEGIN")
        points_db.query_db('INSERT INTO routers (ip, latitude, longitude, continent_code) VALUES (?,?,?,?)', [
            router.ip, router.latitude, router.longitude, router.continent_code])
        cursor.execute("COMMIT")
    for landing_point in landing_points:
        # Begin and end a trasncation for efficiency
        cursor.execute("BEGIN")
        points_db.query_db('INSERT INTO landing_points (latitude, longitude, continent_code, point_id) VALUES (?,?,?,?)', [
            landing_point.latitude, landing_point.longitude, landing_point.continent_code, landing_point.point_id])
        cursor.execute("COMMIT")
