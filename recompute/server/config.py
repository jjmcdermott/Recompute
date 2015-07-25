import flask
import tornado.wsgi
import tornado.httpserver
import tornado.web
import tornado.log

recompute_app = flask.Flask(__name__)
recompute_app.config.from_object(__name__)
recompute_app.config["SECRET_KEY"] = "SECRET!"
recompute_app.debug = True

recompute_container = tornado.wsgi.WSGIContainer(recompute_app)

settings = {
    "auto_reload": True,
    "debug": True
}

from . import play
recompute_server = tornado.httpserver.HTTPServer(tornado.web.Application([
    (r"/ws/play/(.*)", play.PlayWebSocket),
    (r".*", tornado.web.FallbackHandler, dict(fallback=recompute_container))
], **settings))

tornado.log.enable_pretty_logging()

default_memory = 4098
default_cpus = 2

default_recomputefile = "recompute/server/software/recomputation.xml"

default_vagrantfile_dict = {
    "python": "recompute/server/languages/python/python.vconfig",
    "node_js": "recompute/server/languages/nodejs/nodejs.vconfig",
    "cpp": "recompute/server/languages/cpp/cpp.vconfig",
    "c++": "recompute/server/languages/cpp/cpp.vconfig",
    "c": "recompute/server/languages/cpp/cpp.vconfig"
}

default_language_install_dict = {
    "python": "pip install -r requirements.txt",
    "node_js": "npm install",
    "cpp": ["chmod +x configure", "./configure", "make", "sudo make install"],
    "c++": ["chmod +x configure", "./configure", "make", "sudo make install"],
    "c": ["chmod +x configure", "./configure", "make", "sudo make install"]
}

default_language_version_dict = {
    "python": "2.7",
    "node_js": "0.10",
    "cpp": "",
    "c++": "",
    "c": ""
}
