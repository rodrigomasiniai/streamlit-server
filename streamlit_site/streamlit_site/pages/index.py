import flask
import json
from pathlib import Path
import streamlit_site as site

ROOT = site.app.config["ROOT"]


@site.app.route("/")
def show_index():
    apps = json.load(open(ROOT / Path("config.json"), "r"))["apps"]
    status = json.load(open(
        ROOT / Path("streamlit_controls/status.json"), "r"))
    for name, vals in apps.items():
        if name not in status:
            vals["running"] = False
        vals["running"] = True if status[name]["pid"] else False
    context = {
        "apps": sorted(apps.values(), key=lambda x: x["name"])
    }
    response= flask.make_response(flask.render_template("index.html", **context))

        # Setting the Content-Security-Policy header for the index page too
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