
from flask import request, jsonify, send_file
from .config import recompute_server
from .recompute import create_vm, get_all_vms

@recompute_server.route("/recompute/", methods=["GET"])
def recompute():
    """
    Recompute
    """

    try:
        hostname = request.args.get("hostname")
        github_url = request.args.get("github_url")
        path = create_vm(hostname, github_url)
        return send_file(path, mimetype="application/vnd.previewsystems.box", as_attachment=True)
    except KeyError:
        return jsonify(message="Invalid request"), 400

@recompute_server.route("/vms", methods=["GET"])
def get_all_vms():
    return jsonify(vms=get_all_vms())

@recompute_server.route("/vagrantfile", methods=["GET"])
def get_vagrantfile():
    pass
