
from flask import render_template as render_template
from flask_socketio import emit
from .config import recompute_server, recompute_socket
from .recompute import get_all_vms

@recompute_server.route("/", methods=["GET"])
@recompute_server.route("/index", methods=["GET"])
def get_index():
    vms = get_all_vms()
    return render_template("index.html", vms=list())

@recompute_server.route("/tty", methods=["GET"])
def get_tty():
    return render_template("tty.html")

@recompute_socket.on("connect", namespace="/tty")
def test_connect(message=None):
    print "connected"
    recompute_socket.emit("response", {"message": "Connected!!!!!"})
    emit("response", {"message": "Connected"})
