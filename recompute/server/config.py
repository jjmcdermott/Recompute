import flask
import tornado.wsgi
import tornado.httpserver
import tornado.web
import tornado.log
from . import play

recompute_app = flask.Flask(__name__)
recompute_app.config.from_object(__name__)
recompute_app.config["SECRET_KEY"] = "SECRET!"
recompute_app.debug = True

recompute_container = tornado.wsgi.WSGIContainer(recompute_app)
settings = {
    "auto_reload": False,
    "debug": True
}
recompute_server = tornado.httpserver.HTTPServer(tornado.web.Application([
    (r"/ws/play/(.*)/(.*)/(.*)", play.PlayWebSocket),
    (r".*", tornado.web.FallbackHandler, dict(fallback=recompute_container))
], **settings))

tornado.log.enable_pretty_logging()

# how many recomputations to show in the "latest" list
latest_recomputations_count = 5

# initialization variables
recomputations_count = 0
base_vagrantboxes_summary = None
