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
        latest_recomputations = io.get_all_recomputations_summary(config.latest_recomputations_count)
        self.render("index.html", recompute_form=form, recomputations_count=recomputations_count,
                    latest_recomputations=latest_recomputations)


class Recomputations(tornado.web.RequestHandler):
    """
    Returns the recomputations/search page.
    """
    def initialize(self):
        self.form = forms.FilterRecomputationsForm()
        self.recomputations = io.get_all_recomputations_summary()

    def get(self):
        self.render("recomputations.html", filter_recomputations_form=self.form, recomputations=self.recomputations)

    def post(self):
        if self.form.validate():
            name = self.form.name.data
            if name != "":
                self.recomputations = [r for r in self.recomputations if r["name"] == name]

        self.render("recomputations.html", filter_recomputations_form=self.form, recomputations=self.recomputations)


class Recomputation(tornado.web.RequestHandler):
    """
    Returns the individaul recomputation page.
    """

    def get(self, name):
        if not io.exists_recomputation(name):
            self.render("recomputation404.html", name=name)
        else:
            self.render("recomputation.html", recomputation=io.get_recomputation(name))
