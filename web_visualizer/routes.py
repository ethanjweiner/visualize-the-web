from web_visualizer import app
import socket
import ipinfo
from flask import jsonify, request
from web_visualizer.classes import Router, LandingPoint
import urllib.request


# Animate: Sends the request asynchronously, and runs an animation


@app.route("/routes")
def routes():
    # 1. Run the AJAX request, & retrieve response data
    client_data = {
        request_url: request.args.get("request_url"),
        request_method: request.args.get("request_method"),
        request_content: request.args.get("request_content"),
        ip: None,
        latitude: 0,
        longitude: 0
    }

    num_packets = request.args.get("num_packets"),

    server_data = simumlate_http_request(client_data.request_url, client_data.request_method, client_data.request_content)
    # Create routers for the client & server to be able to route from
    client_router = Router(0, 0) # Retrieve location information using geolocation
    server_router = Router(10, 10) # Retrieve location information using DNS (socket) & ipinfo

    # # 2. Route from source -> destination (one packet)
    request_routes = generate_routes(client_router, server_router, num_packets)
    # request_packet_routes = []
    # for i in range(request_data["num_packets"]):
    #     request_packet_routes.append(client_router.route(server_router))

    # # 3. Route destination -> source (one packet)
    response_routes = generate_routes(server_router, client_router, num_packets)
    # response_packet_routes = []
    # for i in range(request_data["num_packets"]):
    #     request_packet_routes.append(server_router.route(client_router))

    # 4. Send request routes and response routes to the browser to animate
    return jsonify("Routes and animation data")

# http_request
# Simulates an HTTP request, & subsequently retrieves information about the server and its response
# - Response content
# - Server ip
# - Server location
def simulate_http_request(request_url, request_method, request_content=''):
    return None


# generate_routes : Router Router Number -> [List-of Router]
# Generate _num_routes_ routes from the _origin_ router to the _destination_ router
def generate_routes(origin, destination, num_routes):
    for i in range(num_routes):
        print(i)
    return []