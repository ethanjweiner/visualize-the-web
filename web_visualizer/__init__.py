import os
import jsmin
import itertools
from flask import Flask, request, render_template, g
from flask_assets import Environment, Bundle
from flask_sqlalchemy import SQLAlchemy

# App configuration
app = Flask(__name__)

# Database setup
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data/points.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
import web_visualizer.routes
import web_visualizer.routers

# Bundling Javascript
assets = Environment(app)
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
    ip_db = getattr(g, '_database', None)
    if ip_db is not None:
        ip_db.close()


def resetDatabase():
    db.drop_all()
    db.create_all()
    db.session.commit()


resetDatabase()  # Try creating database here (else move outside)

