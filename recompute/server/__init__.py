
__all__ = ["config", "pageserver", "restful"]

from config import recompute_server
from recompute.server import pageserver
from recompute.server import restful

def run(host, port):
    recompute_server.run(host=host, port=port, debug=True)
