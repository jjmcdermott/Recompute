
from flask import Flask

recompute_server = Flask(__name__)
recompute_server.config.from_object(__name__)

DEFAULT_VM = "ubuntu/trusty64"
DEFAULT_VAGRANT_FILE = "python.vagrant"
