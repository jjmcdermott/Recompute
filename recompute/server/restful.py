
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
        path = create_vm(hostname, github_url)
        if path is not None:
            return hostname
            # return send_file(path, mimetype="application/vnd.previewsystems.box", as_attachment=True)
        else:
            return jsonify(message="Internal error"), 400
    except KeyError:
        return jsonify(message="Invalid request"), 400

@recompute_server.route("/machines", methods=["GET"])
def get_all_vms():
    pass
