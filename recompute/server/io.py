import subprocess
import os
import shutil
import json
import re
import time

import boxes
import defaults

recomputations_dir = "recompute/server/recomputations"
logs_dir = "recompute/server/logs"
base_boxes_dir = "recompute/server/boxes"


def create_recomputations_dir():
    if not os.path.exists(recomputations_dir):
        os.makedirs(recomputations_dir)


def create_logs_dir():
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)


def get_recomputation_dir(name):
    """
    Return the path of the recomputation directory

    :param name: Recomputation
    """

    return "{dir}/{name}".format(dir=recomputations_dir, name=name)


def get_log_dir(name):
    """
    Return the path of the recomputation log directory
    """

    return "{dir}/{name}".format(dir=logs_dir, name=name)


def get_recomputation_vm_dir(name, tag, version):
    return "{dir}/vms/{tag}_{version}".format(dir=get_recomputation_dir(name), tag=tag, version=version)


def create_recomputation_dir(name):
    recomputation_dir = get_recomputation_dir(name)
    if not os.path.exists(recomputation_dir):
        os.makedirs(recomputation_dir)

    log_dir = get_log_dir(name)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)


def create_recomputation_vm_dir(name, tag, version):
    recomputation_build_dir = get_recomputation_vm_dir(name, tag, version)
    if not os.path.exists(recomputation_build_dir):
        os.makedirs(recomputation_build_dir)


def get_log_file(name):
    """
    Return a new log file name for the recomputation
    """
    return "{dir}/{name}/{time}.txt".format(dir=logs_dir, name=name, time=time.strftime("%Y%m%d-%H%M%S"))


def get_base_vm_url(box):
    return boxes.BASE_BOXES_URL[box]


def get_base_vm_version(box):
    for base_box in get_base_vms_list():
        if base_box["name"] == box:
            return base_box["version"]


def get_vagrantfile(name, tag, version):
    return "{dir}/Vagrantfile".format(dir=get_recomputation_vm_dir(name, tag, version))


def get_recomputefile(name):
    return "{dir}/{name}.recompute.json".format(dir=get_recomputation_dir(name), name=name)


def get_vagrantfile_template(language):
    if language in defaults.vagrantfile_templates_dict:
        return "{dir}/{template}".format(dir=base_boxes_dir, template=defaults.vagrantfile_templates_dict[language])
    else:
        return None


def get_next_build_version(name):
    recompute_dict = read_recomputefile(name)
    if recompute_dict is None:
        return 0
    else:
        return recompute_dict["vms"][0]["version"] + 1


def get_file_if_exists(recomputation_name, filename):
    path = "{dir}/{filename}".format(dir=get_recomputation_dir(recomputation_name), filename=filename)
    if os.path.isfile(path):
        return path
    else:
        return None


def get_vm_path(name, tag, version):
    return get_file_if_exists(name, "vms/{tag}_{version}/{name}.box".format(tag=tag, version=version, name=name))


def get_vm_name(name, provider="VirtualBox"):
    return "{name}.box".format(name=name)


def get_file_size(path):
    if path is None or not os.path.isfile(path):
        return 0
    else:
        return os.path.getsize(path)


def get_latest_log_file(name):
    """
    Returns the latest log file for the recomputation
    """

    recomputation_log_dir = "{dir}/{name}".format(dir=logs_dir, name=name)
    log_file_list = list()
    for log_filename in next(os.walk(recomputation_log_dir))[2]:
        log_file_list.append(log_filename)
    log_file_list.sort()
    return "{dir}/{name}/{log}".format(dir=logs_dir, name=name, log=log_file_list[0])


def get_newest_vm(name):
    recompute_dict = read_recomputefile(name)
    return recompute_dict["vms"][0]


def read_recomputefile(name):
    """
    Returns a Dictionary representation of the recomputation
    """

    recompute_file = get_file_if_exists(name, "{name}.recompute.json".format(name=name))

    if recompute_file is None:
        return None
    else:
        with open(recompute_file) as recomputation_file:
            return json.load(recomputation_file)


def get_all_recomputations_summary(count=0):
    """
    Returns a list of dictionaries, each representing a recomputation, ordered by decreasing ids
    """

    recomputations_summary = list()
    for recomputation in next(os.walk(recomputations_dir))[1]:
        recompute_dict = read_recomputefile(recomputation)
        if recompute_dict is not None:
            recomputations_summary.append(recompute_dict)
    recomputations_summary.sort(key=lambda r: r["id"])

    ordered_by_ids = list(reversed(recomputations_summary))

    if count != 0:
        return ordered_by_ids[:count]
    else:
        return ordered_by_ids


def get_next_recomputation_id():
    recomputation_summary = get_all_recomputations_summary()
    if len(recomputation_summary) == 0:
        return 0
    else:
        return recomputation_summary[0]["id"] + 1


def get_recomputations_count():
    if os.path.exists(recomputations_dir):
        count = 0
        for recomputation in next(os.walk(recomputations_dir))[1]:
            recompute_dict = read_recomputefile(recomputation)
            if recompute_dict is not None:
                count += 1
        return count
    else:
        return 0


def remove_failed_recomputations():
    # for each recomputation directory (name)
    for recomputation in next(os.walk(recomputations_dir))[1]:
        recompute_dict = read_recomputefile(recomputation)
        if recompute_dict is None:
            shutil.rmtree("{dir}/{name}".format(dir=recomputations_dir, name=recomputation))
            server_log_info("Removed {}.".format(recomputation))


def remove_logs():
    for recomputation in next(os.walk(logs_dir))[1]:
        shutil.rmtree("{dir}/{name}".format(dir=logs_dir, name=recomputation))


def exists_recomputation(name):
    return os.path.exists(get_recomputation_dir(name))


def destroy_recomputation(name):
    shutil.rmtree(get_recomputation_dir(name), ignore_errors=True)


def destroy_vm(name, tag, version):
    # update recomputefile
    recompute_dict = read_recomputefile(name)
    recompute_dict["releases"] = [release for release in recompute_dict["releases"] if
                                  release["tag"] != tag and release["version"] != version]

    recomputefile_path = get_recomputefile(name)
    with open(recomputefile_path, "w") as recomputef:
        recomputef.write(json.dumps(recompute_dict, indent=4, sort_keys=True))

    # remove build directory
    shutil.rmtree(get_recomputation_vm_dir(name, tag, version), ignore_errors=True)


def get_all_boxes_summary():
    # TODO get rid of hardcoded
    return [{"language": "python", "version": "2.7"}, {"language": "c/c++"}, {"language": "node.js", "version": "0.10"},
            {"language": "gap", "version": "4.7.8"}, {"language": "gecode", "version": "4.4.0"}]


def get_base_vms_list():
    """
    Return a list of vagrantboxes installed, where each element in a dictionary containing the name, provider, and version
    of the vagrantbox.
    """

    output = execute("vagrant box list")
    # 'vagrant box list' returns something like
    # ubuntu/trusty64                                                 (virtualbox, 20150609.0.9)
    # ubuntu/trusty64                                                 (virtualbox, 20150814.0.1)
    # ubuntu/trusty64                                                 (virtualbox, 20150817.0.0)

    vagrantboxes = [re.sub("[(),]", "", line).split() for line in output.split("\n") if line]
    # get rid of repeating white spaces and brackets, so we are left with something like
    # [['ubuntu/trusty64', 'virtualbox', '20150609.0.9'],
    #  ['ubuntu/trusty64', 'virtualbox', '20150814.0.1'],
    #  ['ubuntu/trusty64', 'virtualbox', '20150817.0.0']]
    # "if line" to get rid of the trailing empty line

    vagrantboxes_list = list()

    for vagrantbox in vagrantboxes:
        box_vars = dict()
        box_vars["name"] = vagrantbox[0]
        box_vars["provider"] = vagrantbox[1]
        box_vars["version"] = vagrantbox[2]
        vagrantboxes_list.append(box_vars)

    return vagrantboxes_list


def update_base_vagrantboxes():
    base_vms_list = get_base_vms_list()
    base_boxes_list = [box[0] for box in boxes.BASE_BOXES]
    current_base_vms = [vm for vm in base_vms_list if vm["name"] in base_boxes_list]

    for base_vm in current_base_vms:
        name = base_vm["name"]
        provider = base_vm["provider"]
        version = base_vm["version"]

        output = execute("vagrant box update --box {name} --provider {}".format(name=name, provider=provider))
        # 'vagrant box update --box BOX' returns something like
        # ... Successfully added box 'ubuntu/trusty64' (v20150818.0.0) for 'virtualbox'!
        # or
        # ... Box 'ubuntu/trusty64' (v20150818.0.0) is running the latest version.
        #
        if any("Successfully added box" in line for line in output.split("\n")):
            # remove old version
            execute("vagrant box remove {name} --box-version {version} --provider {provider}".format(name=name,
                                                                                                     version=version,
                                                                                                     provider=provider))


def execute(command, cwd=None):
    output = ""

    p = subprocess.Popen(command.split(), cwd=cwd, stdout=subprocess.PIPE)
    while True:
        line = p.stdout.readline()

        if line == '' and p.poll() is not None:
            break

        if line != '':
            output += output

    return output


def server_log_info(task, info=""):
    time_string = time.strftime("%Y-%m-%d %H:%M:%S")
    print "\033[94m$ Recompute {time} [{task}] \033[0m{info}".format(time=time_string, task=task, info=info)


def server_log_error(task, error=""):
    time_string = time.strftime("%Y-%m-%d %H:%M:%S")
    print "\033[95m$ Recompute {time} [{task}] \033[0m{error}".format(time=time_string, task=task, error=error)
