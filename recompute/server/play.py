import logging
import os
import ptyprocess
import tornado.web
import tornado.websocket
import tornado.ioloop


class PlayWebSocket(tornado.websocket.WebSocketHandler):
    def __init__(self, application, request, **kwargs):
        super(PlayWebSocket, self).__init__(application, request, **kwargs)
        self.terminal = PlayTerminal(self)
        self.name = None
        self.log = logging.getLogger(__name__)

    def on_vagrant_init(self):
        self.write_message("\x1b[31mInitializing {}...\x1b[m\r\n\n".format(self.name))

    def on_vagrant_up(self):
        self.write_message("\x1b[31mStarting {}...\x1b[m\r\n\n".format(self.name))

    def on_vagrant_ssh(self):
        self.write_message("\x1b[31mSSH into {}...\x1b[m\r\n\n".format(self.name))

    def open(self, name):
        self.name = name
        self.terminal.handle_open(self.name)
        self.log.info("Recomputation: {name} opened @ {ip} ".format(name=self.name, ip=self.request.remote_ip))

    def on_message(self, message):
        self.terminal.handle_message(message)

    def on_close(self):
        self.terminal.handle_close()
        self.log.info("Recomputation: {name} closed @ {ip} ".format(name=self.name, ip=self.request.remote_ip))

    def on_pty_read(self, data):
        self.write_message(data)

    def on_pty_exit(self):
        self.close()


class PlayTerminal(object):
    def __init__(self, socket):
        self.socket = socket
        self.pty = None
        self.ioloop = tornado.ioloop.IOLoop.instance()
        self.recomputation_build_dir = None

    def handle_open(self, name, tag="Latest", version="0"):
        from . import config
        from . import io

        self.recomputation_build_dir = io.get_recomputation_build_dir(name, tag, version)

        self.socket.on_vagrant_init()
        io.execute(["vagrant", "init", name], self.recomputation_build_dir)

        self.socket.on_vagrant_up()
        io.execute(["vagrant", "up"], self.recomputation_build_dir)

        self.socket.on_vagrant_ssh()
        argv = ["vagrant", "ssh"]
        cwd = os.path.join(config.recompute_app.root_path,
                           "recomputations/{name}/vms/{tag}_{version}".format(name=name, tag=tag, version=version))
        env = os.environ.copy()
        env["TERM"] = "xterm"
        self.pty = ptyprocess.PtyProcessUnicode.spawn(argv=argv, cwd=cwd, env=env, dimensions=(24, 80))
        self.ioloop.add_handler(self.pty.fd, self.pty_read, self.ioloop.READ)

    def handle_close(self):
        from . import io
        io.execute(["vagrant", "halt"], self.recomputation_build_dir)

        os.close(self.pty.fd)
        self.ioloop.remove_handler(self.pty.fd)
        self.pty.isalive()

    def handle_message(self, message):
        self.pty.write(message)

    def handle_resize(self):
        pass

    def pty_read(self, fd, events):
        try:
            data = self.pty.read(65536)
            self.socket.on_pty_read(data)
        except EOFError:
            self.socket.on_pty_exit()
