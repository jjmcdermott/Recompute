__all__ = ["config", "boxes", "io", "forms", "pageserver", "play_socket", "recompute_socket", "recomputation",
           "recompute", "defaults", "restful"]

import threading
from tornado.ioloop import IOLoop
from . import config
from . import boxes
from . import io
from . import forms
from . import pageserver
from . import play_socket
from . import recompute_socket
from . import recomputation
from . import recompute
from . import defaults
from . import restful


def run(port):
    init()
    config.recompute_server.listen(port)
    IOLoop.instance().start()


def init():
    """
    Initialization function for the web app
    """

    io.server_prints("Creating recomputations directory...")
    io.create_recomputations_dir()

    io.server_prints("Getting recomputations count...")
    config.recomputations_count = io.get_recomputations_count()

    update_base_vagrantboxes()
    clean_up_failed_recomputations()

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
