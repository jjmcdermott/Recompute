import tornado.web

import forms
import config
import io


class Index(tornado.web.RequestHandler):
    """
    Returns the index page.
    """

    def get(self):
        form = forms.RecomputeForm()
        recomputations_count = io.get_recomputations_count()
        latest_recomputations = io.get_recomputations_summary(config.latest_recomputations_count)
        self.render("index.html", recompute_form=form, recomputations_count=recomputations_count,
                    latest_recomputations=latest_recomputations)


class Recomputations(tornado.web.RequestHandler):
    """
    Returns the recomputations/search page.
    """

    def get(self):
        form = forms.FilterRecomputationsForm()
        all_recomputations = io.get_all_recomputations_summary()

        if form.validate():
            name = form.name.data
            if name != "":
                all_recomputations = [r for r in all_recomputations if r["name"] == name]
            if len(all_recomputations) == 0:
                pass
                # flask.flash("Recomputation: " + name + " not found.", "danger")

        self.render("recomputations.html", filter_recomputations_form=form, all_recomputations=all_recomputations)


class Recomputation(tornado.web.RequestHandler):
    """
    Returns the individaul recomputation page.
    """

    def get(self, name):
        if not io.exists_recomputation(name):
            self.render("recomputation404.html", name=name)
        else:
            self.render("recomputation.html", recomputation=io.read_recomputefile(name))
