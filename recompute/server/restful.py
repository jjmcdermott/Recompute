import os
from flask import request, jsonify, send_file
from .config import recompute_app
from .recompute import create_vm


@recompute_app.route("/recompute/", methods=["GET"])
def recompute():
    """
    Recompute
    """

    try:
        hostname = request.args.get("hostname")

        project_dir = "recompute/server/vms/" + hostname + "/"
        vagrantbox_path = project_dir + hostname + ".box"
        if os.path.exists(project_dir) and os.path.isfile(vagrantbox_path):
            return jsonify(message="VM already exists"), 400

        github_url = request.args.get("github_url")
        base_vm = request.args.get("base_vm")
        relative_vagrantbox_path = create_vm(hostname, github_url, base_vm)
        if relative_vagrantbox_path is None:
            return jsonify(message="VM not created"), 500
        else:
            return send_file(relative_vagrantbox_path,
                             mimetype="application/vnd.previewsystems.box", as_attachment=True)

    except KeyError:
        return jsonify(message="Invalid request"), 400


@recompute_app.route("/download/<hostname>", methods=["GET"])
def download(hostname):
    """
    Download the virtual machine
    """

    project_dir = "recompute/server/vms/" + hostname + "/"
    vagrantbox_path = project_dir + hostname + ".box"
    relative_vagrantbox_path = "vms/" + hostname + "/" + hostname + ".box"

    if os.path.exists(project_dir) and os.path.isfile(vagrantbox_path):
        return send_file(relative_vagrantbox_path, mimetype="application/vnd.previewsystems.box", as_attachment=True)
    else:
        return jsonify(message="VM not found"), 400

@recompute_app.route("/vagrantfile/<hostname>", methods=["GET"])
def get_vagrantfile(hostname):
    """
    """

    pass
