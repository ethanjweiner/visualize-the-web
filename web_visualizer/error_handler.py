from werkzeug.exceptions import HTTPException
from web_visualizer import app
from flask import render_template, request, redirect, url_for


# Handle HTTP Exceptions
@app.errorhandler(HTTPException)
def handle_exception(error):
    return render_template("error.html", error=error)


@app.errorhandler(404)
def handle_exception_404(error):
    return render_template("error.html", error=error)


@app.errorhandler(500)
def handle_exception_500(error):
    return render_template("error.html", error=error)
