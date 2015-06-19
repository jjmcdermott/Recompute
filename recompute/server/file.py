import os


def get_software_absolute_dir():
    return "recompute/server/software/"


def get_software_relative_dir():
    return "software/"


def get_software_absolute_path(name):
    return get_software_absolute_dir() + name + "/"


def get_software_relative_path(name):
    return get_software_relative_dir() + name + "/"


def find_file_relative_path(software_name, filename):
    absolute_path_dir = get_software_absolute_path(software_name)
    relative_path_dir = get_software_relative_path(software_name)
    if os.path.exists(absolute_path_dir) and os.path.isfile(absolute_path_dir + filename):
        return relative_path_dir + filename
    else:
        return None


def find_vagrantfile_relative_path(name):
    return find_file_relative_path(name, "Vagrantfile")


def find_vagrantbox_relative_path(name):
    return find_file_relative_path(name, name + ".box")


def get_recomputation_count():
    software_dir = get_software_absolute_dir()
    count = len(next(os.walk(software_dir))[1])
    return count
