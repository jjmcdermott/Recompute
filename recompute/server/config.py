
from flask import Flask

recompute_server = Flask(__name__)
recompute_server.config.from_object(__name__)
