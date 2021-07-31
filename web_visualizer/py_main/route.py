from web_visualizer import app
from web_visualizer.py_main.classes import Point, Router, LandingPoint
from web_visualizer.py_auxiliary.helpers import *

from flask import jsonify, request, session, abort


# A Route is a [List-of X] where X can be a:
# - Router
# - LandingPoint
# - Cable


@app.route("/route")
def routes():
    direction = request.args.get("direction")

    client_data = session['client_data']
    server_data = session['server_data']

    client_router = Router(ip=client_data['ip_details']['ip'], latitude=client_data['request_details']['latitude'],
                           longitude=client_data['request_details']['longitude'], continent_code=client_data['ip_details']['continent'])
    server_router = Router(ip=server_data['ip_details']['ip'], latitude=server_data['ip_details']['latitude'],
                           longitude=server_data['ip_details']['longitude'], continent_code=server_data['ip_details']['continent'])

    routers = Point.query.all()

    # Dynamically set radius increment based on distance
    # Wider radius ==> More options for routing
    starting_increment = starting_radius(client_router, server_router)

    route = False

    while not route:
        if direction == "request":
            route = client_router.route(
                server_router, routers, starting_increment)
        else:
            route = server_router.route(
                client_router, routers, starting_increment)

    if len(route):
        return jsonify(list(map(lambda node: node.toJson(), route)))
    else:
        abort(500, description="No route could be found to the location of the provided domain. Please try again with new routers or a different URL.")


def starting_radius(client_router, server_router):
    candidate = distance(client_router, server_router) / 15
    if candidate > 0.5:
        return candidate
    return 0.5
