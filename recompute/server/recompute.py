import subprocess
import os
import requests
from bs4 import BeautifulSoup
from .config import vagrant_config_dict


def _generate_vagrantbox(project_dir, hostname):
    """
    Package a Vagrant box
    """

    vagrant_up = subprocess.Popen(
        ["vagrant", "up", "--provision"],
        cwd=project_dir, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, error = vagrant_up.communicate()
    print out
    print error

    vagrant_package = subprocess.Popen(
        ["vagrant", "package", "--output", hostname + ".box"],
        cwd=project_dir, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, error = vagrant_package.communicate()
    print out
    print error


def _generate_vagrantfile(hostname, github_url, base_vm, base_vagrantfile, new_vagrantfile_path):
    """
    Generate a Vagrantfile
    """

    with open("recompute/server/vagrant_configs/" + base_vagrantfile, "r") as vagrant_file:
        vagrant_config = vagrant_file.read()

    vagrant_config = vagrant_config.replace("<HOSTNAME>", hostname)
    vagrant_config = vagrant_config.replace("<BOX>", base_vm)
    vagrant_config = vagrant_config.replace("<GITHUB_URL>", github_url)
    vagrant_config = vagrant_config.replace("<GITHUB_REPO_NAME>", github_url.split("/")[-1])

    with open(new_vagrantfile_path, "w") as vagrant_file:
        vagrant_file.write("{0}".format(vagrant_config))


def _get_base_vagrantfile(language):
    """
    Get the base Vagrantfile
    """

    if language in vagrant_config_dict:
        return vagrant_config_dict[language]
    else:
        return None


def _get_project_language(github_url):
    requests.packages.urllib3.disable_warnings()
    response = requests.get(github_url)
    soup = BeautifulSoup(response.text)
    return soup.find("ol", {"class": "repository-lang-stats-numbers"}).find("span", {"class": "lang"}).text


def create_vm(hostname, github_url, base_vm):
    """
    Create a new vagrant box
    """

    project_dir = "recompute/server/vms/" + hostname + "/"
    vagrantfile_path = project_dir + "Vagrantfile"
    vagrantbox_path = project_dir + hostname + ".box"
    relative_vagrantbox_path = "vms/" + hostname + "/" + hostname + ".box"

    if os.path.exists(project_dir) and os.path.isfile(vagrantbox_path):
        print "Returning the existing vm @ {}".format(vagrantbox_path)
        return relative_vagrantbox_path
    elif not os.path.exists(project_dir):
        print "Creating new project directory @ {}".format(project_dir)
        os.makedirs(project_dir)

    project_lang = _get_project_language(github_url)
    print "Project language: {}".format(project_lang)

    print "Project base VM: {}".format(base_vm)

    base_vagrant_file = _get_base_vagrantfile(project_lang)
    if base_vagrant_file is None:
        return None
    print "Project base Vagrantfile: {}".format(base_vagrant_file)

    _generate_vagrantfile(hostname, github_url, base_vm, base_vagrant_file, vagrantfile_path)
    print "Vagrantfile @ {}".format(vagrantfile_path)

    _generate_vagrantbox(project_dir, hostname)
    # print "Vagrantbox @ {}\n".format(vagrantbox_path)

    return relative_vagrantbox_path
