import tornado.web
import tornado.gen

import io
import tasks
import forms


class Recompute(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def post(self):
        form = forms.RecomputeForm(self.request.arguments)
        if not form.validate():
            self.set_status(400)
            self.finish("Invalid request")

        name = form.recomputation.data
        github_url = form.github_url.data
        box = form.box.data

        if io.exists_recomputation(name):
            self.set_status(400)
            self.finish("Name '{}' already exists".format(name))

        status_code, err = yield tasks.recompute(name, github_url, box)

        if status_code:
            self.finish("Recomputed '{}'".format(name))
        else:
            self.set_status(500)
            log_link = "<a href={link}>Download log.</a>".format(link=self.reverse_url("download_log", name))
            vm_link = "<a href={link}>Download vm.</a>".format(link=self.reverse_url("delete_vm", name, "Latest", 0))
            self.finish("Failed to recompute '{name}'. {log}. {vm}.".format(name=name, log=log_link, vm=vm_link))


class EditRecomputation(tornado.web.RequestHandler):
    def initialize(self):
        self.form = forms.EditRecomputationForm(self.request.arguments)

    def get(self, name):
        recomputation = io.load_recomputation(name)
        self.render("edit_recomputation.html", edit_recomputation_form=self.form, recomputation=recomputation)

    def post(self, name):
        if self.form.validate():
            new_name = self.form.recomputation.data
            new_github_url = self.form.github_url.data
            new_description = self.form.description.data
            io.change_recomputation_github_url(name, new_github_url)
            io.change_recomputation_description(name, new_description)
            io.change_recomputation_name(name, new_name)
            self.finish("Recomputation '{}' edited".format(name))
        else:
            self.set_status(400)
            self.finish("Invalid request")


class UpdateRecomputation(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def post(self):
        name = self.get_argument("name")

        if not io.exists_recomputation(name):
            self.set_status(400)
            self.finish("{} not found".format(name))

        recompute_dict = io.load_recomputation(name)
        current_github_url = recompute_dict["github_url"]
        latest_box = recompute_dict["vms"][0]["box"]

        status_code, err = yield tasks.recompute(name, current_github_url, latest_box)

        if status_code:
            self.finish("Recomputation '{}' updated".format(name))
        else:
            self.set_status(500)
            self.finish("Failed to recompute '{name}'. <a href={link}>Download log.</a>".format(
                name=name, link=self.reverse_url("download_log", name)))


class DeleteRecomputation(tornado.web.RequestHandler):
    """
    Deletes the entire recomputation repository
    """

    def post(self):
        name = self.get_argument("name")

        if io.exists_recomputation(name):
            io.destroy_recomputation(name)
            self.finish("Recomputation '{}' removed".format(name))
        else:
            self.set_status(400)
            self.finish("{} not found".format(name))


class DownloadVM(tornado.web.RequestHandler):
    """
    Downloads the recomputation virtual machine with a particular tag and version
    """

    def get(self, name, tag, version):
        path = io.get_vm_path(name, tag, version)
        size = io.get_file_size(path)

        if path is None:
            self.set_status(404)
            self.finish("VM not found")
        else:
            self.set_header("Content-Type", "application/vnd.previewsystems.box")
            self.set_header("Content-Description", "VM")
            self.set_header("Content-Disposition", "attachment; filename={name}.box".format(name=name))
            self.set_header("Content-Length", size)

            with open(path, "rb") as f:
                while True:
                    data = f.read(16384)
                    if not data:
                        break
                    self.write(data)
                    self.flush()

            self.finish()


class DeleteVM(tornado.web.RequestHandler):
    """
    Deletes the recomputation virtual machine with a particular tag and version
    """

    def post(self, ):
        name = self.get_argument("name")
        tag = self.get_argument("tag")
        version = self.get_argument("version")

        if io.exists_vm(name, tag, version):
            io.destroy_vm(name, tag, version)
            self.finish("Recomputation '{name}' {tag}_{version} is removed".format(name=name, tag=tag, version=version))
        else:
            self.set_status(400)
            self.finish("Recomputation '{name}' {tag}_{version} not found".format(name=name, tag=tag, version=version))


class DownloadLog(tornado.web.RequestHandler):
    """
    Downloads the latest recomputation log file
    """

    def get(self, name):
        path = io.get_latest_log_file(name)
        size = io.get_file_size(path)

        if path is None:
            self.set_status(404)
            self.finish("Log file not found")
        else:
            self.set_header("Content-Type", "text/plain")
            self.set_header("Content-Description", "Log")
            self.set_header("Content-Disposition", "attachment; filename={name}.txt".format(name=name))
            self.set_header("Content-Length", size)

            with open(path, "rb") as f:
                while True:
                    data = f.read(16384)
                    if not data:
                        break
                    self.write(data)
                    self.flush()

            self.finish()
