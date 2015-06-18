from flask import Flask
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.web import FallbackHandler, Application
from tornado.websocket import WebSocketHandler
from tornado.log import enable_pretty_logging

recompute_app = Flask(__name__)
recompute_app.config.from_object(__name__)
recompute_app.config["SECRET_KEY"] = "SECRET!"
recompute_app.debug = True

recompute_container = WSGIContainer(recompute_app)


class WebSocket(WebSocketHandler):
    def open(self):
        print "Socket opened."

    def on_message(self, message):
        self.write_message("Received: " + message)
        print "Received message: " + message


recompute_server = HTTPServer(Application([
    (r"/websocket/", WebSocket),
    (r".*", FallbackHandler, dict(fallback=recompute_container))
], debug=True))
enable_pretty_logging()

default_recomputefile = "recompute/server/software/recomputation.xml"

default_vagrantfile_dict = {
    "python": "recompute/server/languages/python/python.vconfig",
    "node_js": "recompute/server/languages/nodejs/nodejs.vconfig",
    "cpp": "recompute/server/languages/cpp/cpp.vconfig",
    "c++": "recompute/server/languages/cpp/cpp.vconfig",
    "c": "recompute/server/languages/cpp/cpp.vconfig"
}

default_language_install_dict = {
    "python": "pip install -r requirements.txt",
    "node_js": "npm install",
    "cpp": ["chmod +x configure", "./configure", "make", "sudo make install"],
    "c++": ["chmod +x configure", "./configure", "make", "sudo make install"],
    "c": ["chmod +x configure", "./configure", "make", "sudo make install"]
}

default_language_version_dict = {
    "python": "2.7",
    "node_js": "0.10",
    "cpp": "",
    "c++": "",
    "c": ""
}
