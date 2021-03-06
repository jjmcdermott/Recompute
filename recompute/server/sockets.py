import logging
import os
import ptyprocess
import tornado.web
import tornado.websocket
import tornado.ioloop
import tornado.gen

import config
import io
import tasks


class PlayWebSocket(tornado.websocket.WebSocketHandler):
    def __init__(self, application, request, **kwargs):
        super(PlayWebSocket, self).__init__(application, request, **kwargs)
        self.name = None
        self.terminal = PlayTerminal(self)
        self.log = logging.getLogger(__name__)

    @tornado.gen.coroutine
    def open(self, name, tag, version):
        self.name = name
        self.terminal.handle_open(self.name, tag, version)
        self.log.info("Recomputation: {name} opened @ {ip} ".format(name=self.name, ip=self.request.remote_ip))

    def on_message(self, message):
        self.terminal.handle_message(message)

    @tornado.gen.coroutine
    def on_close(self):
        yield self.terminal.handle_close()
        self.log.info("Recomputation: {name} closed @ {ip} ".format(name=self.name, ip=self.request.remote_ip))

    def on_vagrant_init(self):
        self.write_message("\x1b[31mvagrant init (Initializing {}...)\x1b[m\r\n\n".format(self.name))

    def on_vagrant_up(self):
        self.write_message("\x1b[31mvagrant up (Starting {}...)\x1b[m\r\n\n".format(self.name))

    def on_vagrant_ssh(self):
        self.write_message("\x1b[31mvagrant ssh (SSH into {}...)\x1b[m\r\n\n".format(self.name))

    def on_pty_read(self, data):
        self.write_message(data)

    def on_pty_exit(self):
        self.close()


class PlayTerminal(object):
    def __init__(self, socket):
        self.socket = socket
        self.pty = None
        self.ioloop = tornado.ioloop.IOLoop.instance()
        self.recomputation = None
        self.recomputation_vm_dir = None

    @tornado.gen.coroutine
    def handle_open(self, name, tag, version):
        self.recomputation = name
        self.recomputation_vm_dir = io.get_recomputation_vm_dir(name, tag, version)

        async_recomputator = tasks.AsyncRecomputator(recomputation=name, cwd=self.recomputation_vm_dir)

        self.socket.on_vagrant_init()
        vagrant_init = "vagrant init {}.box".format(name)
        yield async_recomputator.run(category="Playing", command=vagrant_init)

        self.socket.on_vagrant_up()
        vagrant_up = "vagrant up"
        yield async_recomputator.run(category="Playing", command=vagrant_up)

        self.socket.on_vagrant_ssh()
        argv = "vagrant ssh".split()
        cwd = self.recomputation_vm_dir
        env = os.environ.copy()
        env["TERM"] = "xterm"
        self.pty = ptyprocess.PtyProcessUnicode.spawn(argv=argv, cwd=cwd, env=env, dimensions=(24, 80))
        self.ioloop.add_handler(self.pty.fd, self.pty_read, self.ioloop.READ)

    @tornado.gen.coroutine
    def handle_close(self):
        os.close(self.pty.fd)
        self.ioloop.remove_handler(self.pty.fd)
        self.pty.isalive()

        vagrant_halt = "vagrant halt"
        async_recomputator = tasks.AsyncRecomputator(recomputation=self.recomputation, cwd=self.recomputation_vm_dir)
        yield async_recomputator.run(category="Playing", command=vagrant_halt)

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

    def send_progress(self, message):
        self.write_message(message)

    def try_close(self):
        self.close()

    @classmethod
    def get_socket(cls, name):
        if name in config.recomputation_sockets_dict:
            return config.recomputation_sockets_dict[name]
        else:
            return None

    @classmethod
    def remove_socket(cls, name):
        if name in config.recomputation_sockets_dict:
            config.recomputation_sockets_dict[name].try_close()
            del config.recomputation_sockets_dict[name]
