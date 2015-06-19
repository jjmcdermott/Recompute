import subprocess
import os
import sys
import shutil
import requests
import yaml
from bs4 import BeautifulSoup
from xml.etree import ElementTree
from . import config
from . import file


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
        p.communicate()
        rcode = p.returncode
        if rcode == 0:
            return True
        else:
            return False

    @staticmethod
    def _generate_recomputefile(build_details, base_recomputefile_path, software_recomputefile_path):
        recomputefile = ElementTree.parse(base_recomputefile_path)
        root = recomputefile.getroot()
        root["id"].text = config.recomputation_count

    @staticmethod
    def _generate_vagrantbox(software_dir, name):
        success = Recomputation._execute(["vagrant", "up", "--provision"], software_dir)
        if success:
            success = Recomputation._execute(["vagrant", "package", "--output", name + ".box"], software_dir)
        Recomputation._execute(["vagrant", "halt"], software_dir)
        if success:
            return True
        else:
            return False

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
        vagrant_config = vagrant_config.replace("<TEST_SCRIPT>", build_details["TEST_SCRIPT"])
        vagrant_config = vagrant_config.replace("<MEMORY>", build_details["MEMORY"])
        vagrant_config = vagrant_config.replace("<CPUS>", build_details["CPUS"])

        with open(software_vagrantfile_path, "w") as vagrant_file:
            vagrant_file.write("{0}".format(vagrant_config))

    @staticmethod
    def _get_base_vagrantfile(language):
        if language in config.default_vagrantfile_dict:
            return config.default_vagrantfile_dict[language]
        else:
            return None

    @staticmethod
    def _get_build_details(software_lang, travis_script):
        add_apt_repositories = list()
        apt_install_packages = list()
        install_scripts = list()
        envs = list()
        test_scripts = list()

        if travis_script is not None:
            if "before_install" in travis_script:
                travis_before_install = travis_script["before_install"]
                # ADD_APT_REPOSITORIES
                for add_apt_repo in [line for line in travis_before_install if "add-apt-repository" in line]:
                    repositories = [repo for repo in add_apt_repo.split(" ") if repo.startswith("ppa:")]
                    add_apt_repositories.extend(repositories)

                # APT-GET INSTALL
                for apt_get_install in [line for line in travis_before_install if "apt-get install" in line]:
                    packages = [p for p in apt_get_install.split(" ") if p not in ["sudo", "apt-get", "install", "-y"]]
                    apt_install_packages.extend(packages)

            # APT-GET INSTALL
            if "addons" in travis_script and "apt_packages" in travis_script["addons"]:
                apt_install_packages.extend(travis_script["addons"]["apt_packages"])

            # INSTALL
            if "install" in travis_script:
                install_scripts.extend(travis_script["install"])

            # ENV
            if "env" in travis_script:
                envs.extend(travis_script["env"])

            # SCRIPT
            if "script" in travis_script:
                test_scripts.extend(travis_script["script"])

        else:
            install_scripts.extend(config.default_language_install_dict[software_lang])

        # CLEAN UP
        final_test_scripts = list()
        # NON-TEST statements
        final_test_scripts.extend([s for s in test_scripts if not any(env.split("=", 1)[0] in s for env in envs)])
        # TEST statements, interpolated with different env variables
        for env in envs:
            final_test_scripts.append(str("export " + env))
            final_test_scripts.extend([s for s in test_scripts if env.split("=", 1)[0] in s])

        return {
            "ADD_APT_REPOSITORY": "\n".join(["add-apt-repository -y " + repo for repo in add_apt_repositories]),
            "APT_GET_INSTALL": "apt-get install -y " + " ".join(apt_install_packages) + "\n",
            "INSTALL_SCRIPT": "\n  ".join(install_scripts),
            "TEST_SCRIPT": "\n  ".join(final_test_scripts)
        }

    @staticmethod
    def _get_software_language_version(software_lang, travis_script):
        if travis_script is not None:
            if software_lang in travis_script:
                return travis_script[software_lang][-1]
        if software_lang in config.default_language_version_dict:
            return config.default_language_version_dict[software_lang]
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
        software_dir = file.get_software_absolute_path(name)
        software_vagrantfile_path = software_dir + "Vagrantfile"
        software_vagrantbox_path = software_dir + name + ".box"
        software_recomputefile_path = software_dir + "recomputation.xml"

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
        build_details["MEMORY"] = config.default_memory
        build_details["CPUS"] = config.default_cpus

        Recomputation._generate_vagrantfile(build_details, base_vagrantfile_path, software_vagrantfile_path)
        success = Recomputation._generate_vagrantbox(software_dir, name)
        if not success:
            "Vagrantbox not created"
            shutil.rmtree(software_dir, ignore_errors=True)
            return False

        # Recomputation._generate_recomputefile(build_details, config.default_recomputefile, software_recomputefile_path)

        print "Base VM: {}".format(base_vm)
        print "Base Vagrantfile: {}".format(base_vagrantfile_path)
        print "Vagrantfile @ {}".format(software_vagrantfile_path)
        print "Vagrantbox @ {}".format(software_vagrantbox_path)
        print "Recomputefile @ {}".format(software_recomputefile_path)

        return True
