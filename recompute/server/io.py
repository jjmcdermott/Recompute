"""
Accessing recomputation files, Vagrantboxes and Vagrantfiles
"""

import os
import shutil
import json

recomputations_dir = "recompute/server/recomputations"
recomputations_dir_relative = "recomputations"
template_vagrantfiles_dir_absolute = "recompute/server/boxes"


def create_recomputations_dir():
    if not os.path.exists(recomputations_dir):
        os.makedirs(recomputations_dir)


def create_recomputation_vms_dir(name):
    """
    :param name: Recomputation name
    """
    vms_dir = get_recomputation_vms_dir(name)
    if not os.path.exists(vms_dir):
        os.makedirs(vms_dir)


def create_recomputation_build_dir(recomputation_name, tag, version):
    """
    :param tag:
    :param version:
    """
    build_dir = get_recomputation_build_dir(recomputation_name, tag, version)
    if not os.path.exists(build_dir):
        os.makedirs(build_dir)


def get_recomputation_dir(name):
    """
    Return the absolute path of the recomputation directory (inside the project directory i.e. Recompute).

    :param name: Recomputation name
    """

    return "{recomputations_dir}/{name}".format(recomputations_dir=recomputations_dir, name=name)


def get_recomputation_dir_relative(name):
    """
    Return the relative path of the recomputation directory (inside the project directory i.e. Recompute).

    :param name: Recomputation name
    """

    return "{recomputations_dir}/{name}".format(recomputations_dir=recomputations_dir_relative, name=name)


def get_recomputation_vms_dir(name):
    """
    Return the absolute path of the recomputation vms directory (inside the project directory i.e. Recompute).

    :param name: Recomputation name
    """

    return "{{recomputations_dir}/{name}/vms".format(recomputations_dir=recomputations_dir, name=name)


def get_recomputation_build_dir(name, tag, version):
    """
    Return the absolute path of a recomputation vm directory (inside the project directory i.e. Recompute).

    :param name: Recomputation name
    """

    return "{{recomputations_dir}/{name}/vms/{tag}_{version}".format(recomputations_dir=recomputations_dir, name=name,
                                                                     tag=tag, version=version)


def get_file(recomputation_name, filename):
    recomputation_dir = get_recomputation_dir(recomputation_name)
    if os.path.exists(recomputation_dir) and os.path.isfile(recomputation_dir + "/" + filename):
        return "{absolute_recomputation_dir}/{filename}".format(absolute_recomputation_dir=recomputation_dir,
                                                                filename=filename)
    else:
        return None


def get_file_relative(name, filename):
    """
    Get the file's relative path. Used for downloading files.

    :param name: Recomputation name
    """

    absolute_dir = get_recomputation_dir(name)
    relative_dir = get_recomputation_dir_relative(name)
    if os.path.exists(absolute_dir) and os.path.isfile(absolute_dir + "/" + filename):
        return "{relative_recomputation_dir}/{filename}".format(relative_recomputation_dir=relative_dir,
                                                                filename=filename)
    else:
        return None


def get_vagrantfile_relative(name):
    """
    :param name: Recomputation name
    """

    return get_file_relative(name, "Vagrantfile")


def get_vagrantbox_relative(name):
    """
    :param name: Recomputation name
    """

    return get_file_relative(name, name + ".box")


def get_recomputation_summary_file(name):
    """
    :param name: Recomputation name
    """

    return get_file(name, name + ".recompute.json")


def get_recomputation_summary(name):
    """
    :param name: Recomputation name
    """

    with open(get_recomputation_summary_file(name)) as recomputation_file:
        return json.load(recomputation_file)


def get_latest_recomputations_summary(count):
    """
    :param count: The number of recomputations summary to return
    """

    recomputation_list = get_all_recomputations_summary()
    return list(reversed(recomputation_list[-count:]))


def get_all_recomputations_summary():
    recomputations_summary = list()
    # for each recomputation directory (name)
    for recomputation in next(os.walk(recomputations_dir))[1]:
        recomputations_summary.append(get_recomputation_summary(recomputation))
    recomputations_summary.sort(key=lambda r: r["id"])
    return recomputations_summary


def get_recomputations_count():
    if os.path.exists(recomputations_dir):
        return len(next(os.walk(recomputations_dir))[1])
    else:
        return 0


def exists_vagrantbox(name):
    """
    :param name: Recomputation name
    """

    return get_vagrantfile_relative(name) is not None


def exists_recomputation(name):
    """
    :param name: Recomputation name
    """

    return os.path.exists(get_recomputation_dir(name))


def delete_recomputation(name):
    """
    :param name: Recomputation name
    """

    shutil.rmtree(get_recomputation_dir(name))


def get_all_boxes_data():
    # TODO get rid of hardcoded
    return [{"language": "python", "version": "2.7"}, {"language": "c/c++"}, {"language": "node.js", "version": "0.10"},
            {"language": "gap", "version": "4.7.8"}, {"language": "gecode", "version": "4.4.0"}]
