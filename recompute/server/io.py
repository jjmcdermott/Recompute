"""
Accessing recomputation files, Vagrantboxes and Vagrantfiles
"""

import subprocess
import sys
import os
import shutil
import json
import re
from . import boxes

recomputations_dir = "recompute/server/recomputations"
recomputations_dir_RELATIVE = "recomputations"
base_boxes_dir = "recompute/server/boxes"


def create_recomputations_dir():
    if not os.path.exists(recomputations_dir):
        os.makedirs(recomputations_dir)

    return recomputations_dir


def get_recomputation_dir(name):
    """
    Return the absolute path of the recomputation directory

    :param name: Recomputation
    """

    return "{dir}/{name}".format(dir=recomputations_dir, name=name)


def get_recomputation_dir_relative(name):
    """
    Return the relative path of the recomputation directory

    :param name: Recomputation
    """

    return "{dir}/{name}".format(dir=recomputations_dir_RELATIVE, name=name)


def create_new_recomputation_dir(name):
    recomputation_dir = get_recomputation_dir(name)
    if not os.path.exists(recomputation_dir):
        os.makedirs(recomputation_dir)

    return recomputation_dir


def get_recomputation_vms_dir(name):
    """
    :param name: Recomputation
    """
    return "{dir}/vms".format(dir=get_recomputation_dir(name), name=name)


def create_recomputation_vms_dir(name):
    recomputation_vms_dir = get_recomputation_vms_dir(name)
    if not os.path.exists(recomputation_vms_dir):
        os.makedirs(recomputation_vms_dir)

    return recomputation_vms_dir


def get_recomputation_build_dir(name, tag, version):
    """
    :param name: Recomputation
    :param tag: Tag
    :param version: Version
    """

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
    Used to download Vagrantfile

    :param name: Recomputation
    """

    return get_file_if_exists(name, "Vagrantfile", absolute_path=False)


def get_vagrantbox_relative(name, tag, version):
    """
    Used to download Vagrantbox

    :param name: Recomputation
    """

    return get_file_if_exists(name, "vms/{tag}_{version}/{name}.box".format(tag=tag, version=version, name=name),
                              absolute_path=False)


def move_vagrantfile_to_build_dir(name, tag, version):
    _, _ = execute(["mv", "Vagrantfile", "vms/{tag}_{version}/boxVagrantfile".format(tag=tag, version=version)],
                   cwd=get_recomputation_dir(name))


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
    recomputations_summary = list()
    # for each recomputation directory (name)
    for recomputation in next(os.walk(recomputations_dir))[1]:
        recompute_dict = read_recomputefile(recomputation)
        if recompute_dict is not None:
            recomputations_summary.append(recompute_dict)
    recomputations_summary.sort(key=lambda r: r["id"])
    return list(reversed(recomputations_summary))


def remove_failed_recomputations():
    # for each recomputation directory (name)
    for recomputation in next(os.walk(recomputations_dir))[1]:
        recompute_dict = read_recomputefile(recomputation)
        if recompute_dict is None:
            shutil.rmtree("{dir}/{name}".format(dir=recomputations_dir, name=recomputation))
            server_prints("Removed {name}.".format(name=recomputation))


def get_latest_recomputations_summary(count):
    """
    :param count: The number of recomputations summary to return
    """

    recomputation_list = get_all_recomputations_summary()
    return recomputation_list[:count]


def get_recomputations_count():
    if os.path.exists(recomputations_dir):
        return len(next(os.walk(recomputations_dir))[1])
    else:
        return 0


def exists_vagrantbox(name):
    return get_vagrantfile_relative(name) is not None


def remove_vagrantbox_cache(name):
    shutil.rmtree("{dir}/.vagrant".format(dir=get_recomputation_dir(name)), ignore_errors=True)


def exists_recomputation(name):
    return os.path.exists(get_recomputation_dir(name))


def destroy_recomputation(name):
    shutil.rmtree(get_recomputation_dir(name), ignore_errors=True)


def destroy_build(name, tag, version):
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
    base_vagrantboxes_list = [box[0] for box in boxes.RECOMPUTE_BOXES]
    base_vagrantboxes_summary = [box for box in vagrantboxes_summary if box["name"] in base_vagrantboxes_list]

    for base_vagrantbox in base_vagrantboxes_summary:
        name = base_vagrantbox["name"]
        provider = base_vagrantbox["provider"]
        version = base_vagrantbox["version"]

        _, output = execute(["vagrant", "box", "update", "--box", name, "--provider", provider], save_output=True)
        # 'vagrant box update --box BOX' returns something like
        # ... Successfully added box 'ubuntu/trusty64' (v20150818.0.0) for 'virtualbox'!
        # or
        # ... Box 'ubuntu/trusty64' (v20150818.0.0) is running the latest version.

        if any("Successfully added box" in line for line in output.split("\n")):
            # remove old version
            _, _ = execute(["vagrant", "box", "remove", name, "--box-version", version, "--provider", provider])


def execute(command, cwd=None, save_output=False, socket=None):
    print command

    output = ""

    p = subprocess.Popen(command, cwd=cwd, stdout=subprocess.PIPE)
    while True:
        out = p.stdout.read(1)

        if out == '' and p.poll() is not None:
            break
        if out != '':
            sys.stdout.write(out)
            sys.stdout.flush()

        if save_output:
            output += out

    if p.returncode == 0:
        return True, output
    else:
        return False, output


def server_prints(message):
    print "\033[94m***Recompute: {message}\033[0m".format(message=message)
