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
        latest_recomputations = io.load_all_recomputations(config.latest_recomputations_count)
        self.render("index.html", recompute_form=form, recomputations_count=recomputations_count,
                    latest_recomputations=latest_recomputations)


class Recomputations(tornado.web.RequestHandler):
    """
    Returns the recomputations/search page.
    """

    def initialize(self):
        self.form = forms.FilterRecomputationsForm(self.request.arguments)
        self.recomputations = io.load_all_recomputations()

    def get(self):
        self.render("recomputations.html", filter_recomputations_form=self.form, recomputations=self.recomputations)

    def post(self):
        if self.form.validate():
            print "here"
            name = self.form.name.data
            if name != "":
                print name
                self.recomputations = [r for r in self.recomputations if r["name"] == name]

        self.render("recomputations.html", filter_recomputations_form=self.form, recomputations=self.recomputations)


class Recomputation(tornado.web.RequestHandler):
    """
    Returns the individual recomputation page.
    """

    def get(self, name):
        if name.isdigit():
            recomputation = io.load_recomputation_by_id(int(name))
        else:
            recomputation = io.load_recomputation(name)

        if recomputation is not None:
            self.render("recomputation.html", recomputation=recomputation)
        else:
            self.render("recomputation404.html", name=name)

class testMachine(tornado.web.RequestHandler):
    """
    Returns an individual test recomputation page.
    """

    def get(self, name):
        if name.isdigit():
            recomputation = io.load_recomputation_by_id(int(name))
        else:
            recomputation = io.load_recomputation(name)

        if recomputation is not None:
            self.render("test_machine.html", recomputation=recomputation)
        else:
            self.render("recomputation404.html", name=name)

class Jtest(tornado.web.RequestHandler):
    """
    Returns the John test page.
    """

    def initialize(self):
        self.form = forms.FilterRecomputationsForm(self.request.arguments)
        self.recomputations = io.load_all_recomputations()

    def get(self):
        self.render("test.html", filter_recomputations_form=self.form, recomputations=self.recomputations)

    def post(self):
        if self.form.validate():
            print "here"
            name = self.form.name.data
            if name != "":
                print name
                self.recomputations = [r for r in self.recomputations if r["name"] == name]

        self.render("test.html", filter_recomputations_form=self.form, recomputations=self.recomputations)
