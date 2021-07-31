from web_visualizer import app, db
from web_visualizer.py_main.classes import Router, LandingPoint, Point, Path
from web_visualizer.py_auxiliary.database import Database
from web_visualizer.py_auxiliary.helpers import *
from web_visualizer.py_auxiliary.constants import *

from flask import jsonify, request, g, abort

import urllib.request
import json


# Routers: Generates GeoJSON locations of _num_routers_ routers
@app.route("/routers")
def routers():

    num_routers = request.args.get("num_routers")

    if Router.query.first() != None:
        Router.query.delete()

    # Randomly select & store routers
    try:
        store_routers(num_routers)
    except Exception:
        abort(
            500, description="There was a database error when generating the routers. Please refresh.")

    # Query this new set of points from the database
    return jsonify(list(map(lambda point: point.toJson(), Point.query.all())))


# store_routers : Number -> [List-of Router]
# Uses the ip_addresses database to generate a list of Routers, of size _num_routers_
def store_routers(num_routers):

    ip_addresses_db = Database(IP_ADDRESSES_PATH)
    routers = []

    # Change to insert num_routers as argument instead (to avoid database manipulation)
    for loc in ip_addresses_db.query_db('SELECT * FROM ip_addresses ORDER BY RANDOM() LIMIT ?',
                                        [num_routers]):
        db.session.add(
            Router(ip=loc["ip"], latitude=loc["latitude"], longitude=loc["longitude"],
                   continent_code=loc["continent_id"]))

    db.session.commit()
