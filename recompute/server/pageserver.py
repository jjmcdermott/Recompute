
import os
from flask import render_template as render_template
from .config import recompute_server

@recompute_server.route("/", methods=["GET"])
@recompute_server.route("/index", methods=["GET"])
def get_index():
    vms = list()
    for hostname in next(os.walk("recompute/server/vms/"))[1]:
        vms.append({"hostname": hostname})
    print vms
    return render_template("index.html", vms=vms)


@recompute_server.route("/tty", methods=["GET"])
def get_tty():
    return render_template("tty.html")
