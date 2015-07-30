import subprocess
import os
import sys
import shutil
import requests
import yaml
import datetime
import bs4
from . import config
from . import file
from . import recomputation
from . import recompute_learn


def __execute(command, cwd):
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


def __make_recomputefile(recomputation_data, recomputefile):
    recomputefile_json = recomputation_data.to_json()

    with open(recomputefile, "w") as rfile:
        rfile.write("{0}".format(recomputefile_json))


def __make_vagrantbox(recomputation_data):
    recomputation_name = recomputation_data.name
    vagrantbox = recomputation_name + ".box"
    recomputation_dir = file.get_recomputation_absolute_dir(recomputation_name)
    recomputation_vm_dir = recomputation_dir + "vm/"

    success = __execute(["vagrant", "up", "--provision"], recomputation_dir)
    if success:
        __execute(["vagrant", "package", "--output", vagrantbox], recomputation_dir)
        __execute(["vagrant", "destroy"], recomputation_dir)
        __execute(["mkdir", "vm"], recomputation_dir)
        __execute(["cp", vagrantbox, "vm/"], recomputation_dir)
        __execute(["vagrant", "init", vagrantbox], recomputation_vm_dir)
        __execute(["vagrant", "up"], recomputation_vm_dir)

    return success


def __make_vagrantfile(recomputation_data, vagrantfile_template, vagrantfile):
    with open(vagrantfile_template, "r") as vtemplate:
        contents = vtemplate.read()

    contents = contents.replace("<NAME>", recomputation_data.name)

    build = recomputation_data.release.build

    contents = contents.replace("<BOX>", build.box)
    contents = contents.replace("<LANGUAGE_VERSION>", build.language_version)

    contents = contents.replace("<GITHUB_URL>", build.github_url)
    contents = contents.replace("<GITHUB_REPO_NAME>", build.github_repo_name)

    contents = contents.replace("<ADD_APT_REPOSITORIES>", build.add_apts)
    contents = contents.replace("<APT_GET_INSTALL>", build.apt_gets)
    contents = contents.replace("<INSTALL_SCRIPT>", build.installs)
    contents = contents.replace("<TEST_SCRIPT>", build.tests)

    contents = contents.replace("<MEMORY>", str(build.memory))
    contents = contents.replace("<CPUS>", str(build.cpus))

    with open(vagrantfile, "w") as vfile:
        vfile.write("{0}".format(contents))


def __get_vagrantfile_template(language):
    if language in recompute_learn.vagrantfile_templates_dict:
        return file.template_vagrantfiles_dir_absolute + recompute_learn.vagrantfile_templates_dict[language]
    else:
        return None


def __get_travis_script(github_url):
    user = github_url.split("/")[-2]
    repo = github_url.split("/")[-1]
    raw_travis_url = "https://raw.githubusercontent.com/" + user + "/" + repo + "/master/.travis.yml"
    travis_script = requests.get(raw_travis_url)
    if travis_script.status_code < 400:
        return yaml.load(travis_script.text)
    else:
        return None


def __get_language(travis_script, github_url):
    if travis_script is not None:
        return travis_script["language"]
    else:
        response = requests.get(github_url)
        soup = bs4.BeautifulSoup(response.text)
        return soup.find("span", {"class": "lang"}).text.lower()


def __get_language_version(travis_script, language):
    if travis_script is not None:
        if language in travis_script:
            return travis_script[language][-1]
    if language in recompute_learn.default_languages_version_dict:
        return recompute_learn.default_languages_version_dict[language]
    else:
        return None


def __get_recomputation_data(id, name, github_url, box):
    """
    """

    travis_script = __get_travis_script(github_url)

    box_version = "TODO"

    language = __get_language(travis_script, github_url)
    language_ver = __get_language_version(travis_script, language)

    github_repo_name = github_url.split("/")[-1]
    github_commit = "TODO"

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

            # apt-get install
            for apt_get_install in [line for line in travis_before_install if "apt-get install" in line]:
                packages = [p for p in apt_get_install.split(" ") if p not in ["sudo", "apt-get", "install", "-y"]]
                apt_install_packages.extend(packages)

        # apt-get install
        if "addons" in travis_script and "apt_packages" in travis_script["addons"]:
            apt_install_packages.extend(travis_script["addons"]["apt_packages"])

        if "install" in travis_script:
            install_scripts.extend(travis_script["install"])

        if "env" in travis_script:
            envs.extend(travis_script["env"])

        if "script" in travis_script:
            test_scripts.extend(travis_script["script"])

    else:
        install_scripts.extend(recompute_learn.default_languages_installs_dict[language])

    # clean up
    final_test_scripts = list()
    # non-tests statements
    final_test_scripts.extend([s for s in test_scripts if not any(env.split("=", 1)[0] in s for env in envs)])
    # tests statements, interpolated with different env variables
    for env in envs:
        final_test_scripts.append(str("export " + env))
        final_test_scripts.extend([s for s in test_scripts if env.split("=", 1)[0] in s])

    add_apts = "\n".join(["add-apt-repository -y " + repo for repo in add_apt_repositories])
    apt_gets = " ".join(apt_install_packages) + "\n"
    installs = " \n".join(install_scripts)
    tests = " \n".join(final_test_scripts)

    memory = recompute_learn.default_memory
    cpus = recompute_learn.default_cpus

    build = recomputation.Build(box, box_version, language, language_ver, github_url, github_repo_name,
                                github_commit, add_apts, apt_gets, installs, tests, memory, cpus)

    tag = "Latest"
    version = "0"
    date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    release = recomputation.Release(tag, version, date, build)

    recomputation_data = recomputation.Recomputation(id, name, github_url, release)

    return recomputation_data


def create_vm(name, github_url, box):
    recomputation_dir = file.get_recomputation_absolute_dir(name)
    vagrantfile = recomputation_dir + "Vagrantfile"
    recomputefile = recomputation_dir + name + ".recompute.json"

    os.makedirs(recomputation_dir)

    recomputation_data = __get_recomputation_data(config.recomputations_count, name, github_url, box)

    language = recomputation_data.release.build.language
    vagrantfile_template = __get_vagrantfile_template(language)
    if vagrantfile_template is None:
        os.rmdir(recomputation_dir)
        return False, "Vagrantfile cannot be generated."

    __make_vagrantfile(recomputation_data, vagrantfile_template, vagrantfile)
    __make_vagrantbox(recomputation_data)
    __make_recomputefile(recomputation_data, recomputefile)

    if not file.exists_vagrantbox(name):
        shutil.rmtree(recomputation_dir, ignore_errors=True)
        return False, "Recomputation was unsuccessful."

    print "Recomputed: {} @ {}".format(name, recomputation_dir)
    config.recomputations_count += 1

    return True, "Successful."
