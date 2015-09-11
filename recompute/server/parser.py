import requests
import yaml
import bs4


class TravisObject(object):
    def __init__(self):
        self.add_apt_repositories_list = None
        self.apt_get_installs_list = None
        self.install_scripts_list = None
        self.test_scripts_list = None


class GitHubObject(object):
    def __init__(self, github_url):
        self.github_url = github_url
        self.user = github_url.split("/")[-2]
        self.repo_name = github_url.split("/")[-1]
        self.programming_language = None
        self.programming_language_version = None
        self.latest_commit = None
        self.travis_obj = None


class GitHubParser(object):
    @classmethod
    def parse(cls, github_url):
        travis_script = GitHubParser.get_travis_script(github_url)
        github_page = GitHubParser.get_github_page_contents(github_url)

        github_obj = GitHubObject(github_url)

        lang, ver = GitHubParser.__get_programming_language(travis_script, github_page)
        github_obj.programming_language = lang
        github_obj.programming_language_version = ver

        github_obj.latest_commit = GitHubParser.__get_github_commit_sha(github_page)

        travis_obj = TravisObject()
        travis_obj.add_apt_repositories = GitHubParser.__get_add_apt_repositories(travis_script)
        travis_obj.apt_get_installs_list = GitHubParser.__get_apt_get_installs(travis_script)
        travis_obj.install_scripts_list = GitHubParser.__get_install_scripts(github_obj.repo_name, travis_script)
        travis_obj.test_scripts_list = GitHubParser.__get_test_scripts(travis_script)

        github_obj.travis_obj = travis_obj

        return github_obj

    @classmethod
    def get_travis_script(cls, github_url):
        user = github_url.split("/")[-2]
        repo = github_url.split("/")[-1]
        raw_travis_url = "https://raw.githubusercontent.com/" + user + "/" + repo + "/master/.travis.yml"
        travis_script = requests.get(raw_travis_url)
        if travis_script.status_code < 400:
            return yaml.load(travis_script.text)
        else:
            return None

    @classmethod
    def get_github_page_contents(cls, github_url):
        response = requests.get(github_url)
        return response.text

    @classmethod
    def __get_programming_language(cls, travis_script, github_page):
        if travis_script is not None:
            language = travis_script["language"]
            if language in travis_script:
                return language, travis_script[language][-1]
        else:
            soup = bs4.BeautifulSoup(github_page)
            language = soup.find("span", {"class": "lang"}).text.lower()

        return language, None

    @classmethod
    def __get_github_commit_sha(cls, github_page):
        soup = bs4.BeautifulSoup(github_page)
        return soup.find("a", {"class": "message"})["href"].split("/")[-1]

    @classmethod
    def __get_add_apt_repositories(cls, travis_script):
        apt_repositories_list = list()

        if travis_script is not None:
            if "before_install" in travis_script:
                travis_before_install = travis_script["before_install"]
                for add_apt_repo in [line for line in travis_before_install if "add-apt-repository" in line]:
                    repositories = [repo for repo in add_apt_repo.split(" ") if repo.startswith("ppa:")]
                    apt_repositories_list.extend(repositories)

        return apt_repositories_list

    @classmethod
    def __get_apt_get_installs(cls, travis_script):
        apt_installs_list = list()

        if travis_script is not None:
            if "before_install" in travis_script:
                for apt_get_install in [line for line in travis_script["before_install"] if "apt-get install" in line]:
                    packages = [p for p in apt_get_install.split(" ") if p not in ["sudo", "apt-get", "install", "-y"]]
                    apt_installs_list.extend(packages)

            if "addons" in travis_script and "apt_packages" in travis_script["addons"]:
                apt_installs_list.extend(travis_script["addons"]["apt_packages"])

        return apt_installs_list

    @classmethod
    def __get_install_scripts(cls, language, travis_script):
        install_scripts_list = list()

        if travis_script is not None:
            if "install" in travis_script:
                install_list = travis_script["install"]
                if language == "haskell":
                    install_list = [install.replace("dependencies-only", "only-dependencies") for install in
                                    install_list]
                    install_list = ["$VAGRANT_USER '{install}'".format(install=install) for install in install_list]
                install_scripts_list.extend(install_list)

        return install_scripts_list

    @classmethod
    def __get_test_scripts(cls, travis_script):
        envs = list()
        before_scripts = list()
        test_scripts = list()

        if travis_script is not None:
            if "before_script" in travis_script:
                before_scripts.extend(travis_script["before_script"])

            if "script" in travis_script:
                test_scripts.extend(travis_script["script"])

            if "env" in travis_script:
                envs.extend(travis_script["env"])

        # clean up
        final_test_scripts_list = [script for script in before_scripts]
        # non-tests statements
        final_test_scripts_list.extend([s for s in test_scripts if not any(env.split("=", 1)[0] in s for env in envs)])
        # tests statements, interpolated with different env variables
        for env in envs:
            final_test_scripts_list.append(str("export " + env))
            final_test_scripts_list.extend([s for s in test_scripts if env.split("=", 1)[0] in s])

        return final_test_scripts_list
