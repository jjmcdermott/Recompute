
from flask import Flask
from flask_socketio import SocketIO

recompute_server = Flask(__name__)
recompute_server.config.from_object(__name__)
recompute_server.config["SECRET_KEY"] = "SECRET!"
recompute_server.debug = True
recompute_socket = SocketIO(recompute_server)

DEFAULT_VM = "ubuntu/trusty64"

vagrant_config_dict = dict()
vagrant_config_dict["Python"] = "python.vagrant.config"
vagrant_config_dict["NodeJS"] = "nodejs.vagrant.config"
vagrant_config_dict["JavaScript"] = "nodejs.vagrant.config"

language_version_dict = dict()
language_version_dict["Python"] = "2.7"
language_version_dict["NodeJS"] = "0.10"
language_version_dict["JavaScript"] = "0.10"
