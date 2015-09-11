import tornado.web
import tornado.gen

import io
import tasks
import forms


class Recompute(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def post(self):
        name = self.get_argument("recomputation")
        github_url = self.get_argument("github_url")
        box = self.get_argument("box")

        form = forms.RecomputeForm(self.request.arguments)
        if not form.validate():
            self.set_status(400)
            self.finish("Invalid request")

        if io.exists_recomputation(name):
            self.set_status(400)
            self.finish("Name already exists")

        status_code, err = yield tasks.recompute(name, github_url, box)

        if status_code:
            self.finish("Recomputed {}".format(name))
        else:
            self.set_status(500)
            self.finish("Recomputation failed")


class EditRecomputation(tornado.web.RequestHandler):
    def get(self, name):
        self.redirect(self.reverse_url("recomputation", name))


class UpdateRecomputation(tornado.web.RequestHandler):
    def post(self):
        name = self.get_argument("recomputation")
        newest_vm = io.get_newest_vm(name)

        status_code, err = yield tasks.recompute(name, newest_vm["github_url"], newest_vm["box"])

        if status_code:
            newest_vm = io.get_newest_vm(name)
            self.finish(self.reverse_url("download_vm", name, newest_vm["tag"], newest_vm["version"]))
        else:
            self.set_status(500)
            self.finish("Recomputation failed")


class DeleteRecomputation(tornado.web.RequestHandler):
    """
    Deletes the entire recomputation repository
    """

    def post(self):
        name = self.get_argument("recomputation")
        if io.exists_recomputation(name):
            io.destroy_recomputation(name)
            self.finish("{} is removed".format(name))
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

    def post(self, name, tag, version):
        name = self.get_argument("recomputation")
        tag = self.get_argument("tag")
        version = self.get_argument("version")

        if io.exists_vm(name, tag, version):
            io.destroy_vm(name, tag, version)
            self.finish("{name} {tag}_{version} is removed".format(name=name, tag=tag, version=version))
        else:
            self.set_status(400)
            self.finish("{name} {tag}_{version} not found".format(name=name, tag=tag, version=version))


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
