import logging
import os
import ptyprocess
import tornado.web
import tornado.websocket
import tornado.ioloop
from .config import recompute_app


class PlayWebSocket(tornado.websocket.WebSocketHandler):
    def __init__(self, application, request, **kwargs):
        super(PlayWebSocket, self).__init__(application, request, **kwargs)
        self.terminal = PlayTerminal(self)
        self.recomputation_name = None
        self.log = logging.getLogger(__name__)

    def open(self, recomputation_name):
        self.recomputation_name = recomputation_name
        self.terminal.handle_open(self.recomputation_name)
        self.write_message("\x1b[31mRecomputation: {}!\x1b[m\r\n\n".format(self.recomputation_name))
        self.log.info("Recomputation: {} opened @ {} ".format(self.recomputation_name, self.request.remote_ip))

    def on_message(self, message):
        self.terminal.handle_message(message)

    def on_close(self):
        self.terminal.handle_close()
        self.log.info("Recomputation: {} closed @ {} ".format(self.recomputation_name, self.request.remote_ip))

    def on_pty_read(self, data):
        self.write_message(data)

    def on_pty_exit(self):
        self.close()


class PlayTerminal(object):
    def __init__(self, socket):
        self.socket = socket
        self.pty = None
        self.ioloop = tornado.ioloop.IOLoop.instance()

    def handle_open(self, recomputation_name):
        argv = ["vagrant", "ssh"]
        cwd = os.path.join(recompute_app.root_path, "recomputations", recomputation_name, "vm")
        env = os.environ.copy()
        env["TERM"] = "xterm"
        self.pty = ptyprocess.PtyProcessUnicode.spawn(argv=argv, cwd=cwd, env=env, dimensions=(24, 80))
        self.ioloop.add_handler(self.pty.fd, self.pty_read, self.ioloop.READ)

    def handle_close(self):
        self.ioloop.remove_handler(self.pty.fd)
        os.close(self.pty.fd)
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
