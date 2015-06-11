
import os
import requests
from bs4 import BeautifulSoup
from flask import render_template as render_template
from .config import recompute_server

def _get_online_base_vagrantboxes():
    requests.packages.urllib3.disable_warnings()
    response = requests.get("https://atlas.hashicorp.com/boxes/search")
    soup = BeautifulSoup(response.text)
    return [str(span.a.text) for span in soup.findAll("span", attrs={"class": "title title-small"})]

def _get_all_vms():
    vms = list()
    for hostname in next(os.walk("recompute/server/vms/"))[1]:
        vms.append({"hostname": hostname})
    return vms


@recompute_server.route("/", methods=["GET"])
@recompute_server.route("/index", methods=["GET"])
def get_index():
    return render_template("index.html", base_vagrantboxes=_get_online_base_vagrantboxes(), vms=_get_all_vms())


@recompute_server.route("/tty", methods=["GET"])
def get_tty():
    return render_template("tty.html")
