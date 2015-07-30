__all__ = ["config", "consts", "file", "forms", "pageserver", "play", "recomputation", "recompute", "recompute_learn",
           "restful"]

from tornado.ioloop import IOLoop
from . import config
from . import consts
from . import file
from . import forms
from . import pageserver
from . import play
from . import recomputation
from . import recompute
from . import recompute_learn
from . import restful


def run(port):
    config.recomputations_count = file.get_recomputations_count()
    config.recompute_server.listen(port)
    IOLoop.instance().start()
