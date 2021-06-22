from web_visualizer import app

# Animate: Sends the request asynchronously, and runs an animation


@app.route("/animate")
def animate():
    # Run the AJAX request
    requestData = request.args.get("request_data")

    # Provide the response data to the template
    return jsonify("animate")
