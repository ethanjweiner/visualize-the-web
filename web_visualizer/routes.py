from web_visualizer import app
from flask import jsonify, request, session, abort
from web_visualizer.classes import Point, Router, LandingPoint
from web_visualizer.helpers import *

# Note

# A Route is a [List-of X] where X can be a:
# - Router
# - LandingPoint
# - Cable


@app.route("/routes")
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
    radius_increment = distance(client_router, server_router) / 15

    route = False

    while not route:
        if direction == "request":
            route = client_router.route(
                server_router, routers, radius_increment)
        else:
            route = server_router.route(
                client_router, routers, radius_increment)

    if len(route):
        return jsonify(list(map(lambda node: node.toJson(), route)))
    else:
        abort(500, description="No route could be found to the location of the provided domain. Please try again with new routers or a different URL.")
