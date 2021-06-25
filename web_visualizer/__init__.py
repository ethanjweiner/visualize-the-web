import os
import jsmin
import itertools
from flask import Flask, request, render_template, g
from flask_assets import Environment, Bundle


# IP-related imports:
# import socket
# import ipinfo

# App configuration
app = Flask(__name__)
assets = Environment(app)

import web_visualizer.routers
import web_visualizer.routes


# Bundle javascript files into minified "bundle.js"
js = Bundle('js/jquery.min.js', 'js/store.js', 'js/animation.js', 'js/helpers.js', 'js/index.js',
            filters='jsmin', output='bundle.js')
assets.register('js_all', js)

# CONSTANTS
KEY = "AIzaSyCCl7-ieDSLRydryyQ1JaypI_dKuBhqfOc"


# Index: Displays a static map on load
@app.route("/")
def index():
    return render_template("index.html", key=KEY)


# close_connection
# Closes the database when finished
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


# Run app
if __name__ == "__main__":
    app.run(debug=True)
