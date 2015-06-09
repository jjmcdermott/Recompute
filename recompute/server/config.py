
from flask import Flask
from flask_socketio import SocketIO

recompute_server = Flask(__name__)
recompute_server.config.from_object(__name__)
recompute_server.config["SECRET_KEY"] = "SECRET!"
recompute_socket = SocketIO(recompute_server)

DEFAULT_VM = "ubuntu/trusty64"
DEFAULT_VAGRANT_FILE = "python.vagrant.config"
