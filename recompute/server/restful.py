import re
import flask
from recompute.server import config as recompute_config
from recompute.server import io as recompute_io
from recompute.server import tasks as recompute_tasks


@recompute_config.recompute_app.route("/recomputation/create", methods=["POST"])
def create_recomputation():
    from .forms import RecomputeForm
    recompute_form = RecomputeForm()

    if recompute_form.validate_on_submit():
        name = recompute_form.name.data
        name = re.sub(r"[^a-zA-Z0-9 \n\.]", "_", name)  # replace symbols with underscores
        github_url = recompute_form.github_url.data
        box = recompute_form.box.data

        if recompute_io.exists_recomputation(name):
            flask.flash("Recomputation already exists.", "danger")
            return flask.redirect(flask.url_for("index_page"))

        successful, msg = recompute_tasks.create_vm(name, github_url, box)
        # task = recompute_tasks.

        if successful:
            flask.flash("Successful recomputation.", "success")
            return flask.send_file(recompute_io.get_vagrantbox_relative(name, "Latest", "0"),
                                   mimetype="application/vnd.previewsystems.box", as_attachment=True)
        else:
            error_message = "Unsuccessful recomputation: {msg} <a href='{url}'>Download log</a>.".format(
                msg=msg, url=flask.url_for("download_log_file", name=name)
            )
            flask.flash(flask.Markup(error_message), "danger")
            return flask.redirect(flask.url_for("index_page"))
    else:
        flask.flash("Unsuccessful recomputation. Missing data.", "danger")
        return flask.redirect(flask.url_for("index_page"))


@recompute_config.recompute_app.route("/recomputation/edit/<name>", methods=["GET"])
def edit_recomputation(name):
    return flask.redirect(flask.url_for("recomputation_page", name=name))


@recompute_config.recompute_app.route("/recomputation/update/<name>", methods=["GET"])
def update_recomputation(name):
    recompute_dict = recompute_io.read_recomputefile(name)
    recompute_tasks.update_vm(name, recompute_dict["github_url"], recompute_dict["releases"][0]["box"])
    return flask.redirect(flask.url_for("recomputation_page", name=name))


@recompute_config.recompute_app.route("/recomputation/delete/<name>", methods=["GET"])
def delete_recomputation(name):
    recomputation = dict()
    recomputation["name"] = name

    if recompute_io.exists_recomputation(name):
        recompute_io.destroy_recomputation(name)
        flask.flash(name + " is removed", "warning")
        flask.render_template("recomputation404.html", name=name)
    else:
        flask.flash(name + " not found", "error")
        flask.render_template("recomputation404.html", name=name)


@recompute_config.recompute_app.route("/vagrantbox/download/<name>/<tag>/<version>", methods=["GET"])
def download_vagrantbox(name, tag, version):
    path = recompute_io.get_vagrantbox_relative(name, tag, version)
    if path is not None:
        return flask.send_file(path, mimetype="application/vnd.previewsystems.box", as_attachment=True)
    else:
        flask.flash("Recomputation: {name} not found.".format(name=name), "danger")
        return flask.redirect(flask.url_for("index_page"))


@recompute_config.recompute_app.route("/vagrantbox/delete/<name>/<tag>/<version>", methods=["GET"])
def delete_vagrantbox(name, tag, version):
    recompute_io.destroy_build(name, tag, version)
    return flask.redirect(flask.url_for("recomputation_page", name=name))


@recompute_config.recompute_app.route("/log/<name>", methods=["GET"])
def download_log_file(name):
    path = recompute_io.get_latest_log_file(name)
    if path is not None:
        return flask.send_file(path, mimetype="text/plain", as_attachment=True)
    else:
        flask.flash("Log file for recomputation: {name} not found.".format(name, name), "danger")
        return flask.redirect(flask.url_for("index_page"))
