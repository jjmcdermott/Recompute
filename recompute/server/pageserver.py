
from config import recompute_server
from flask import render_template as f_render_template

@recompute_server.route("/", methods=["GET"])
@recompute_server.route("/index", methods=["GET"])
def get_index():
    return f_render_template("index.html")
