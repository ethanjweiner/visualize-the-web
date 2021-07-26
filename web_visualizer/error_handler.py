from werkzeug.exceptions import HTTPException
from web_visualizer import app
from flask import render_template, request, redirect, url_for, jsonify


# Handle HTTP Exceptions
@app.errorhandler(HTTPException)
def handle_exception(error):
    return jsonify(error)


@app.errorhandler(404)
def handle_exception_404(error):
    return render_template("error.html", error=error)


@app.errorhandler(400)
def handle_exception_400(error):
    return render_template("error.html", error=error)
