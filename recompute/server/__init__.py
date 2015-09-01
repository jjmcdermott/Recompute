__all__ = ["config", "boxes", "io", "forms", "pageserver", "sockets", "recomputation", "tasks", "defaults", "restful"]

import threading
import signal
import tornado.ioloop
import logging
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

is_closing = False


def run(address="0.0.0.0", port=5000):
    init()
    signal.signal(signal.SIGINT, signal_handler)
    config.recompute_server.bind(port=port, address=address)
    config.recompute_server.start(0)
    tornado.ioloop.PeriodicCallback(try_exit, 100).start()
    tornado.ioloop.IOLoop.instance().start()


def signal_handler(signum, frame):
    global is_closing
    logging.info('Exiting...')
    is_closing = True


def try_exit():
    global is_closing
    if is_closing:
        tornado.ioloop.IOLoop.instance().stop()
        logging.info('Exit success')


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
