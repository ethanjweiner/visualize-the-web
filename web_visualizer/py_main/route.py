from web_visualizer import app
from web_visualizer.py_main.classes import Point, Router, LandingPoint
from web_visualizer.py_auxiliary.helpers import *
from flask import jsonify, request, session, abort

import random
import time

# A Route is a [List-of X] where X can be a:
# - Router
# - LandingPoint
# - Cable


@app.route("/route")
def routes():
    direction = request.args.get("direction")

    client_data = session['client_data']
    server_data = session['server_data']

    client_router = Router(ip=client_data['ip_details']['ip'], latitude=float(client_data['request_details']['latitude']),
                           longitude=float(client_data['request_details']['longitude']), continent_code=client_data['ip_details']['continent'])
    server_router = Router(ip=server_data['ip_details']['ip'], latitude=float(server_data['ip_details']['latitude']),
                           longitude=float(server_data['ip_details']['longitude']), continent_code=server_data['ip_details']['continent'])

    route = False

    if direction == "request":
        # Set up a timer here?
        route = client_router.init_routing(
            server_router)
    else:
        route = server_router.init_routing(
            client_router)

    if len(route):
        return jsonify(list(map(lambda node: node.toJson(), route)))
    else:
        abort(500, description="No route could be found to the location of the provided domain. Please try again with new routers or a different URL.")
