import os
import flask
from recompute.server import config as recompute_config
from recompute.server import io as recompute_io


@recompute_config.recompute_app.route("/favicon.ico")
def favicon():
    return flask.send_from_directory(os.path.join(recompute_config.recompute_app.root_path, "static"),
                                     "favicon.ico",
                                     mimetype="image/vnd.microsoft.icon")


@recompute_config.recompute_app.route("/", methods=["GET"])
def index_page():
    from .forms import RecomputeForm
    recompute_form = RecomputeForm()

    recomputations_count = recompute_config.recomputations_count
    latest_recomputations_summary = recompute_io.get_recomputations_summary(recompute_config.latest_count)

    return flask.render_template("index.html", recompute_form=recompute_form, recomputations_count=recomputations_count,
                                 latest_recomputations_summary=latest_recomputations_summary)


@recompute_config.recompute_app.route("/recomputations", methods=["GET", "POST"])
def recomputations_page():
    from .forms import FilterRecomputationsForm
    filter_recomputations_form = FilterRecomputationsForm()

    all_recomputations_summary = recompute_io.get_all_recomputations_summary()

    if filter_recomputations_form.validate_on_submit():
        name = filter_recomputations_form.name.data
        if name != "":
            all_recomputations_summary = [r for r in all_recomputations_summary if r["name"] == name]
        if len(all_recomputations_summary) == 0:
            flask.flash("Recomputation: " + name + " not found.", "danger")

    return flask.render_template("recomputations.html", filter_recomputations_form=filter_recomputations_form,
                                 all_recomputations_summary=all_recomputations_summary)


@recompute_config.recompute_app.route("/recomputation/<string:name>", methods=["GET"])
def recomputation_page(name):
    if not recompute_io.exists_recomputation(name):
        return flask.render_template("recomputation404.html", name=name)
    else:
        return flask.render_template("recomputation.html", recomputation=recompute_io.read_recomputefile(name))


@recompute_config.recompute_app.route("/boxes", methods=["GET"])
def boxes_page():
    from .forms import FilterBoxesForm
    filter_boxes_form = FilterBoxesForm()

    all_boxes = recompute_io.get_all_boxes_summary()

    if filter_boxes_form.validate_on_submit():
        language = filter_boxes_form.language.data
        if language != "":
            all_boxes = [box for box in all_boxes if box["language"] == language]
        if len(all_boxes) == 0:
            flask.flash("Language: " + all_boxes + " not found.", "danger")

    return flask.render_template("boxes.html", filter_boxes_form=filter_boxes_form, all_boxes=all_boxes)
