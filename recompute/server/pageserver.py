import os
import flask
from . import config
from . import file


@config.recompute_app.route("/favicon.ico")
def favicon():
    return flask.send_from_directory(os.path.join(recompute_app.root_path, "static"), "favicon.ico",
                                     mimetype="image/vnd.microsoft.icon")


@config.recompute_app.route("/", methods=["GET"])
def index_page():
    from .forms import RecomputeForm
    recompute_form = RecomputeForm()

    recomputations_count = config.recomputations_count
    latest_recomputations = file.get_latest_recomputations_data()

    return flask.render_template("index.html", recompute_form=recompute_form, recomputations_count=recomputations_count,
                                 latest_recomputations=latest_recomputations)


@config.recompute_app.route("/recomputations", methods=["GET", "POST"])
def recomputations_page():
    from .forms import FilterRecomputationsForm
    filter_recomputation_form = FilterRecomputationsForm()

    all_recomputations = file.get_all_recomputations_data()

    if filter_recomputation_form.validate_on_submit():
        name = filter_recomputation_form.name.data
        if name != "":
            all_recomputations = [r for r in all_recomputations if r["name"] == name]
        if len(all_recomputations) == 0:
            flask.flash("Recomputation: " + name + " not found.", "danger")

    return flask.render_template("recomputations.html", filter_recomputation_form=filter_recomputation_form,
                                 all_recomputations=all_recomputations)


@config.recompute_app.route("/recomputation/<string:name>", methods=["GET"])
def recomputation_page(name):
    if not file.exists_recomputation(name):
        return flask.render_template("recomputation404.html", name=name)
    else:
        recomputation = file.get_recomputation_data(name)
        return flask.render_template("recomputation.html", recomputation=recomputation)


@config.recompute_app.route("/boxes", methods=["GET"])
def boxes_page():
    return flask.render_template("boxes.html")
