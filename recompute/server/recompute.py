import subprocess
import os
import sys
import requests
import yaml
from bs4 import BeautifulSoup
from .config import default_vagrantfile_dict, default_language_version_dict, default_language_install_dict
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
    def _generate_vagrantfile(build_details, base_vagrantfile_path, software_vagrantfile_path):

        with open(base_vagrantfile_path, "r") as vagrant_file:
            vagrant_config = vagrant_file.read()

        vagrant_config = vagrant_config.replace("<HOSTNAME>", build_details["HOSTNAME"])
        vagrant_config = vagrant_config.replace("<BOX>", build_details["BOX"])
        vagrant_config = vagrant_config.replace("<LANG_VERSION>", build_details["LANG_VERSION"])
        vagrant_config = vagrant_config.replace("<GITHUB_URL>", build_details["GITHUB_URL"])
        vagrant_config = vagrant_config.replace("<GITHUB_REPO_NAME>", build_details["GITHUB_REPO_NAME"])
        vagrant_config = vagrant_config.replace("<ADD_APT_REPOSITORY>", build_details["ADD_APT_REPOSITORY"])
        vagrant_config = vagrant_config.replace("<APT_GET_INSTALL>", build_details["APT_GET_INSTALL"])
        vagrant_config = vagrant_config.replace("<INSTALL_SCRIPT>", build_details["INSTALL_SCRIPT"])
        vagrant_config = vagrant_config.replace("<TEST_SCRIPT>", "")

        with open(software_vagrantfile_path, "w") as vagrant_file:
            vagrant_file.write("{0}".format(vagrant_config))

    @staticmethod
    def _get_base_vagrantfile(language):
        if language in default_vagrantfile_dict:
            return default_vagrantfile_dict[language]
        else:
            return None

    @staticmethod
    def _get_build_details(software_lang, travis_script):
        add_apt_repositories = []
        apt_packages = []
        installs = []
        scripts = []

        if travis_script is not None:
            if "before_install" in travis_script:
                travis_before_install = travis_script["before_install"]
                # ADD_APT_REPOSITORIES
                for add_apt_repo in [line for line in travis_before_install if "add-apt-repository" in line]:
                    repositories = [phrase for phrase in add_apt_repo.split(" ") if phrase.startswith("ppa:")]
                    add_apt_repositories.extend(repositories)

                # APT-GET INSTALL
                for apt_get_install in [line for line in travis_before_install if "apt-get install" in line]:
                    packages = [phrase for phrase in apt_get_install.split(" ") if
                                phrase not in ["sudo", "apt-get", "install", "-y"]]
                    apt_packages.extend(packages)

            # APT-GET INSTALL
            if "addons" in travis_script and "apt_packages" in travis_script["addons"]:
                apt_packages.extend(travis_script["addons"]["apt_packages"])

            # INSTALL
            if "install" in travis_script:
                installs.extend(travis_script["install"])

            # SCRIPT
            if "script" in travis_script:
                scripts.extend(travis_script["script"])

        else:
            installs.append(default_language_install_dict[software_lang])

        return {
            "ADD_APT_REPOSITORY": "\n".join(["add-apt-repository -y " + repo for repo in add_apt_repositories]),
            "APT_GET_INSTALL": "apt-get install -y " + " ".join(apt_packages) + "\n",
            "INSTALL_SCRIPT": "\n".join(installs),
            "TEST_SCRIPT": "\n".join(scripts)
        }

    @staticmethod
    def _get_software_language_version(software_lang, travis_script):
        if travis_script is not None:
            if travis_script[software_lang] is not None:
                return travis_script[software_lang][-1]
        if software_lang in default_language_version_dict:
            return default_language_version_dict[software_lang]
        else:
            return None

    @staticmethod
    def _get_software_language(github_url, travis_script):
        if travis_script is not None:
            return travis_script["language"]
        else:
            response = requests.get(github_url)
            soup = BeautifulSoup(response.text)
            return soup.find("span", {"class": "lang"}).text.lower()

    @staticmethod
    def _get_travis_script(github_url):
        user = github_url.split("/")[-2]
        repo = github_url.split("/")[-1]
        raw_travis_url = "https://raw.githubusercontent.com/" + user + "/" + repo + "/master/.travis.yml"
        travis_script = requests.get(raw_travis_url)
        if travis_script.status_code < 400:
            return yaml.load(travis_script.text)
        else:
            return None

    @staticmethod
    def create_vm(name, github_url, base_vm):
        software_dir = get_software_absolute_path(name)
        software_vagrantfile_path = software_dir + "Vagrantfile"
        software_vagrantbox_path = software_dir + name + ".box"

        os.makedirs(software_dir)
        travis_script = Recomputation._get_travis_script(github_url)
        software_lang = Recomputation._get_software_language(github_url, travis_script)
        software_lang_ver = Recomputation._get_software_language_version(software_lang, travis_script)

        print "Creating Project: {}...".format(name)
        print "Directory @ {}".format(software_dir)
        print "Language: {}, Version: {}".format(software_lang, software_lang_ver)

        base_vagrantfile_path = Recomputation._get_base_vagrantfile(software_lang)
        if base_vagrantfile_path is None:
            print "Base Vagrantfile not found"
            os.rmdir(software_dir)
            return False

        build_details = Recomputation._get_build_details(software_lang, travis_script)
        build_details["HOSTNAME"] = name
        build_details["BOX"] = base_vm
        build_details["LANG_VERSION"] = software_lang_ver
        build_details["GITHUB_URL"] = github_url
        build_details["GITHUB_REPO_NAME"] = github_url.split("/")[-1]

        Recomputation._generate_vagrantfile(build_details, base_vagrantfile_path, software_vagrantfile_path)
        Recomputation._generate_vagrantbox(software_dir, name)

        print "Base VM: {}".format(base_vm)
        print "Base Vagrantfile: {}".format(base_vagrantfile_path)
        print "Vagrantfile @ {}".format(software_vagrantfile_path)
        print "Vagrantbox @ {}".format(software_vagrantbox_path)

        return True
