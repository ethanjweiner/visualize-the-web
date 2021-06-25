from web_visualizer import app
import sqlite3
import random
import urllib.request
import json
from flask import jsonify, request, g

# Constants


DATABASE_PATH = './web_visualizer/data/ip_addresses.sqlite3'
LANDING_POINTS_DATA = './web_visualizer/data/landing_points.json'
ROUTERS = []
LANDING_POINTS = []

# Data Definitions

# INTERPRETATION: A router with _ip_ located at [_latitude_, _longitude_]
class Router():
    def __init__(self, ip, latitude, longitude):
        self.ip = ip
        self.latitude = latitude
        self.longitude = longitude
    # Provide a json version of a router, so that it can be provided to the browser
    def jsonify(self):
        return {
            "ip": self.ip,
            "latitude": self.latitude,   
            "longitude": self.longitude
        }
    # Determine a route from _self_ to _destination_, such that the next router is closer to the destination
    # ACCUMULATOR: The _path_ generated so far in the routing process
    # TERMINATION: On each recursion, the current router in the path must be closer to _destination_ than the previous
    def route(self, destination, path=[]):
        # Base case: The destination has been reached
        if self.latitude == destination.latidue and self.longitude == self.latitude:
            return path
        # Circular case: We backtracked by accident
        elif self in path:
            return None
        else:
            # Route the next router/landing point: route(...)
            return None


# INTERPREATION: A landing point for an oceanic cable, defining a path from _start_router_ to _end_router_ via _inner_nodes_
# By storing landing points like this, routing across the ocean will be an easy process
# N.B. The landing point might be stored twice, if that landing point connects to multiple cables
class LandingPoint(Router):
    def __init__(self, latitude, longitude, point_id):
        # Landing points don't have an ip address
        super().__init__(None, latitude, longitude)
        self.point_id = point_id
    # Provide a json version of a landing point, so that it can be provided to the browser
    def jsonify(self):
        return {
            "ip": self.ip,
            "latitude": self.latitude,   
            "longitude": self.longitude,
            "point_id": self.point_id
        }
    # Determine a route from _self_ to _destination_, such that the next router is closer to the destination
    # ACCUMULATOR: The _path_ generated so far in the routing process
    # TERMINATION: On each recursion, the current router in the path must be closer to _destination_ than the previous
    def route(self, destination, path=[]):
        # Base case: The destination has been reached
        if self.latitude == destination.latidue and self.longitude == self.latitude:
            return path
        # Circular case: We backtracked by accident
        elif self in path:
            return None
        else:
            # Choose a cable starting from _self_ whose endpoint (lat/lng) is closest to _destination_
            # Route the next router / landing point: route(...)
            return None




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

    for ip in query_db('SELECT * FROM ip_addresses ORDER BY RANDOM() LIMIT ' + num_routers, one=False):
        routers.append(Router(ip["ip"], ip["latitude"], ip["longitude"]).jsonify())
    
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