import re
import flask
from . import config
from . import recompute
from . import io


@config.recompute_app.route("/recomputation/create", methods=["POST"])
def create_recomputation():
    from .forms import RecomputeForm
    recompute_form = RecomputeForm()

    if recompute_form.validate_on_submit():
        name = recompute_form.name.data
        name = re.sub(r"[^a-zA-Z0-9 \n\.]", "-", name)  # replace symbols with underscores
        github_url = recompute_form.github_url.data
        box = recompute_form.box.data

        if io.exists_recomputation(name):
            flask.flash("Recomputation already exists.", "danger")
            return flask.redirect(flask.url_for("index_page"))

        successful, msg = recompute.create_vm(name, github_url, box)

        if successful:
            return flask.send_file(io.get_vagrantbox_relative(name), mimetype="application/vnd.previewsystems.box",
                                   as_attachment=True)
        else:
            flask.flash("Recomputation was unsuccessful. " + msg, "danger")
            return flask.redirect(flask.url_for("index_page"))
    else:
        flask.flash("Recomputation was unsuccessful. Missing data.", "danger")
        return flask.redirect(flask.url_for("index_page"))


@config.recompute_app.route("/recomputation/edit/<name>", methods=["GET"])
def edit_recomputation(name):
    return flask.redirect(flask.url_for("recomputation_page", name=name))


@config.recompute_app.route("/recomputation/rebuild/<name>", methods=["GET"])
def update_recomputation(name):
    return flask.redirect(flask.url_for("recomputation_page", name=name))


@config.recompute_app.route("/recomputation/delete/<name>", methods=["GET"])
def delete_recomputation(name):
    recomputation = dict()
    recomputation["name"] = name

    if io.exists_recomputation(name):
        io.destroy_recomputation(name)
        flask.flash(name + " is removed", "warning")
        flask.render_template("recomputation404.html", name=name)
    else:
        flask.flash(name + " not found", "error")
        flask.render_template("recomputation404.html", name=name)


@config.recompute_app.route("/vagrantbox/download/<name>", methods=["GET"])
def download_vagrantbox(name):
    path = io.get_vagrantbox_relative(name)
    if path is not None:
        return flask.send_file(path, mimetype="application/vnd.previewsystems.box", as_attachment=True)
    else:
        flask.flash("Recomputation: " + name + " not found.", "danger")
        return flask.redirect(flask.url_for("index_page"))


@config.recompute_app.route("/vagrantbox/delete/<name>", methods=["GET"])
def delete_vagrantbox(name):
    return flask.redirect(flask.url_for("recomputation_page", name=name))
