import os
import requests
import random
from bs4 import BeautifulSoup
from xml.etree import ElementTree
from flask import render_template as render_template
from .config import recompute_app, recomputation_count
from . import file


def _get_base_vagrantboxes():
    requests.packages.urllib3.disable_warnings()
    response = requests.get("https://atlas.hashicorp.com/boxes/search")
    soup = BeautifulSoup(response.text)
    return [str(span.a.text) for span in soup.findAll("span", attrs={"class": "title title-small"})]


def _get_latest_recomputation():
    recomputation_list = _get_all_recomputation()
    return random.sample(recomputation_list, 5)


def _get_all_recomputation():
    recomputation_list = list()
    software_dir = file.get_software_absolute_dir()
    inside_software_dir = next(os.walk(software_dir))
    recomputation_dirs = [os.path.join(inside_software_dir[0], d) for d in inside_software_dir[1]]
    for d in recomputation_dirs:
        recomputation_details = ElementTree.parse(d+"/recomputation.xml").getroot()
        latest_release = next(recomputation_details.iter("releases"))
        print latest_release
        recomputation_list.append({
            "name": recomputation_details["name"].text,
            "id": recomputation_details["id"].text,
            "tag": latest_release["tag"].text,
            "date": latest_release["date"].text,
            "box": latest_release["box"].text,
            "box_version": latest_release["box_version"].text
        })
    return recomputation_list


@recompute_app.route("/", methods=["GET"])
def get_index_page():
    return render_template("index.html",
                           recomputation_count=recomputation_count,
                           base_vagrantboxes=_get_base_vagrantboxes(),
                           latest_recomputation=_get_latest_recomputation())


@recompute_app.route("/software", methods=["GET"])
def get_software_page():
    return render_template("software.html", all_recomputation=_get_all_recomputation())


@recompute_app.route("/languages", methods=["GET"])
def get_languages_page():
    return render_template("languages.html")


@recompute_app.route("/recomputation/<string:name>", methods=["GET"])
def get_single_recomputation_page(name):
    recomputation = {"name": name}
    return render_template("recomputation.html", recomputation=recomputation)


@recompute_app.route("/tty", methods=["GET"])
def get_tty():
    return render_template("tty.html")
