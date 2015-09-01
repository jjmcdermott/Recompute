__all__ = ["config", "boxes", "io", "forms", "pageserver", "sockets", "recomputation", "tasks", "defaults", "restful"]

import threading
from tornado.ioloop import IOLoop
from recompute.server import config
from recompute.server import boxes
from recompute.server import io
from recompute.server import forms
from recompute.server import pageserver
from recompute.server import sockets
from recompute.server import recomputation
from recompute.server import tasks
from recompute.server import defaults
from recompute.server import restful


def run(address, port):
    init()
    config.recompute_server.listen(port, address)
    IOLoop.instance().start()


def init():
    """
    Initialization function for the web app
    """

    io.server_prints("Creating recomputations directory...")
    io.create_recomputations_dir()
    io.create_logs_dir()

    io.server_prints("Getting recomputations count...")
    config.recomputations_count = io.get_recomputations_count()

    update_base_vagrantboxes()

    clean_up_failed_recomputations()

    clean_up_logs()

    io.server_prints("Server started.")


def update_base_vagrantboxes():
    t = threading.Timer(config.update_base_vms_timer, update_base_vagrantboxes)
    t.daemon = True  # exit when ctrl-c is pressed
    t.start()

    io.server_prints("Updating base boxes...")
    io.update_base_vagrantboxes()

    io.server_prints("Refreshing base boxes information...")
    config.base_vagrantboxes_summary = io.get_base_vagrantboxes_summary()


def clean_up_failed_recomputations():
    t = threading.Timer(config.clean_up_timer, clean_up_failed_recomputations)
    t.daemon = True
    t.start()

    io.server_prints("Cleaning up failed recomputations...")
    io.remove_failed_recomputations()


def clean_up_logs():
    t = threading.Timer(config.clean_up_timer, clean_up_logs)
    t.daemon = True
    t.start()

    io.server_prints("Cleaning up logs...")
    io.remove_logs()
