"""
Accessing recomputation files, Vagrantboxes and Vagrantfiles
"""

import os
import shutil
import json

recomputations_dir = "recompute/server/recomputations"
recomputations_dir_relative = "recomputations"
base_boxes_dir = "recompute/server/boxes"


def create_recomputations_dir():
    if not os.path.exists(recomputations_dir):
        os.makedirs(recomputations_dir)


def create_recomputation_dir(name):
    recomputation_dir = get_recomputation_dir(name)
    if not os.path.exists(recomputation_dir):
        os.makedirs(recomputation_dir)


def create_recomputation_vms_dir(name):
    """
    :param name: Recomputation name
    """

    vms_dir = get_recomputation_vms_dir(name)
    if not os.path.exists(vms_dir):
        os.makedirs(vms_dir)


def create_recomputation_build_dir(name, tag, version):
    """
    :param tag:
    :param version:
    """

    build_dir = get_recomputation_build_dir(name, tag, version)
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

    return "{recomputations_dir}/{name}/vms".format(recomputations_dir=recomputations_dir, name=name)


def get_recomputation_build_dir(name, tag, version):
    """
    Return the absolute path of a recomputation vm directory (inside the project directory i.e. Recompute).

    :param name: Recomputation name
    """

    return "{recomputations_dir}/{name}/vms/{tag}_{version}".format(recomputations_dir=recomputations_dir, name=name,
                                                                    tag=tag, version=version)


def get_vagrantfile_path(name):
    return "{recomputation_dir}/Vagrantfile".format(recomputation_dir=get_recomputation_dir(name))


def get_recomputefile_path(name):
    return "{recomputation_dir}/{name}.recompute.json".format(recomputation_dir=get_recomputation_dir(name), name=name)


def get_vagrantfile_template_path(template):
    return "{base_boxes_dir}/{template}".format(base_boxes_dir=base_boxes_dir, template=template)


def get_file_if_exists(recomputation_name, filename, absolute_path=True):
    recomputation_dir = get_recomputation_dir(recomputation_name)
    recomputation_dir_relative = get_recomputation_dir_relative(recomputation_name)

    if os.path.exists(recomputation_dir) and os.path.isfile(recomputation_dir + "/" + filename):
        if absolute_path:
            return "{recomputation_dir}/{filename}".format(recomputation_dir=recomputation_dir, filename=filename)
        else:
            return "{recomputation_dir}/{filename}".format(recomputation_dir=recomputation_dir_relative,
                                                           filename=filename)
    else:
        return None


def get_vagrantfile_relative(name):
    """
    Used to download Vagrantfile

    :param name: Recomputation name
    """

    return get_file_if_exists(name, "Vagrantfile", False)


def get_vagrantbox_relative(name):
    """
    Used to download Vagrantbox

    :param name: Recomputation name
    """

    return get_file_if_exists(name, name + ".box", False)


def get_recomputation_summary_file(name):
    """
    :param name: Recomputation name
    """

    return get_file_if_exists(name, name + ".recompute.json", True)


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


def remove_vagrantbox_cache(name):
    """
    TODO: fix
    """

    cache_dir = "{recomputation_dir}/.vagrant".format(recomputation_dir=get_recomputation_dir(name))
    shutil.rmtree(cache_dir, ignore_errors=True)


def exists_recomputation(name):
    """
    :param name: Recomputation name
    """

    return os.path.exists(get_recomputation_dir(name))


def destroy_recomputation(name):
    """
    Remove recomputation

    :param name: Recomputation name
    """

    shutil.rmtree(get_recomputation_dir(name), ignore_errors=True)


def get_all_boxes_data():
    # TODO get rid of hardcoded
    return [{"language": "python", "version": "2.7"}, {"language": "c/c++"}, {"language": "node.js", "version": "0.10"},
            {"language": "gap", "version": "4.7.8"}, {"language": "gecode", "version": "4.4.0"}]
