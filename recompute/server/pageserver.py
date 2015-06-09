
from flask import render_template as render_template
from .config import recompute_server

@recompute_server.route("/", methods=["GET"])
@recompute_server.route("/index", methods=["GET"])
def get_index():
    return render_template("index.html", virtual_machines=list())
