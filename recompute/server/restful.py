from flask import request, jsonify, send_file
from .config import recompute_app
from .recompute import Recomputation
from .file import find_vagrantfile_relative_path, find_vagrantbox_relative_path


@recompute_app.route("/recompute/", methods=["GET"])
def recompute():
    try:
        name = request.args.get("name")
        name = name.replace("_", "-").replace(" ", "-")
        github_url = request.args.get("github_url")
        base_vm = request.args.get("base_vm")

        if find_vagrantbox_relative_path(name) is not None:
            return jsonify(message="VM already exists"), 400

        success = Recomputation.create_vm(name, github_url, base_vm)
        if success:
            path = find_vagrantbox_relative_path(name)
            return send_file(path, mimetype="application/vnd.previewsystems.box", as_attachment=True)
        else:
            return jsonify(message="VM not created"), 500

    except KeyError:
        return jsonify(message="Invalid request"), 400


@recompute_app.route("/vagrantfile/<name>", methods=["GET"])
def get_vagrantfile(name):
    path = find_vagrantfile_relative_path(name)
    if path is not None:
        return send_file(path, mimetype="text/plain", as_attachment=True)
    else:
        return jsonify(message="Vagrantfile found"), 400


@recompute_app.route("/vagrantbox/<name>", methods=["GET"])
def get_vagrantbox(name):
    path = find_vagrantbox_relative_path(name)
    if path is not None:
        return send_file(path, mimetype="application/vnd.previewsystems.box", as_attachment=True)
    else:
        return jsonify(message="Vagrantbox not found"), 400
