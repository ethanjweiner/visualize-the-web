from web_visualizer import app
import socket
import ipinfo
from flask import jsonify, request
from web_visualizer.classes import Router, LandingPoint
import requests
from urllib.parse import urlparse
from web_visualizer.helpers import *

IP_INFO_ACCESS_TOKEN = '798b7b7ebf8444'


@app.route("/routes")
def routes():
    # 1. Run the AJAX request, & retrieve response data
    client_data = {
        "request_url": request.args.get("request_url"),
        "request_method": request.args.get("request_method"),
        "request_content": request.args.get("request_content"),
        "ip": None,
        "latitude": request.args.get("latitude"),
        "longitude": request.args.get("longitude")
    }

    num_packets = int(request.args.get("num_packets"))

    server_data = simulate_http_request(
        client_data["request_url"], client_data["request_method"], client_data["request_content"])

    # If there was an error processing the request, don't animate
    if server_data == 1:
        return jsonify("An error occured while sending the request")

    # Create routers for the client & server to be able to route from
    # Retrieve location information using geolocation
    client_router = Router(
        client_data['ip'], client_data["latitude"], client_data["longitude"])
    # Retrieve location information using DNS (socket) & IP_INFO_ACCESS_TOKEN
    server_router = Router(
        server_data["ip"], server_data["latitude"], server_data["longitude"])

    # 2. Route from source -> destination, and vice versa
    request_routes = generate_routes(client_router, server_router, num_packets)
    response_routes = generate_routes(
        server_router, client_router, num_packets)

    # 3. Send request routes and response routes to the browser to animate
    return jsonify("Routes and animation data")


# simulate_http_request
# Simulates an HTTP request, & subsequently retrieves information about the server and its response
# - Response content
# - Server ip
# - Server location
def simulate_http_request(request_url, request_method, request_content=None):
    # Retrieve response content

    if request_method == "POST":
        response = requests.post(request_url, data=request_content)
    else:
        response = request.get(request_url)

    # If the response is unsuccessful, signify an error
    if response.status_code / 100 == 4 or response.status_code / 100 == 5:
        return 1  # The response was faulty

    host_name = get_host_name(response.url)

    if host_name == 1:
        return 2  # The host was invalid

    # Retrieve information about the server/host
    server_ip = socket.gethostbyname(host_name)
    handler = ipinfo.getHandler(IP_INFO_ACCESS_TOKEN)
    details = handler.getDetails(server_ip)

    return {
        "response_url": response.url,
        "status_code": response.status_code,
        "content-type": response.headers["content-type"],
        "ip": server_ip,
        "city": details.city,
        "region": details.region,
        "country": details.country,
        "latitude": details.loc.split(',')[0],
        "longitude": details.loc.split(',')[1]
    }


# generate_routes : Router Router Number -> [List-of Router]
# Generate _num_routes_ routes from the _origin_ router to the _destination_ router
def generate_routes(origin, destination, num_routes):

    routes = []

    for i in range(num_routes):
        routes.append(origin.route(destination, routers))

    return routes


# get_host_name : String -> String
# Determines the host name of the given _url_
def get_host_name(url):
    try:
        parsed_url = urlparse(url)
    except NameError:
        return 1
    return parsed_url.netloc
