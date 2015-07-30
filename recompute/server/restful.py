import flask
from .config import recompute_app
from . import recompute
from . import file


@recompute_app.route("/recomputation/create", methods=["POST"])
def create_recomputation():
    from .forms import RecomputeForm
    recompute_form = RecomputeForm()

    if recompute_form.validate_on_submit():
        name = recompute_form.name.data
        github_url = recompute_form.github_url.data
        box = recompute_form.box.data

        if file.exists_recomputation(name):
            flask.flash("Recomputation already exists.", "danger")
            return flask.redirect(flask.url_for("index_page"))

        success, msg = recompute.create_vm(name, github_url, box)

        if success:
            path = file.get_vagrantbox_relative_path(name)
            return flask.send_file(path, mimetype="application/vnd.previewsystems.box", as_attachment=True)
        else:
            flask.flash("Recomputation was unsuccessful. " + msg, "danger")
            return flask.redirect(flask.url_for("index_page"))
    else:
        flask.flash("Recomputation was unsuccessful. Missing data.", "danger")
        return flask.redirect(flask.url_for("index_page"))


@recompute_app.route("/recomputation/edit/<name>", methods=["GET", ])
def edit_recomputation(name):
    pass


@recompute_app.route("/recomputation/rebuild/<name>", methods=["GET"])
def rebuild_recomputation(name):
    pass


@recompute_app.route("/recomputation/delete/<name>", methods=["GET"])
def delete_recomputation(name):
    recomputation = dict()
    recomputation["name"] = name

    if file.exists_recomputation(name):
        file.delete_recomputation(name)
        flask.flash(name + " is removed", "warning")
        flask.render_template("recomputation404.html", name=name)
    else:
        flask.flash(name + " not found", "error")
        flask.render_template("recomputation404.html", name=name)


@recompute_app.route("/vagrantfile/<name>", methods=["GET"])
def get_vagrantfile(name):
    path = file.get_vagrantfile_relative_path(name)
    if path is not None:
        return flask.send_file(path, mimetype="text/plain", as_attachment=True)
    else:
        return flask.jsonify(message="Vagrantfile found"), 400


@recompute_app.route("/vagrantbox/download/<name>", methods=["GET"])
def download_vagrantbox(name):
    path = file.get_vagrantbox_relative_path(name)
    if path is not None:
        return flask.send_file(path, mimetype="application/vnd.previewsystems.box", as_attachment=True)
    else:
        flask.flash("Recomputation: " + name + " not found.", "danger")
        flask.redirect(flask.url_for("index_page"))


@recompute_app.route("/vagrantbox/delete/<name>/<version>", methods=["POST"])
def delete_vagrantbox(name, version):
    pass
