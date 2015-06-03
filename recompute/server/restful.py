
from config import recompute_server
from flask import send_file as f_send_file

@recompute_server.route("/recompute/", methods=["GET"])
@recompute_server.route("/recompute/<string:url>", methods=["GET"])
def recompute(url=None):
    https_clone_url = url + ".git"
    # subprocess.check_call(["git", "clone", https_clone_url])

    repo_name = re.split("/", https_clone_url)[-1].replace(".git", "")
    subprocess.check_call(["cd", repo_name], shell=True)
    subprocess.check_call(["pipreqs", repo_name])
    return f_send_file("data/dummy.txt", mimetype="text/plain", as_attachment=True)
