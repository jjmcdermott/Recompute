import subprocess
import os
import requests
from bs4 import BeautifulSoup
from .config import vagrant_config_dict, language_version_dict

def _execute(command, cwd):
    p = subprocess.Popen(command, cwd=cwd, stdout=subprocess.PIPE)
    lines_iter = iter(p.stdout.readline, b"")
    for line in lines_iter:
        print(line)

def _generate_vagrantbox(project_dir, hostname):
    """
    Package a Vagrant box
    """

    # vagrant_up = subprocess.Popen(
    #     ["vagrant", "up", "--provision"],
    #     cwd=project_dir, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # while True:
    #     nextline = vagrant_up.stdout.readline()
    #     if nextline == '' and vagrant_up.poll() != None:
    #         break

    vagrant_up = ["vagrant", "up", "--provision"]
    _execute(vagrant_up, project_dir)

    vagrant_package = subprocess.Popen(
        ["vagrant", "package", "--output", hostname + ".box"],
        cwd=project_dir, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, error = vagrant_package.communicate()
    print out
    print error


def _generate_vagrantfile(hostname, github_url, language_version, base_vm, base_vagrantfile, new_vagrantfile_path):
    """
    Generate a Vagrantfile
    """

    with open("recompute/server/configs/" + base_vagrantfile, "r") as vagrant_file:
        vagrant_config = vagrant_file.read()

    vagrant_config = vagrant_config.replace("<HOSTNAME>", hostname)
    vagrant_config = vagrant_config.replace("<BOX>", base_vm)
    vagrant_config = vagrant_config.replace("<VERSION>", language_version)
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


def _get_language_version(language, github_url):
    return language_version_dict[language]


def _get_project_language(github_url):
    requests.packages.urllib3.disable_warnings()
    response = requests.get(github_url)
    soup = BeautifulSoup(response.text)
    return soup.find("ol", attrs={"class": "repository-lang-stats-numbers"}).find("span", {"class": "lang"}).text


def create_vm(hostname, github_url, base_vm):
    """
    Create a new vagrant box
    """

    project_dir = "recompute/server/vms/" + hostname + "/"
    vagrantfile_path = project_dir + "Vagrantfile"
    vagrantbox_path = project_dir + hostname + ".box"
    relative_vagrantbox_path = "vms/" + hostname + "/" + hostname + ".box"

    print "Project: {}".format(hostname)

    os.makedirs(project_dir)
    print "Directory @ {}".format(project_dir)

    project_lang = _get_project_language(github_url)
    language_version = _get_language_version(project_lang, github_url)
    print "Language: {}, Version: {}".format(project_lang, language_version)

    base_vagrant_file = _get_base_vagrantfile(project_lang)
    if base_vagrant_file is None:
        return None
    print "Base VM: {}".format(base_vm)
    print "Base Vagrantfile: {}".format(base_vagrant_file)

    _generate_vagrantfile(hostname, github_url, language_version, base_vm, base_vagrant_file, vagrantfile_path)
    print "Vagrantfile @ {}".format(vagrantfile_path)

    _generate_vagrantbox(project_dir, hostname)
    print "Vagrantbox @ {}".format(vagrantbox_path)

    return relative_vagrantbox_path
