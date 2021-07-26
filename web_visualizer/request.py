from web_visualizer import app
import socket
import ipinfo
from flask import jsonify, request, session, abort
from web_visualizer.classes import Router, LandingPoint
import requests
from urllib.parse import urlparse
from web_visualizer.helpers import get_continent

IP_INFO_ACCESS_TOKEN = '798b7b7ebf8444'


@app.route("/request")
def http_request():
    # 1. Run the AJAX request, & retrieve response data
    ip_details = get_ip_details()

    client_data = {
        "request_details": {
            "request_url": request.args.get("request_url"),
            "request_method": request.args.get("request_method"),
            "request_content": request.args.get("request_content"),
            "latitude": request.args.get("latitude"),
            "longitude": request.args.get("longitude")
        },
        "ip_details": ip_details
    }

    server_data = simulate_http_request(
        client_data["request_details"]["request_url"], client_data["request_details"]["request_method"], client_data["request_details"]["request_content"])

    # Store the client & server data in a session for usage
    session['client_data'] = client_data
    session['server_data'] = server_data
    # Send client and server data back to the browser & the next route
    return jsonify(client_data=client_data, server_data=server_data)


# simulate_http_request
# Simulates an HTTP request, & subsequently retrieves information about the server and its response
# - Response content
# - Server ip
# - Server location
def simulate_http_request(request_url, request_method, request_content=None):
    # Retrieve response content
    try:
        if request_method == "POST":
            response = requests.post(request_url, data=request_content)
        else:
            response = requests.get(request_url)
    except Exception:
        abort(400, description="There was a problem with the request.")

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


# get_ip_details : [Maybe String] -> IP Details
# Retrieve the ip-related details associated with a particular _url_ or the local ip address
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
