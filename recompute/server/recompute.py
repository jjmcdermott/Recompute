"""
Recompute a project
"""

import shutil
import requests
import yaml
import datetime
import bs4
from . import config
from . import io
from . import recomputation
from . import defaults
from . import boxes


def __make_recomputefile(recomputation_summary):
    recomputefile_path = io.get_recomputefile_path(recomputation_summary.name)
    with open(recomputefile_path, "w") as rfile:
        rfile.write("{}".format(recomputation_summary.to_json_pretty()))

    return True


def __make_vagrantbox(recomputation_summary):
    name = recomputation_summary.name
    tag = recomputation_summary.release.tag
    version = recomputation_summary.release.version

    vagrantbox = name + ".box"

    recomputation_dir = io.get_recomputation_dir(name)
    recomputation_build_dir = io.get_recomputation_build_dir(name, tag, version)

    success = io.execute(["vagrant", "up", "--provision"], recomputation_dir)
    if success:
        io.execute(["vagrant", "package", "--output", vagrantbox], recomputation_dir)
        io.execute(["vagrant", "destroy", "-f"], recomputation_dir)
        io.execute(["vagrant", "box", "add", "--force", name, vagrantbox], recomputation_dir)

        io.remove_vagrantbox_cache(name)
        io.create_recomputation_vms_dir(name)
        io.create_recomputation_build_dir(name, tag, version)
        shutil.move(recomputation_dir + "/" + vagrantbox, recomputation_build_dir + "/" + vagrantbox)

    return success


def __make_vagrantfile(recomputation_summary):
    language = recomputation_summary.release.build.language

    if language in defaults.vagrantfile_templates_dict:
        vagrantfile_template = io.get_vagrantfile_template_path(defaults.vagrantfile_templates_dict[language])
    else:
        return False

    with open(vagrantfile_template, "r") as f:
        vagrantfile = f.read()

    vagrantfile = vagrantfile.replace("<NAME>", recomputation_summary.name)

    build = recomputation_summary.release.build

    vagrantfile = vagrantfile.replace("<BOX>", build.box)
    vagrantfile = vagrantfile.replace("<LANGUAGE_VERSION>", build.language_version)

    vagrantfile = vagrantfile.replace("<GITHUB_URL>", build.github_url)
    vagrantfile = vagrantfile.replace("<GITHUB_REPO_NAME>", build.github_repo_name)

    vagrantfile = vagrantfile.replace("<ADD_APT_REPOSITORIES>", build.add_apts)
    vagrantfile = vagrantfile.replace("<APT_GET_INSTALL>", build.apt_gets)
    vagrantfile = vagrantfile.replace("<INSTALL_SCRIPT>", build.installs)
    vagrantfile = vagrantfile.replace("<TEST_SCRIPT>", build.tests)

    vagrantfile = vagrantfile.replace("<MEMORY>", str(build.memory))
    vagrantfile = vagrantfile.replace("<CPUS>", str(build.cpus))

    vagrantfile_path = io.get_vagrantfile_path(recomputation_summary.name)
    with open(vagrantfile_path, "w") as f:
        f.write("{}".format(vagrantfile))

    return True


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
        language = travis_script["language"]
    else:
        response = requests.get(github_url)
        soup = bs4.BeautifulSoup(response.text)
        language = soup.find("span", {"class": "lang"}).text.lower()

    if travis_script is not None:
        if language in travis_script:
            return language, travis_script[language][-1]
    if language in defaults.languages_version_dict:
        return language, defaults.languages_version_dict[language]
    else:
        return None, None


def __get_github_commit_sha(github_url):
    response = requests.get(github_url)
    soup = bs4.BeautifulSoup(response.text)
    return soup.find("a", {"class": "sha-block"})["href"].split("/")[-1]


def __get_add_apts_repositories(travis_script):
    apt_repositories = list()

    if travis_script is not None:
        if "before_install" in travis_script:
            travis_before_install = travis_script["before_install"]
            for add_apt_repo in [line for line in travis_before_install if "add-apt-repository" in line]:
                repositories = [repo for repo in add_apt_repo.split(" ") if repo.startswith("ppa:")]
                apt_repositories.extend(repositories)

    return "\n".join(["add-apt-repository -y " + repo for repo in apt_repositories])


def __get_apt_get_installs(travis_script):
    apt_installs = list()

    if travis_script is not None:
        if "before_install" in travis_script:
            travis_before_install = travis_script["before_install"]
            # apt-get install
            for apt_get_install in [line for line in travis_before_install if "apt-get install" in line]:
                packages = [p for p in apt_get_install.split(" ") if p not in ["sudo", "apt-get", "install", "-y"]]
                apt_installs.extend(packages)

        if "addons" in travis_script and "apt_packages" in travis_script["addons"]:
            apt_installs.extend(travis_script["addons"]["apt_packages"])

    return " ".join(apt_installs) + "\n"


def __get_install_scripts(recomputation_name, language, travis_script):
    install_scripts = list()

    if travis_script is not None:
        if "install" in travis_script:
            install_scripts.extend(travis_script["install"])
    else:
        install_scripts.extend(defaults.languages_install_dict[language])

    # extra stuff for individual recomputations
    if recomputation_name in defaults.boxes_install_scripts:
        install_scripts.extend(defaults.boxes_install_scripts[recomputation_name])

    return "\n  ".join(install_scripts)


def __get_test_scripts(travis_script):
    envs = list()
    test_scripts = list()

    if travis_script is not None:
        if "env" in travis_script:
            envs.extend(travis_script["env"])

        if "script" in travis_script:
            test_scripts.extend(travis_script["script"])

    # clean up
    final_test_scripts = list()
    # non-tests statements
    final_test_scripts.extend([s for s in test_scripts if not any(env.split("=", 1)[0] in s for env in envs)])
    # tests statements, interpolated with different env variables
    for env in envs:
        final_test_scripts.append(str("export " + env))
        final_test_scripts.extend([s for s in test_scripts if env.split("=", 1)[0] in s])

    return " \n".join(final_test_scripts)


def __gather_recomputation_summary(name, github_url, box):
    """
    """

    id = config.recomputations_count

    box_url = boxes.RECOMPUTE_BOXES_URL[box]
    box_version = "TODO"

    travis_script = __get_travis_script(github_url)

    language, language_version = __get_language(travis_script, github_url)
    if language is None:
        raise UnknownLanguageException()

    github_repo_name = github_url.split("/")[-1]
    github_commit = __get_github_commit_sha(github_url)

    add_apts = __get_add_apts_repositories(travis_script)
    apt_gets = __get_apt_get_installs(travis_script)
    installs = __get_install_scripts(name, language, travis_script)
    tests = __get_test_scripts(travis_script)

    memory = defaults.vm_memory
    cpus = defaults.vm_cpus

    tag = "Latest"
    version = "0"
    date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    build = recomputation.Build(box, box_url, box_version, language, language_version, github_url, github_repo_name,
                                github_commit, add_apts, apt_gets, installs, tests, memory, cpus)
    release = recomputation.Release(tag, version, date, build)

    return recomputation.Recomputation(id, name, github_url, release)


def create_vm(name, github_url, box):
    io.create_new_recomputation_dir(name)

    try:
        recomputation_summary = __gather_recomputation_summary(name, github_url, box)
    except UnknownLanguageException:
        io.destroy_recomputation(name)
        return False, "Did not understand the project programming language."

    if not __make_vagrantfile(recomputation_summary):
        io.destroy_recomputation(name)
        return False, "Vagrantfile cannot be generated."

    if not __make_vagrantbox(recomputation_summary):
        io.destroy_recomputation(name)
        return False, "Vagrantbox was not created."

    if not __make_recomputefile(recomputation_summary):
        io.destroy_recomputation(name)
        return False, "Recomputefile was not created."

    print "Recomputed: {name} @ {dir}".format(name=name, dir=io.get_recomputation_dir(name))
    config.recomputations_count += 1

    return True, "Successful."


class UnknownLanguageException(Exception):
    pass
