from web_visualizer import app
from flask import jsonify, request, session
from web_visualizer.classes import Router, LandingPoint
from web_visualizer.helpers import *


@app.route("/routes")
def routes():
    direction = request.args.get("direction")

    client_data = session['client_data']
    server_data = session['server_data']

    client_router = Router(ip=client_data['ip_details']['ip'], latitude=client_data['request_details']['latitude'],
                           longitude=client_data['request_details']['longitude'], continent_code=client_data['ip_details']['continent'])
    server_router = Router(ip=server_data['ip_details']['ip'], latitude=server_data['ip_details']['latitude'],
                           longitude=server_data['ip_details']['longitude'], continent_code=server_data['ip_details']['continent'])

    print(client_router, server_router)

    routers = Router.query.all()

    if direction == "request":
        route = client_router.route(server_router, routers)
    else:
        route = server_router.route(client_router, routers)

    return jsonify(list(map(lambda router: router.toJson(), route)))
