
import os
from flask import request, jsonify, send_file
from .config import recompute_server
from .recompute import create_vm

@recompute_server.route("/recompute/", methods=["GET"])
def recompute():
    """
    Recompute
    """

    try:
        hostname = request.args.get("hostname")
        github_url = request.args.get("github_url")
        base_vm = request.args.get("base_vm")
        path = create_vm(hostname, github_url, base_vm)
        return send_file(path, mimetype="application/vnd.previewsystems.box", as_attachment=True)
    except KeyError:
        return jsonify(message="Invalid request"), 400


@recompute_server.route("/download/<hostname>", methods=["GET"])
def download():
    pass


@recompute_server.route("/vagrantfile/<hostname>", methods=["GET"])
def get_vagrantfile(hostname):
    """
    """

    pass
