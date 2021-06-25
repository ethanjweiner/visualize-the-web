from web_visualizer import app
import socket
import ipinfo
from flask import jsonify, request

# Animate: Sends the request asynchronously, and runs an animation


@app.route("/animate")
def animate():
    # 1. Run the AJAX request, & retrieve response data
    request_data = request.args.get("request_data")
    # Create routers for the client & server to be able to route from
    client_router = Router(...) # Retrieve location information using geolocation
    server_router = Router(...) # Retrieve location information using DNS (socket) & ipinfo

    # 2. Route from source -> destination (one packet)
    request_packet_routes = []
    for i in range(request_data["num_packets"]):
        request_packet_routes.append(client_router.route(server_router))

    # 3. Route destination -> source (one packet)
    response_packet_routes = []
    for i in range(request_data["num_packets"]):
        request_packet_routes.append(server_router.route(client_router))

    # 4. Send request routes and response routes to the browser to animate
    return jsonify("animate")