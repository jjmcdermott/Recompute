"""
Accessing recomputation files, Vagrantboxes and Vagrantfiles
"""

import subprocess
import sys
import os
import shutil
import json

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

    return get_file_if_exists(name, "Vagrantfile", False)


def get_vagrantbox_relative(name, tag="Latest", version="0"):
    """
    Used to download Vagrantbox

    :param name: Recomputation
    """

    return get_file_if_exists(name, "vms/{tag}_{version}/{name}.box".format(tag=tag, version=version, name=name), False)


def get_recomputation_summary(name):
    with open(get_file_if_exists(name, name + ".recompute.json", True)) as recomputation_file:
        return json.load(recomputation_file)


def get_all_recomputations_summary():
    recomputations_summary = list()
    # for each recomputation directory (name)
    for recomputation in next(os.walk(recomputations_dir))[1]:
        recomputations_summary.append(get_recomputation_summary(recomputation))
    recomputations_summary.sort(key=lambda r: r["id"])
    return recomputations_summary


def get_latest_recomputations_summary(count):
    """
    :param count: The number of recomputations summary to return
    """

    recomputation_list = get_all_recomputations_summary()
    return list(reversed(recomputation_list[-count:]))


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


def get_all_boxes_summary():
    # TODO get rid of hardcoded
    return [{"language": "python", "version": "2.7"}, {"language": "c/c++"}, {"language": "node.js", "version": "0.10"},
            {"language": "gap", "version": "4.7.8"}, {"language": "gecode", "version": "4.4.0"}]


def update_vagrantboxes():
    execute(["vagrant", "box", "update"], recomputations_dir)


def execute(command, cwd):
    print command
    p = subprocess.Popen(command, cwd=cwd, stdout=subprocess.PIPE)
    while True:
        out = p.stdout.read(1)
        if out == '' and p.poll() is not None:
            break
        if out != '':
            sys.stdout.write(out)
            sys.stdout.flush()
    rcode = p.returncode
    if rcode == 0:
        return True
    else:
        return False
