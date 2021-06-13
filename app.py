import os
import jsmin
import csv
from flask import Flask, jsonify, request, render_template
from flask_assets import Environment, Bundle

# IP-related imports:
# import socket
# import ipinfo

# An IPCoordinate is a dictionary:
# {
#   ip: String
#   latitude: Number
#   longitude: Number
# }

app = Flask(__name__)
assets = Environment(app)

# Bundle javascript files into minified "bundle.js"
js = Bundle('js/jquery.min.js', 'js/store.js', 'js/animation.js', 'js/helpers.js', 'js/index.js',
            filters='jsmin', output='bundle.js')
assets.register('js_all', js)

# CONSTANTS
KEY = "AIzaSyCCl7-ieDSLRydryyQ1JaypI_dKuBhqfOc"
TOTAL_IP_ADDRESSES = 60000


# ROUTES

# Index: Displays a static map on load
@app.route("/")
def index():
    return render_template("index.html", key=KEY)


# Routers: Generates GeoJSON locations of _num_routers_ routers
@app.route("/routers")
def routers():
    # 1. Clear routers.db

    # 2. Update routers.db with new coordinates

    num_routers = int(request.args.get("num_routers"))

    with open('data/ip_addresses.csv') as ip_addresses:
        ip_addresses_reader = csv.DictReader(ip_addresses)
        rows = list(ip_addresses_reader)
        for i in range(0, num_routers):
            print(i)
            # Retrieve a random IPCoordinate from the database
            # Store this coordinate in routers.db

    return jsonify("Routers")


# Animate: Sends the request asynchronously, and runs an animation
@ app.route("/animate")
def animate():
    # Run the AJAX request
    requestData = request.args.get("request_data")

    # Provide the response data to the template
    return jsonify("animate")


# Run app
if __name__ == "__main__":
    app.run()
