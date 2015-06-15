import subprocess
import os
import sys
import requests
import yaml
from bs4 import BeautifulSoup
from .config import default_vagrantfile_dict, default_language_version_dict
from .file import get_software_absolute_path


class Recomputation:
    def __init__(self):
        pass

    @staticmethod
    def _execute(command, cwd):
        p = subprocess.Popen(command, cwd=cwd, stdout=subprocess.PIPE)
        lines_iter = iter(p.stdout.readline, b"")
        for line in lines_iter:
            sys.stdout.write(line)
            sys.stdout.flush()

    @staticmethod
    def _generate_vagrantbox(software_dir, name):
        Recomputation._execute(["vagrant", "up", "--provision"], software_dir)
        Recomputation._execute(["vagrant", "package", "--output", name + ".box"], software_dir)

    @staticmethod
    def _generate_vagrantfile(name, github_url, software_lang_ver, base_vm, base_vagrantfile_path,
                              software_vagrantfile_path):
        with open(base_vagrantfile_path, "r") as vagrant_file:
            vagrant_config = vagrant_file.read()

        vagrant_config = vagrant_config.replace("<NAME>", name)
        vagrant_config = vagrant_config.replace("<BOX>", base_vm)
        vagrant_config = vagrant_config.replace("<VERSION>", software_lang_ver or "")
        vagrant_config = vagrant_config.replace("<GITHUB_URL>", github_url)
        vagrant_config = vagrant_config.replace("<GITHUB_REPO_NAME>", github_url.split("/")[-1])

        with open(software_vagrantfile_path, "w") as vagrant_file:
            vagrant_file.write("{0}".format(vagrant_config))

    @staticmethod
    def _get_base_vagrantfile(language):
        if language in default_vagrantfile_dict:
            return default_vagrantfile_dict[language]
        else:
            return None

    @staticmethod
    def _get_software_language_version(software_lang, github_url):
        github_user = github_url.split("/")[-2]
        github_repo_name = github_url.split("/")[-1]
        raw_travis_url = "https://raw.githubusercontent.com/" + github_user + "/" + github_repo_name + "/master/.travis.yml"
        travis_script = requests.get(raw_travis_url)
        if travis_script.status_code < 400:
            travis_yaml = yaml.load(travis_script.text)
            travis_language = travis_yaml["language"]
            return travis_yaml[travis_language][-1]
        elif software_lang in default_language_version_dict:
            return default_language_version_dict[software_lang]
        else:
            return None

    @staticmethod
    def _get_software_language(github_url):
        response = requests.get(github_url)
        soup = BeautifulSoup(response.text)
        return soup.find("ol", attrs={"class": "repository-lang-stats-numbers"}).find("span", {"class": "lang"}).text

    @staticmethod
    def create_vm(name, github_url, base_vm):
        software_dir = get_software_absolute_path(name)
        software_vagrantfile_path = software_dir + "Vagrantfile"
        software_vagrantbox_path = software_dir + name + ".box"

        print "Creating Project: {}...".format(name)
        print "Directory @ {}".format(software_dir)

        os.makedirs(software_dir)
        software_lang = Recomputation._get_software_language(github_url)
        software_lang_ver = Recomputation._get_software_language_version(software_lang, github_url)

        print "Language: {}, Version: {}".format(software_lang, software_lang_ver)

        base_vagrantfile_path = Recomputation._get_base_vagrantfile(software_lang)
        if base_vagrantfile_path is None:
            print "Base Vagrantfile not found"
            os.rmdir(software_dir)
            return False

        Recomputation._generate_vagrantfile(
            name, github_url, software_lang_ver, base_vm, base_vagrantfile_path, software_vagrantfile_path)
        Recomputation._generate_vagrantbox(software_dir, name)

        print "Base VM: {}".format(base_vm)
        print "Base Vagrantfile: {}".format(base_vagrantfile_path)
        print "Vagrantfile @ {}".format(software_vagrantfile_path)
        print "Vagrantbox @ {}".format(software_vagrantbox_path)

        return True
