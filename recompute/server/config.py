from flask import Flask
from tornado.wsgi import WSGIContainer
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


recompute_server = Application([
    (r"/websocket/", WebSocket),
    (r".*", FallbackHandler, dict(fallback=recompute_container))
], debug=True)
enable_pretty_logging()

vagrant_config_dict = dict()
vagrant_config_dict["Python"] = "python.vagrant.config"
vagrant_config_dict["NodeJS"] = "nodejs.vagrant.config"
vagrant_config_dict["JavaScript"] = "nodejs.vagrant.config"

language_version_dict = dict()
language_version_dict["Python"] = "2.7"
language_version_dict["NodeJS"] = "0.10"
language_version_dict["JavaScript"] = "0.10"
