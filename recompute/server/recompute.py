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
    def _generate_vagrantfile(name, github_url, software_lang_ver, base_vm, build_details, base_vagrantfile_path,
                              software_vagrantfile_path):
        with open(base_vagrantfile_path, "r") as vagrant_file:
            vagrant_config = vagrant_file.read()

        vagrant_config = vagrant_config.replace("<HOSTNAME>", name)
        vagrant_config = vagrant_config.replace("<BOX>", base_vm)
        vagrant_config = vagrant_config.replace("<VERSION>", software_lang_ver)
        vagrant_config = vagrant_config.replace("<GITHUB_URL>", github_url)
        vagrant_config = vagrant_config.replace("<GITHUB_REPO_NAME>", github_url.split("/")[-1])
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
            travis_before_install = travis_script["before_install"]
            if travis_before_install is not None:
                # ADD_APT_REPOSITORIES
                add_apt_packages_cmds = [cmd for cmd in travis_before_install if "add-apt-repository" in cmd]
                print add_apt_packages_cmds
                for cmd in add_apt_packages_cmds:
                    repositories = [phrase for phrase in cmd.split(" ") if phrase.startswith("ppa:")]
                    add_apt_repositories.append(repositories)
                # APT-GET INSTALL
                apt_get_install_cms = [cmd for cmd in travis_before_install if "apt-get install" in cmd]
                print apt_get_install_cms
                for cmd in apt_get_install_cms:
                    packages = [phrase for phrase in cmd.split(" ") if phrase not in ["sudo", "apt-get", "install", "-y"]]
                    apt_packages.append(packages)

            # APT-GET INSTALL
            travis_apt_packages = travis_script["addons"]["apt_packages"]
            if travis_apt_packages is not None:
                apt_packages.append(travis_apt_packages)

            # INSTALL
            travis_install = travis_script["install"]
            if travis_install is not None:
                installs.append(travis_install)

            # SCRIPT
            travis_script = travis_script["script"]
            if travis_script is not None:
                scripts.append(travis_script)

        else:
            installs = default_language_install_dict[software_lang]

        return {
            "ADD_APT_REPOSITORY": "\n".join(["add-apt-repository -y " + repo for repo in add_apt_repositories]),
            "APT_GET_INSTALL": "apt-get install -y " + " ".join(apt_packages),
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
        github_user = github_url.split("/")[-2]
        github_repo_name = github_url.split("/")[-1]
        raw_travis_url = "https://raw.githubusercontent.com/" + github_user + "/" + github_repo_name + "/master/.travis.yml"
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

        print "Creating Project: {}...".format(name)
        print "Directory @ {}".format(software_dir)

        os.makedirs(software_dir)
        travis_script = Recomputation._get_travis_script(github_url)
        software_lang = Recomputation._get_software_language(github_url, travis_script)
        software_lang_ver = Recomputation._get_software_language_version(software_lang, github_url)

        print "Language: {}, Version: {}".format(software_lang, software_lang_ver)

        base_vagrantfile_path = Recomputation._get_base_vagrantfile(software_lang)
        if base_vagrantfile_path is None:
            print "Base Vagrantfile not found"
            os.rmdir(software_dir)
            return False

        build_details = Recomputation._get_build_details(software_lang, travis_script)
        Recomputation._generate_vagrantfile(
            name, github_url, software_lang_ver, base_vm, base_vagrantfile_path, software_vagrantfile_path)
        Recomputation._generate_vagrantbox(software_dir, name)

        print "Base VM: {}".format(base_vm)
        print "Base Vagrantfile: {}".format(base_vagrantfile_path)
        print "Vagrantfile @ {}".format(software_vagrantfile_path)
        print "Vagrantbox @ {}".format(software_vagrantbox_path)

        return True
