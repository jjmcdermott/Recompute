import flask
import tornado.wsgi
import tornado.httpserver
import tornado.web
import tornado.log

recompute_app = flask.Flask(__name__)
recompute_app.config.from_object(__name__)
recompute_app.config["SECRET_KEY"] = "SECRET!"
recompute_app.debug = True

from . import play

recompute_container = tornado.wsgi.WSGIContainer(recompute_app)
settings = {
    "auto_reload": True,
    "debug": True
}
recompute_server = tornado.httpserver.HTTPServer(tornado.web.Application([
    (r"/ws/play/(.*)", play.PlayWebSocket),
    (r".*", tornado.web.FallbackHandler, dict(fallback=recompute_container))
], **settings))

tornado.log.enable_pretty_logging()

recomputations_count = 0
