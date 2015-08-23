__all__ = ["config", "boxes", "io", "forms", "pageserver", "play", "recomputation", "recompute", "defaults",
           "restful"]

from tornado.ioloop import IOLoop
from . import config
from . import boxes
from . import io
from . import forms
from . import pageserver
from . import play
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

    recompute.server_prints("Creating recomputations directory...")
    io.create_recomputations_dir()

    recompute.server_prints("Updating base boxes...")
    io.update_base_vagrantboxes()

    recompute.server_prints("Getting recomputations count...")
    config.recomputations_count = io.get_recomputations_count()

    recompute.server_prints("Getting base boxes summary...")
    config.base_vagrantboxes_summary = io.get_base_vagrantboxes_summary()

    recompute.server_prints("Server started.")
