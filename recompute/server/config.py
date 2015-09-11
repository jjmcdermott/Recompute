import os
import logging
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
uri_recomputation = r"/recomputation/(?P<name>[\w]+)$"

uri_recompute = r"/recompute"
uri_edit_recomputation = r"/recomputation/edit"
uri_update_recomputation = r"/recomputation/update/(?P<name>[\w]+)"
uri_delete_recomputation = r"/recomputation/delete/(?P<name>[\w]+)"
uri_download_vm = r"/vm/download/(?P<name>[\w]+)/(?P<tag>[\w]+)/(?P<version>[\d]+)"
uri_delete_vm = r"/vm/delete/(?P<name>[\w]+)/(?P<tag>[\w]+)/(?P<version>[\d]+)"
uri_download_log = r"/log/download/(?P<name>[\w]+)"

uri_socket_play = r"/ws/play/(?P<name>[\w]+)/(?P<tag>[\w]+)/(?P<version>[\d]+)"
uri_socket_recompute = r"/ws/recompute/(?P<name>[\w]+)"

# setting default values
latest_recomputations_count = 5
twenty_four_hours = 60 * 60 * 24
time_update_base_vms = twenty_four_hours
time_clean_up = twenty_four_hours
base_vms_list = list()
recomputation_sockets_dict = dict()


class RecomputeApp(tornado.web.Application):
    def __init__(self):
        handlers = [
            tornado.web.url(uri_static, tornado.web.StaticFileHandler),

            tornado.web.url(uri_index, pageserver.Index, name="index"),
            tornado.web.url(uri_recomputations, pageserver.Recomputations, name="recomputations"),
            tornado.web.url(uri_recomputation, pageserver.Recomputation, name="recomputation"),

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
        io.server_log_info("Starting server")
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


tornado.log.enable_pretty_logging()

app = RecomputeApp()
