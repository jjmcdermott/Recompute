import tornado.web
import tornado.gen

import io
import tasks


class Recompute(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def post(self):
        name = self.get_argument("recomputation")
        github_url = self.get_argument("github_url")
        box = self.get_argument("box")

        if io.exists_recomputation(name):
            self.reverse_url("index")

        status_code, err = yield tasks.recompute(name, github_url, box)

        if success:
            self.write("done")
            self.flush()


class EditRecomputation(tornado.web.RequestHandler):
    def get(self):
        self.finish("ok")
        # self.redirect(self.reverse_url("recomputation", name))


class UpdateRecomputation(tornado.web.RequestHandler):
    def post(self):
        name = self.get_argument("recomputation")
        github_url = self.get_argument("github_url")
        box = self.get_argument("box")

        if io.exists_recomputation(name):
            self.reverse_url("index")

        successful, msg = yield tasks.recompute(name, github_url, box)

        if successful:
            self.write("done")
            self.flush()


class DeleteRecomputation(tornado.web.RequestHandler):
    """
    Deletes the entire recomputation repository
    """

    def get(self, name):
        if io.exists_recomputation(name):
            io.destroy_recomputation(name)
            # flask.flash(name + " is removed", "warning")
        else:
            pass
            # flask.flash(name + " not found", "error")

        self.render("recomputation404.html", name=name)


class DownloadVM(tornado.web.RequestHandler):
    """
    Downloads the recomputation virtual machine with a particular tag and version
    """

    def get(self, name, tag, version):
        path = io.get_vm_path(name, tag, version)
        size = io.get_file_size(path)

        if path is None:
            self.clear()
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

    def get(self, name, tag, version):
        io.destroy_vm(name, tag, version)
        self.redirect(self.reverse_url("recomputation", name))


class DownloadLog(tornado.web.RequestHandler):
    """
    Downloads the latest recomputation log file
    """

    def get(self, name):
        path = io.get_latest_log_file(name)
        size = io.get_file_size(path)

        if path is None:
            self.clear()
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
