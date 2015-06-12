import subprocess
import os
import sys
import requests
import yaml
from bs4 import BeautifulSoup
from .config import vagrant_config_dict, language_version_dict


def _execute(command, cwd):
    p = subprocess.Popen(command, cwd=cwd, stdout=subprocess.PIPE)
    lines_iter = iter(p.stdout.readline, b"")
    for line in lines_iter:
        sys.stdout.write(line)
        sys.stdout.flush()


def _generate_vagrantbox(project_dir, hostname):
    """
    Package a Vagrantbox
    """

    vagrant_up = ["vagrant", "up", "--provision"]
    _execute(vagrant_up, project_dir)

    vagrant_package =  ["vagrant", "package", "--output", hostname + ".box"]
    _execute(vagrant_package, project_dir)


def _generate_vagrantfile(hostname, github_url, language_version, base_vm, base_vagrantfile, new_vagrantfile_path):
    """
    Generate a Vagrantfile
    """

    with open("recompute/server/configs/" + base_vagrantfile, "r") as vagrant_file:
        vagrant_config = vagrant_file.read()

    vagrant_config = vagrant_config.replace("<HOSTNAME>", hostname)
    vagrant_config = vagrant_config.replace("<BOX>", base_vm)
    vagrant_config = vagrant_config.replace("<VERSION>", language_version or "")
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
    github_user = github_url.split("/")[-2]
    github_repo_name = github_url.split("/")[-1]
    raw_travis_url = "https://raw.githubusercontent.com/"+github_user+"/"+github_repo_name+"/master/.travis.yml"
    travis_script = requests.get(raw_travis_url)
    if travis_script.status_code < 400:
        travis_yaml = yaml.load(travis_script.text)
        travis_language = travis_yaml["language"]
        print [travis_language]
        return language_version_dict[language]
    elif language in language_version_dict:
        return language_version_dict[language]
    else:
        return None


def _get_project_language(github_url):
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

    print "Creating Project: {}...".format(hostname)

    os.makedirs(project_dir)
    print "Directory @ {}".format(project_dir)

    project_lang = _get_project_language(github_url)
    language_version = _get_language_version(project_lang, github_url)
    print "Language: {}, Version: {}".format(project_lang, language_version)

    base_vagrant_file = _get_base_vagrantfile(project_lang)
    if base_vagrant_file is None:
        # clean up
        os.rmdir(project_dir)
        return None
    print "Base VM: {}".format(base_vm)
    print "Base Vagrantfile: {}".format(base_vagrant_file)

    _generate_vagrantfile(hostname, github_url, language_version, base_vm, base_vagrant_file, vagrantfile_path)
    print "Vagrantfile @ {}".format(vagrantfile_path)

    _generate_vagrantbox(project_dir, hostname)
    print "Vagrantbox @ {}".format(vagrantbox_path)

    return relative_vagrantbox_path
