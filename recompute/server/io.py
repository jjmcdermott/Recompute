"""
Accessing recomputation files, Vagrantboxes and Vagrantfiles
"""

import subprocess
import sys
import os
import shutil
import json
import re
import time
from recompute.server import boxes as recompute_boxes

recomputations_dir = "recompute/server/recomputations"
recomputations_dir_RELATIVE = "recomputations"
logs_dir = "recompute/server/logs"
logs_dir_RELATIVE = "logs"
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


def get_recomputation_dir_relative(name):
    """
    Return the relative path of the recomputation directory
    """

    return "{dir}/{name}".format(dir=recomputations_dir_RELATIVE, name=name)


def get_log_dir(name):
    """
    Return the path of the recomputation log directory
    """

    return "{dir}/{name}".format(dir=logs_dir, name=name)


def create_log_filename(name):
    """
    Return a new log file name for the recomputation
    """
    return "{dir}/{name}/{time}.txt".format(dir=logs_dir, name=name, time=time.strftime("%Y%m%d-%H%M%S"))


def create_new_recomputation_dir(name):
    recomputation_dir = get_recomputation_dir(name)
    if not os.path.exists(recomputation_dir):
        os.makedirs(recomputation_dir)

    return recomputation_dir


def create_new_log_dir(name):
    log_dir = get_log_dir(name)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)


def get_recomputation_build_dir(name, tag, version):
    return "{dir}/vms/{tag}_{version}".format(dir=get_recomputation_dir(name), tag=tag, version=version)


def create_recomputation_build_dir(name, tag, version):
    recomputation_build_dir = get_recomputation_build_dir(name, tag, version)
    if not os.path.exists(recomputation_build_dir):
        os.makedirs(recomputation_build_dir)

    return recomputation_build_dir


def get_vagrantfile_path(name):
    return "{dir}/Vagrantfile".format(dir=get_recomputation_dir(name))


def get_recomputefile_path(name):
    return "{dir}/{name}.recompute.json".format(dir=get_recomputation_dir(name), name=name)


def get_vagrantfile_template_path(template):
    return "{dir}/{template}".format(dir=base_boxes_dir, template=template)


def get_file_if_exists(recomputation_name, filename, absolute_path=True):
    recomputation_dir = get_recomputation_dir(recomputation_name)
    recomputation_dir_relative = get_recomputation_dir_relative(recomputation_name)

    if os.path.exists(recomputation_dir) and os.path.isfile(recomputation_dir + "/" + filename):
        if absolute_path:
            return "{dir}/{filename}".format(dir=recomputation_dir, filename=filename)
        else:
            return "{dir}/{filename}".format(dir=recomputation_dir_relative, filename=filename)
    else:
        return None


def get_vagrantfile_relative(name):
    """
    Return the file path of the recomputation Vagrantfile (for download)

    :param name: Recomputation
    """

    return get_file_if_exists(name, "Vagrantfile", absolute_path=False)


def get_vagrantbox_relative(name, tag, version):
    """
    Return the file path of the recomputation Vagrantbox (for download)
    """

    return get_file_if_exists(name, "vms/{tag}_{version}/{name}.box".format(tag=tag, version=version, name=name),
                              absolute_path=False)


def move_vagrantfile_to_build_dir(name, tag, version):
    old_vagrantfile = "{dir}/Vagrantfile".format(dir=get_recomputation_dir(name))
    new_vagrantfile = "{dir}/boxVagrantfile".format(dir=get_recomputation_build_dir(name, tag, version))
    shutil.move(old_vagrantfile, new_vagrantfile)


def move_vagrantbox_to_build_dir(name, tag, version, box_name):
    old_vagrantbox = "{dir}/{box}".format(dir=get_recomputation_dir(name), box=box_name)
    new_vagrantbox = "{dir}/{box}".format(dir=get_recomputation_build_dir(name, tag, version), box=box_name)
    shutil.move(old_vagrantbox, new_vagrantbox)


def get_latest_log_file(name):
    """
    Return the latest log file for the recomputation

    :param name: Recomputation
    """

    recomputation_log_dir = "{dir}/{name}".format(dir=logs_dir, name=name)
    log_file_list = list()

    for log_filename in next(os.walk(recomputation_log_dir))[2]:
        log_file_list.append(log_filename)
    log_file_list.sort()

    return "{dir}/{name}/{log}".format(dir=logs_dir_RELATIVE, name=name, log=log_file_list[0])


def read_recomputefile(name):
    """
    Return a Dictionary representation of the recomputation
    """

    recompute_file = get_file_if_exists(name, "{name}.recompute.json".format(name=name), absolute_path=True)

    if recompute_file is None:
        return None
    else:
        with open(recompute_file) as recomputation_file:
            return json.load(recomputation_file)


def get_all_recomputations_summary():
    """
    Return a list of dictionaries, each representing a recomputation, ordered by decreasing ids
    """

    recomputations_summary = list()
    for recomputation in next(os.walk(recomputations_dir))[1]:
        recompute_dict = read_recomputefile(recomputation)
        if recompute_dict is not None:
            recomputations_summary.append(recompute_dict)
    recomputations_summary.sort(key=lambda r: r["id"])
    return list(reversed(recomputations_summary))


def get_recomputations_summary(count):
    return get_all_recomputations_summary()[:count]


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


def exists_vagrantbox(name):
    return get_vagrantfile_relative(name) is not None


def remove_failed_recomputations():
    # for each recomputation directory (name)
    for recomputation in next(os.walk(recomputations_dir))[1]:
        recompute_dict = read_recomputefile(recomputation)
        if recompute_dict is None:
            shutil.rmtree("{dir}/{name}".format(dir=recomputations_dir, name=recomputation))
            server_prints("Removed {name}.".format(name=recomputation))


def remove_logs():
    for recomputation in next(os.walk(logs_dir))[1]:
        shutil.rmtree("{dir}/{name}".format(dir=logs_dir, name=recomputation))


def remove_vagrantbox_cache(name):
    shutil.rmtree("{dir}/.vagrant".format(dir=get_recomputation_dir(name)), ignore_errors=True)


def exists_recomputation(name):
    return os.path.exists(get_recomputation_dir(name))


def destroy_recomputation(name):
    shutil.rmtree(get_recomputation_dir(name), ignore_errors=True)


def destroy_build(name, tag, version):
    # update recomputefile
    recompute_dict = read_recomputefile(name)
    recompute_dict["releases"] = [release for release in recompute_dict["releases"] if
                                  release["tag"] != tag and release["version"] != version]

    recomputefile_path = get_recomputefile_path(name)
    with open(recomputefile_path, "w") as recomputef:
        recomputef.write(json.dumps(recompute_dict, indent=4, sort_keys=True))

    # remove build directory
    shutil.rmtree(get_recomputation_build_dir(name, tag, version), ignore_errors=True)


def get_all_boxes_summary():
    # TODO get rid of hardcoded
    return [{"language": "python", "version": "2.7"}, {"language": "c/c++"}, {"language": "node.js", "version": "0.10"},
            {"language": "gap", "version": "4.7.8"}, {"language": "gecode", "version": "4.4.0"}]


def get_base_vagrantboxes_summary():
    """
    Return a list of vagrantboxes installed, where each element in a dictionary containing the name, provider, and version
    of the vagrantbox.
    """

    _, output = execute(["vagrant", "box", "list"], save_output=True)
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
    vagrantboxes_summary = get_base_vagrantboxes_summary()
    base_vagrantboxes_list = [box[0] for box in recompute_boxes.BASE_BOXES]
    base_vagrantboxes_summary = [box for box in vagrantboxes_summary if box["name"] in base_vagrantboxes_list]

    for base_vagrantbox in base_vagrantboxes_summary:
        name = base_vagrantbox["name"]
        provider = base_vagrantbox["provider"]
        version = base_vagrantbox["version"]

        execute(["vagrant", "box", "update", "--box", name, "--provider", provider], save_output=True)
        # 'vagrant box update --box BOX' returns something like
        # ... Successfully added box 'ubuntu/trusty64' (v20150818.0.0) for 'virtualbox'!
        # or
        # ... Box 'ubuntu/trusty64' (v20150818.0.0) is running the latest version.
        #
        # if any("Successfully added box" in line for line in output.split("\n")):
        #     # remove old version
        #     _, _ = execute(["vagrant", "box", "remove", name, "--box-version", version, "--provider", provider])


def execute(command, cwd=None, save_output=False, socket=None, output_file=None):
    print command

    output = ""

    p = subprocess.Popen(command, cwd=cwd, stdout=subprocess.PIPE)
    while True:
        line = p.stdout.readline()

        if line == '' and p.poll() is not None:
            break

        if line != '':
            print line.rstrip()

            if save_output or output_file is not None:
                output += line

            if socket is not None:
                socket.on_progress(line)

    if output_file is not None:
        with open(output_file, "a") as f:
            f.write(output)

    if p.returncode == 0:
        return True, output
    else:
        return False, output


def server_prints(message):
    print "\033[94m$ Recompute: {message}\033[0m".format(message=message)
