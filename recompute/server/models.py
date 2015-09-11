import json


class RecomputationObject(object):
    def __init__(self, name, github_obj, box, box_url, box_version, memory, cpus, tag, version, date):
        self.id = None
        self.name = name
        self.github_obj = github_obj
        self.box = box
        self.box_url = box_url
        self.box_version = box_version
        self.memory = memory
        self.cpus = cpus
        self.tag = tag
        self.version = version
        self.date = date

    def to_pretty_json(self, old_recompute_dict=None):
        recomputation_vars = dict()
        recomputation_vars["id"] = self.id
        recomputation_vars["name"] = self.name
        recomputation_vars["vms"] = list()
        vm = dict()
        vm["box"] = self.box
        vm["box_url"] = self.box_url
        vm["box_version"] = self.box_version
        vm["github_url"] = self.github_obj.github_url
        vm["github_commit"] = self.github_obj.latest_commit
        vm["tag"] = self.tag
        vm["version"] = self.version
        vm["date"] = self.date
        recomputation_vars["vms"].append(vm)
        if old_recompute_dict is not None:
            recomputation_vars["vms"] = recomputation_vars["vms"] + old_recompute_dict["vms"]
        return json.dumps(recomputation_vars, indent=4, sort_keys=True)
