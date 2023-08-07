import flask
import json
from pathlib import Path
import streamlit_site as site

ROOT = site.app.config["ROOT"]

@site.app.route("/<streamlit_app_url>/")
def show_app(streamlit_app_url):
    apps = json.load(open(ROOT / Path("config.json"), "r"))["apps"]
    context = None
    for app, info in apps.items():
        if info["url"] == f"/{streamlit_app_url}/":
            context = {
                "name": info["name"],
                "port": info["port"]
            }
            break  # This will exit the loop once a match is found
    else:
        if context is None:
            return flask.abort(404)

    response = flask.make_response(flask.render_template("app.html", **context))
    # Setting the Content-Security-Policy header
    csp = ("frame-ancestors 'self' *.github.dev github.dev github.com; " 
        "frame-src 'self' *.github.dev github.dev; "
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data:; "
        "font-src 'self'; "
        "connect-src 'self';")

    response.headers['Content-Security-Policy'] = csp

    return response

