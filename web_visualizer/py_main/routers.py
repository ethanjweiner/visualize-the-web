from web_visualizer import app, db
from web_visualizer.py_main.classes import Router, LandingPoint, Point, Path
from web_visualizer.py_auxiliary.database import Database
from web_visualizer.py_auxiliary.helpers import *
from web_visualizer.py_auxiliary.constants import *

from flask import jsonify, request, g, abort

from itertools import combinations

import urllib.request
import json
import os

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
