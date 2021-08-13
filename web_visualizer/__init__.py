from flask import Flask, request, render_template, g, abort, redirect
from flask_assets import Environment, Bundle
from flask_sqlalchemy import SQLAlchemy

import json
import os
import jsmin
import itertools

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data/points.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Optional Profiling

# from werkzeug.middleware.profiler import ProfilerMiddleware
# app.config['PROFILE'] = True
# app.wsgi_app = ProfilerMiddleware(
#     app.wsgi_app, restrictions=[10])

import web_visualizer.py_main.route  # nopep8
import web_visualizer.py_main.request  # nopep8
import web_visualizer.py_main.routers  # nopep8
import web_visualizer.py_auxiliary.error_handler  # nopep8
import web_visualizer.py_auxiliary.helpers  # nopep8
from web_visualizer.py_auxiliary.config import *  # nopep8

app.config['SECRET_KEY'] = SECRET_KEY

# Bundling Javascript
assets = Environment(app)
js = Bundle('js/jquery.min.js', 'js/globals.js', 'js/animation.js', 'js/helpers.js', 'js/init_display.js', 'js/index.js',
            filters='jsmin', output='bundle.js')
assets.register('js_all', js)


# Index: Displays a static map on load
@app.route("/")
def index():
    return render_template("index.html", key=API_KEY)


# Error: Provides an HTML template for an error handler
@app.route("/error")
def error():
    return render_template("error.html", error=error)


# close_connection
# Closes the IP database when finished
@app.teardown_appcontext
def close_connection(exception):
    ip_db = getattr(g, '_database', None)
    if ip_db is not None:
        ip_db.close()


# Create database if not yet created
db.create_all()
db.session.commit()
