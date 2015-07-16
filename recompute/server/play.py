import logging
import os
import ptyprocess
import tornado.web
import tornado.websocket
import tornado.ioloop


class PlayWebSocket(tornado.websocket.WebSocketHandler):
    def initialize(self):
        self.session = PlayWebSocketSession(self)
        self.pty_fd = None
        self.log = logging.getLogger(__name__)

    def open(self):
        self.log.info("PlayWebSocket opened")
        self.pty_fd = self.session.handle_open()

    def on_message(self, message):
        self.session.handle_message(message, self.pty_fd)

    def on_close(self):
        pass

    def on_pty_read(self, data):
        self.write_message(data)


class PlayWebSocketSession(object):
    def __init__(self, socket):
        self.socket = socket
        self.ptys_by_fd = {}
        self.ioloop = tornado.ioloop.IOLoop.instance()

    def handle_open(self, opts=None, cols=80, rows=24):
        argv = ["bash"]
        env = os.environ.copy()
        env["TERM"] = "xterm"
        env["COLUMNS"] = str(cols)
        env["LINES"] = str(rows)
        pty = ptyprocess.PtyProcessUnicode.spawn(argv, env=env)
        self.ptys_by_fd[pty.fd] = pty
        self.ioloop.add_handler(pty.fd, self.pty_read, self.ioloop.READ)
        return pty.fd

    def handle_message(self, message, fd):
        self.ptys_by_fd[fd].write(message)

    def pty_read(self, fd, events=None):
        pty = self.ptys_by_fd[fd]
        data = pty.read(65536)
        self.socket.on_pty_read(data)
