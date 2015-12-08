import os
import logging
import threading
import signal
import tornado.httpserver
import tornado.log
import tornado.ioloop
import tornado.web

import sockets
import restful
import pageserver
import io

# setting uri
uri_static = r"/static/(.*)"

uri_index = r"/"
uri_recomputations = r"/recomputations"
uri_recomputation = r"/recomputation/name/(?P<name>[\w]+)"
uri_recomputation_by_id = r"/recomputation/id/(?P<name>[0-9]+)"
uri_software = r"/software"
uri_landing = r"/landing/(?P<name>[\w]+)"
uri_requestdoi = r"/requestdoi/(?P<name>[\w]+)"

uri_recompute = r"/recompute"
uri_edit_recomputation = r"/edit/recomputation/(?P<name>[\w]+)"
uri_update_recomputation = r"/update/recomputation"
uri_delete_recomputation = r"/delete/recomputation"
uri_download_vm = r"/download/vm/(?P<name>[\w]+)/(?P<tag>[\w]+)/(?P<version>[\d]+)"
uri_delete_vm = r"/delete/vm"
uri_download_log = r"/download/log/(?P<name>[\w]+)"

uri_socket_play = r"/ws/play/(?P<name>[\w]+)/(?P<tag>[\w]+)/(?P<version>[\d]+)"
uri_socket_recompute = r"/ws/recompute/(?P<name>[\w]+)"

# setting default values
latest_recomputations_count = 5
twenty_four_hours = 60 * 60 * 24
time_update = twenty_four_hours
base_vms_dict = list()
recomputation_sockets_dict = dict()


class RecomputeApp(tornado.web.Application):
    def __init__(self):
        handlers = [
            tornado.web.url(uri_static, tornado.web.StaticFileHandler),

            tornado.web.url(uri_index, pageserver.Index, name="index"),
            tornado.web.url(uri_recomputations, pageserver.Recomputations, name="recomputations"),
            tornado.web.url(uri_recomputation, pageserver.Recomputation, name="recomputation"),
            tornado.web.url(uri_recomputation_by_id, pageserver.Recomputation, name="recomputation_by_id"),
            tornado.web.url(uri_software, pageserver.Software, name="software"),
            tornado.web.url(uri_landing, pageserver.Landing, name="landing"),

            tornado.web.url(uri_requestdoi, restful.Request, name="requestdoi"),
            tornado.web.url(uri_recompute, restful.Recompute, name="recompute"),
            tornado.web.url(uri_edit_recomputation, restful.EditRecomputation, name="edit_recomputation"),
            tornado.web.url(uri_update_recomputation, restful.UpdateRecomputation, name="update_recomputation"),
            tornado.web.url(uri_delete_recomputation, restful.DeleteRecomputation, name="delete_recomputation"),
            tornado.web.url(uri_download_vm, restful.DownloadVM, name="download_vm"),
            tornado.web.url(uri_delete_vm, restful.DeleteVM, name="delete_vm"),
            tornado.web.url(uri_download_log, restful.DownloadLog, name="download_log"),

            tornado.web.url(uri_socket_play, sockets.PlayWebSocket),
            tornado.web.url(uri_socket_recompute, sockets.RecomputeSocket)
        ]

        settings = {
            "static_path": os.path.join(os.path.dirname(__file__), "static"),
            "template_path": os.path.join(os.path.dirname(__file__), "templates"),
            "autoescape": None,
            "autoreload": False,
            "debug": True
        }

        tornado.web.Application.__init__(self, handlers, **settings)

        self.is_closing = False
        self.http_server = tornado.httpserver.HTTPServer(self)

    def start(self, host, port):
        io.server_log_info("Initializing")
        self.initialize()

        io.server_log_info("Server started @ {host}:{port}".format(host=host, port=port))
        self.http_server.bind(address=host, port=port)
        self.http_server.start()
        signal.signal(signal.SIGINT, self.signal_handler)
        tornado.ioloop.PeriodicCallback(self.try_exit, 100).start()
        tornado.ioloop.IOLoop.instance().start()

    def signal_handler(self, signum, frame):
        self.is_closing = True
        logging.info('Exiting...')

    def try_exit(self):
        if self.is_closing:
            tornado.ioloop.IOLoop.instance().stop()
            logging.info('Exit success')

    def initialize(self):
        io.create_recomputations_dir()
        io.create_logs_dir()
        self.update()

    def update(self):
        global time_update
        global base_vms_dict

        t = threading.Timer(time_update, self.update)
        t.daemon = True
        t.start()

        base_vms_dict = io.update_base_vms()
        io.remove_failed_recomputations()
        io.remove_old_logs()


tornado.log.enable_pretty_logging()

app = RecomputeApp()
