import os
import requests
from bs4 import BeautifulSoup
from flask import render_template as render_template
from .config import recompute_app


def _get_base_vagrantboxes():
    requests.packages.urllib3.disable_warnings()
    response = requests.get("https://atlas.hashicorp.com/boxes/search")
    soup = BeautifulSoup(response.text)
    return [str(span.a.text) for span in soup.findAll("span", attrs={"class": "title title-small"})]


def _get_latest_recomputation():
    recomputation_list = [{"name": name} for name in next(os.walk("recompute/server/software/"))[1]]
    return recomputation_list


def _get_all_recomputation():
    recomputation_list = [{"name": name} for name in next(os.walk("recompute/server/software/"))[1]]
    return recomputation_list

@recompute_app.route("/", methods=["GET"])
def get_index_page():
    return render_template(
        "index.html", base_vagrantboxes=_get_base_vagrantboxes(), latest_recomputation=_get_latest_recomputation())


@recompute_app.route("/software", methods=["GET"])
def get_software_page():
    return render_template("software.html", recomputation=_get_all_recomputation())


@recompute_app.route("/languages", methods=["GET"])
def get_languages_page():
    return render_template("languages.html")


@recompute_app.route("/tty", methods=["GET"])
def get_tty():
    return render_template("tty.html")
