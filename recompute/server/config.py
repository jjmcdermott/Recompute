import flask
import tornado.wsgi
import tornado.httpserver
import tornado.web
import tornado.log
from recompute.server import sockets as recompute_sockets

recompute_app = flask.Flask(__name__)
recompute_app.config.from_object(__name__)
recompute_app.config["SECRET_KEY"] = "SECRET!"
recompute_app.config["CELERY_BROKER_URL"] = "redis://localhost:6379/0"
recompute_app.config["CELERY_RESULT_BACKEND"] = "redis://localhost:6379/0"
recompute_app.debug = True
recompute_app.use_reloader = False

recompute_container = tornado.wsgi.WSGIContainer(recompute_app)
settings = {
    "autoreload": False,
    "debug": True
}
recompute_server = tornado.httpserver.HTTPServer(tornado.web.Application([
    (r"/ws/play/(.*)/(.*)/(.*)", recompute_sockets.PlayWebSocket),
    (r"/ws/recompute/(.*)", recompute_sockets.RecomputeSocket),
    (r".*", tornado.web.FallbackHandler, dict(fallback=recompute_container))
], **settings))

tornado.log.enable_pretty_logging()

# initialization variables
recomputations_count = 0
base_vagrantboxes_summary = None

# how many recomputations to show in the "latest" list
latest_count = 5

# update timer = 24 hrs
update_base_vms_timer = 5.0 * 60 * 60 * 24
clean_up_timer = 5.0 * 60 * 60 * 24

recomputation_sockets = dict()
