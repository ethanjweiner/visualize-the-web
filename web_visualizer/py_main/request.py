from web_visualizer import app
from web_visualizer.py_main.classes import *
from web_visualizer.py_auxiliary.helpers import get_continent
from web_visualizer.py_auxiliary.config import IP_INFO_ACCESS_TOKEN

from flask import jsonify, request, session, abort

import socket
import ipinfo
import requests
import json
import random

from urllib.parse import urlparse


@app.route("/request", methods=["POST"])
def http_request():
    # 1. Run the AJAX request, & retrieve response data
    client_ip_details = get_ip_details()

    request_details = json.loads(request.form.get("request_details"))

    client_data = {
        "request_details": request_details,
        "ip_details": client_ip_details
    }

    if request_details["is_random"]:
        client_data["request_details"]["request_url"] = None
        server_data = choose_random_destination(request_details["num_routers"])
    else:
        server_data = simulate_http_request(
            client_data["request_details"]["request_url"], client_data["request_details"]["request_method"], client_data["request_details"]["request_content"])

    # Store the client & server data in a session for routing
    session['client_data'] = client_data
    session['server_data'] = server_data

    # Send client and server data back to the browser & the next route
    return jsonify(client_data=client_data, server_data=server_data)


# simulate_http_request : String String [Maybe String] -> Dictionary
# Simulates an HTTP request, & subsequently retrieves information about the server and its response
def simulate_http_request(request_url, request_method, request_content=None):
    # Retrieve response content
    try:
        if request_method == "POST":
            response = requests.post(request_url, data=request_content)
        else:
            response = requests.get(request_url)
    except Exception:
        abort(404, description="The request could not be made to the provided URL. Please check your spelling.")

    try:
        ip_details = get_ip_details(url=response.url)
    except Exception:
        abort(404, description="The IP details for the provided URL could not be found. Please use a different URL.")

    return {
        "response_details": {
            "response_url": response.url,
            "status_code": response.status_code,
            "content-type": response.headers["content-type"]
        },
        "ip_details": ip_details
    }


# choose_random_destination
# Chooses a random router to use as the deestination
def choose_random_destination(num_routers):
    first_id = Router.query.first().id
    rand_id = random.randint(first_id, first_id + num_routers)
    router = Router.query.get(rand_id)

    return {
        "ip_details": {
            "ip": router.ip,
            "continent": router.continent_code,
            "latitude": router.latitude,
            "longitude": router.longitude

        }
    }


# get_ip_details : [Maybe String] -> IP Details
# Retrieves the ip-related details associated with a particular _url_ or the local ip address
def get_ip_details(url=None):
    if url:
        host_name = get_host_name(url)
        ip = socket.gethostbyname(host_name)
    else:
        ip = requests.get('https://api.ipify.org').text

    handler = ipinfo.getHandler(IP_INFO_ACCESS_TOKEN)
    details = handler.getDetails(ip)

    return {
        "ip": ip,
        "city": details.city,
        "region": details.region,
        "country": details.country,
        "continent": get_continent(details.country),
        "latitude": details.loc.split(',')[0],
        "longitude": details.loc.split(',')[1],
    }


# get_host_name : String -> String
# Determines the host name of the given _url_
def get_host_name(url):
    try:
        parsed_url = urlparse(url)
    except NameError:
        abort(404, description="The IP details for the provided URL could not be found. Please use a different URL.")
    return parsed_url.netloc
