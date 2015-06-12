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

vagrant_config_dict = {
    "Python": "python.vagrant.config",
    "NodeJS": "nodejs.vagrant.config",
    "JavaScript": "nodejs.vagrant.config"
}

language_version_dict = {
    "Python": "2.7",
    "NodeJS": "0.10",
    "JavaScript": "0.10"
}
