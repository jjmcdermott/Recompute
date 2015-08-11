import json


class Recomputation(object):
    def __init__(self, id, name, github_url, release):
        self.id = id
        self.name = name
        self.github_url = github_url
        self.release = release

    def to_json_pretty(self):
        recomputation_vars = dict()
        recomputation_vars["id"] = self.id
        recomputation_vars["name"] = self.name
        recomputation_vars["github_url"] = self.github_url
        recomputation_vars["releases"] = list()
        recomputation_vars["releases"].append(self.release.to_dict())
        return json.dumps(recomputation_vars, indent=4, sort_keys=True)


class Release(object):
    def __init__(self, tag, version, date, build):
        self.tag = tag
        self.version = version
        self.date = date
        self.build = build

    def to_dict(self):
        release_vars = dict()
        release_vars["tag"] = self.tag
        release_vars["version"] = self.version
        release_vars["date"] = self.date
        release_vars["box"] = self.build.box
        release_vars["box_url"] = self.build.box_url
        release_vars["box_version"] = self.build.box_version
        release_vars["github_url"] = self.build.github_url
        release_vars["github_commit"] = self.build.github_commit
        return release_vars


class Build(object):
    def __init__(self, box, box_url, box_version, language, language_ver, github_url, github_repo_name, github_commit,
                 add_apts, apt_gets, installs, tests, memory, cpus):
        self.box = box
        self.box_url = box_url
        self.box_version = box_version
        self.language = language
        self.language_version = language_ver
        self.github_url = github_url
        self.github_repo_name = github_repo_name
        self.github_commit = github_commit
        self.add_apts = add_apts
        self.apt_gets = apt_gets
        self.installs = installs
        self.tests = tests
        self.memory = memory
        self.cpus = cpus
