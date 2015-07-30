import os
import shutil
import json

software_dir_absolute = "recompute/server/recomputations/"
software_dir_relative = "recomputations/"
template_vagrantfiles_dir_absolute = "recompute/server/boxes/"


def get_recomputation_absolute_dir(name):
    return software_dir_absolute + name + "/"


def get_recomputation_relative_dir(name):
    return software_dir_relative + name + "/"


def get_file_relative_path(software_name, filename):
    absolute_path_dir = get_recomputation_absolute_dir(software_name)
    relative_path_dir = get_recomputation_relative_dir(software_name)
    if os.path.exists(absolute_path_dir) and os.path.isfile(absolute_path_dir + filename):
        return relative_path_dir + filename
    else:
        return None


def get_vagrantfile_relative_path(name):
    return get_file_relative_path(name, "Vagrantfile")


def get_vagrantbox_relative_path(name):
    return get_file_relative_path(name, name + ".box")


def exists_vagrantbox(name):
    return get_vagrantbox_relative_path(name) is not None


def exists_recomputation(name):
    recomputation_dir = get_recomputation_absolute_dir(name)
    if os.path.exists(recomputation_dir):
        return True
    else:
        return False


def delete_recomputation(name):
    recomputation_dir = get_recomputation_absolute_dir(name)
    shutil.rmtree(recomputation_dir)


def get_recomputation_data(name):
    recomputation_dir = get_recomputation_absolute_dir(name)
    with open(recomputation_dir + name + ".recompute.json") as recomputation_file:
        return json.load(recomputation_file)


def get_latest_recomputations_data():
    recomputation_list = get_all_recomputations_data()
    return list(reversed(recomputation_list[-5:]))


def get_all_recomputations_data():
    recomputations_data = list()
    recomputations_dir = next(os.walk(software_dir_absolute))
    for recomputation in recomputations_dir[1]:
        recomputations_data.append(get_recomputation_data(recomputation))
    recomputations_data.sort(key=lambda r: r["id"])
    return recomputations_data


def get_recomputations_count():
    return len(next(os.walk(software_dir_absolute))[1])


def get_all_boxes_data():
    return [{"language": "python", "version": "2.7"}, {"language": "c/c++"}, {"language": "node.js", "version": "0.10"},
            {"language": "gap", "version": "4.7.8"}, {"language": "gecode", "version": "4.4.0"}]
