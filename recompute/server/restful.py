from config import recompute_server
from flask import jsonify
from flask import send_file as f_send_file
import subprocess


@recompute_server.route("/recompute/", methods=["GET"])
@recompute_server.route("/recompute/<string:url>", methods=["GET"])
def recompute(url=None):
    print "Making a vagrant box..."
    x = subprocess.Popen(
        ["cd", "recompute/server/data/", "&&", "pwd", "&&",
         "vagrant", "destroy", "--force", "&&",
         "vagrant", "up", "--provision", "&&", "vagrant", "package", "--output", "recompute.box"],
        shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, error = x.communicate()
    print out
    print error
    return f_send_file("data/recompute.box", mimetype="application/vnd.previewsystems.box", as_attachment=True)
