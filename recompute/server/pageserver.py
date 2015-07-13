import os
import requests
from bs4 import BeautifulSoup
from xml.etree import ElementTree
from flask import render_template as render_template
from .config import recompute_app
from . import file


def _get_base_vagrantboxes():
    requests.packages.urllib3.disable_warnings()
    response = requests.get("https://atlas.hashicorp.com/boxes/search")
    soup = BeautifulSoup(response.text)
    return [str(span.a.text) for span in soup.findAll("span", attrs={"class": "title title-small"})]


def _get_latest_recomputation():
    recomputation_list = _get_all_recomputation()
    return recomputation_list[-5:]


def _get_all_recomputation():
    recomputation_list = list()
    software_dir = file.get_software_absolute_dir()
    inside_software_dir = next(os.walk(software_dir))
    recomputation_dirs = [os.path.join(inside_software_dir[0], d) for d in inside_software_dir[1]]
    for d in recomputation_dirs:
        recomputation_details = ElementTree.parse(d + "/recomputation.xml").getroot()
        latest_release = recomputation_details.find("releases")[0]
        recomputation_list.append({
            "name": recomputation_details.find("name").text,
            "id": recomputation_details.find("id").text,
            "tag": latest_release.find("tag").text,
            "version": latest_release.find("version").text,
            "date": latest_release.find("date").text,
            "box": latest_release.find("box").text,
            "box_version": latest_release.find("box_version").text
        })
    recomputation_list.sort(key=lambda recomputation: recomputation["id"])
    return recomputation_list


@recompute_app.route("/", methods=["GET"])
def get_index_page():
    return render_template("index.html",
                           recomputation_count=file.get_recomputation_count(),
                           base_vagrantboxes=_get_base_vagrantboxes(),
                           latest_recomputation=_get_latest_recomputation())


@recompute_app.route("/software", methods=["GET"])
def get_software_page():

    from forms import FilterSoftwareForm
    form = FilterSoftwareForm()

    return render_template("software.html", filter_software_form=form, all_recomputation=_get_all_recomputation())


@recompute_app.route("/base_vms", methods=["GET"])
def get_languages_page():
    return render_template("base_vms.html")


@recompute_app.route("/recomputation/<string:name>", methods=["GET"])
def get_single_recomputation_page(name):
    software_dir = file.get_software_absolute_path(name)
    recomputation_details = ElementTree.parse(software_dir + "/recomputation.xml").getroot()
    latest_release = recomputation_details.find("releases")[0]
    recomputation = {
        "name": recomputation_details.find("name").text,
        "id": recomputation_details.find("id").text,
        "tag": latest_release.find("tag").text,
        "version": latest_release.find("version").text,
        "date": latest_release.find("date").text,
        "box": latest_release.find("box").text,
        "box_version": latest_release.find("box_version").text
    }
    return render_template("recomputation.html", recomputation=recomputation)


@recompute_app.route("/tty", methods=["GET"])
def get_tty():
    return render_template("tty.html")
