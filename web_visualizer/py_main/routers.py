from web_visualizer import app, db
from web_visualizer.py_main.classes import Router, LandingPoint, Point, Path
from web_visualizer.py_auxiliary.helpers import *
from web_visualizer.py_auxiliary.constants import *

from flask import jsonify, request, g, abort, session

from itertools import combinations

import urllib.request
import json
import os


# Routers: Generates GeoJSON locations of _num_routers_ routers
@app.route("/routers")
def routers():

    num_routers = int(request.args.get("num_routers"))
    session["num_routers"] = num_routers

    seed = random_router_seed(num_routers)
    session["router_seed"] = seed

    routers = []

    for id in range(seed, seed + num_routers):
        routers.append(Router.query.get(id))

    # Query this new set of points from the database
    return jsonify(list(map(lambda point: point.toJson(), LandingPoint.query.all()+routers)))
