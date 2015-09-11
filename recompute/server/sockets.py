import logging
import os
import ptyprocess
import tornado.web
import tornado.websocket
import tornado.ioloop

import config
import io


class PlayWebSocket(tornado.websocket.WebSocketHandler):
    def __init__(self, application, request, **kwargs):
        super(PlayWebSocket, self).__init__(application, request, **kwargs)
        self.name = None
        self.terminal = PlayTerminal(self)
        self.log = logging.getLogger(__name__)

    def open(self, name, tag, version):
        self.name = name
        self.terminal.handle_open(self.name, tag, version)
        self.log.info("Recomputation: {name} opened @ {ip} ".format(name=self.name, ip=self.request.remote_ip))

    def on_message(self, message):
        self.terminal.handle_message(message)

    def on_close(self):
        self.terminal.handle_close()
        self.log.info("Recomputation: {name} closed @ {ip} ".format(name=self.name, ip=self.request.remote_ip))

    def on_vagrant_init(self):
        self.write_message("\x1b[31mvagrant init (Initializing {}...)\x1b[m\r\n\n".format(self.name))

    def on_vagrant_up(self):
        self.write_message("\x1b[31mvagrant up (Starting {}...)\x1b[m\r\n\n".format(self.name))

    def on_vagrant_ssh(self):
        self.write_message("\x1b[31mvagrant ssh(SSH into {}...)\x1b[m\r\n\n".format(self.name))

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

    def handle_open(self, name, tag, version):
        self.recomputation_build_dir = io.get_recomputation_build_dir(name, tag, version)

        self.socket.on_vagrant_init()
        io.execute(["vagrant", "init", name], self.recomputation_build_dir)

        self.socket.on_vagrant_up()
        io.execute(["vagrant", "up"], self.recomputation_build_dir)

        self.socket.on_vagrant_ssh()
        argv = ["vagrant", "ssh"]
        cwd = self.recomputation_build_dir
        env = os.environ.copy()
        env["TERM"] = "xterm"
        self.pty = ptyprocess.PtyProcessUnicode.spawn(argv=argv, cwd=cwd, env=env, dimensions=(24, 80))
        self.ioloop.add_handler(self.pty.fd, self.pty_read, self.ioloop.READ)

    def handle_close(self):
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


class RecomputeSocket(tornado.websocket.WebSocketHandler):
    def __init__(self, application, request, **kwargs):
        super(RecomputeSocket, self).__init__(application, request, **kwargs)
        self.name = None

    def open(self, name):
        self.name = name
        config.recomputation_sockets_dict[name] = self

    def on_message(self, message):
        pass

    def on_close(self):
        del config.recomputation_sockets_dict[self.name]

    def send_progress(self, message):
        self.write_message(message)

    def send_close(self):
        self.close()

    @classmethod
    def get_socket(cls, name):
        if name in config.recomputation_sockets_dict:
            return config.recomputation_sockets_dict[name]
        else:
            return None
