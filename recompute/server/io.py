import subprocess
import os
import shutil
import json
import re
import time

import config
import boxes
import defaults

recomputations_dir = "recompute/server/recomputations"
logs_dir = "recompute/server/logs"
base_boxes_dir = "recompute/server/boxes"


def execute(command, cwd=None, readline_callback=None):
    p = subprocess.Popen(command.split(), cwd=cwd, stdout=subprocess.PIPE)
    while True:
        line = p.stdout.readline()
        if line == '' and p.poll() is not None:
            break
        if line != '':
            readline_callback(line)


def server_log_info(task, info=""):
    time_string = time.strftime("%Y-%m-%d %H:%M:%S")
    print "\033[94m$ Recompute {time} [{task}] \033[0m{info}".format(time=time_string, task=task, info=info)


def server_log_error(task, error=""):
    time_string = time.strftime("%Y-%m-%d %H:%M:%S")
    print "\033[95m$ Recompute {time} [{task}] \033[0m{error}".format(time=time_string, task=task, error=error)


def create_recomputations_dir():
    """
    Initialization: Creates recomputations directory
    """

    server_log_info("Creating recomputations directory @ {}".format(recomputations_dir))
    if not os.path.exists(recomputations_dir):
        os.makedirs(recomputations_dir)


def create_logs_dir():
    """
    Initialization: Creates logs directory
    """

    server_log_info("Creating logs directory @ {}".format(logs_dir))
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)


def update_base_vms():
    """
    Initialization: Return a dictionary of base vms where the key is the name and value is the version
    """

    base_vms_dict = dict()

    vagrant_box_list = "vagrant box list"

    def vagrant_box_list_readline_callback(line):
        """
        'vagrant box list' returns something like
        # ubuntu/trusty64                                                 (virtualbox, 20150609.0.9)
        # ubuntu/trusty64                                                 (virtualbox, 20150814.0.1)
        # ubuntu/trusty64                                                 (virtualbox, 20150817.0.0)

        Converts each line to a list of strings like
        # [['ubuntu/trusty64', 'virtualbox', '20150609.0.9'],
        #  ['ubuntu/trusty64', 'virtualbox', '20150814.0.1'],
        #  ['ubuntu/trusty64', 'virtualbox', '20150817.0.0']]
        """
        server_log_info("Listing vm", info=" ".join(line.rstrip().split()))
        descriptions = re.sub("[(),]", "", line).split()
        name = descriptions[0]
        version = descriptions[2]

        if name not in base_vms_dict or version > base_vms_dict[name]:
            base_vms_dict[name] = version

    server_log_info("Listing vms '{}'".format(vagrant_box_list))
    execute(vagrant_box_list, readline_callback=vagrant_box_list_readline_callback)

    base_vms_updated = dict()

    vagrant_box_update = "vagrant box update --box {box}"

    def vagrant_box_update_readline_callback(line):
        """
        'vagrant box update --box BOX' returns something like
        # ... Successfully added box 'ubuntu/trusty64' (v20150818.0.0) for 'virtualbox'!
        # or
        # ... Box 'ubuntu/trusty64' (v20150818.0.0) is running the latest version.
        """
        server_log_info("Updating base vm", info=line.rstrip())
        if "Successfully added box" in line:
            name = line[line.find("box '") + 5:line.find("' (")]
            version = line[line.find("' (v") + 4:line.find(") for ")]
            base_vms_updated[name] = version

    publicly_available_vms = [box[0] for box in boxes.BASE_BOXES]
    for vm in base_vms_dict.iterkeys():
        if vm in publicly_available_vms and vm not in base_vms_updated:
            command = vagrant_box_update.format(box=vm)
            server_log_info("Updating base vm '{}'".format(command))
            execute(command, readline_callback=vagrant_box_update_readline_callback)

    for vm, version in base_vms_updated.iteritems():
        base_vms_dict[vm] = version

    vagrant_box_add = "vagrant box add {box} --provider virtualbox"

    def vagrant_box_add_readline_callback(line):
        server_log_info("Adding base vm", info=" ".join(line.rstrip().split()))
        if "Adding box" in line:
            name = line[line.find("Adding box '") + 12:line.find("' (")]
            version = line[line.find("' (v") + 4:line.find(") for ")]
            base_vms_dict[name] = version

    for box in boxes.BASE_BOXES:
        name = box[0]
        if name not in base_vms_dict:
            command = vagrant_box_add.format(box=name)
            print command
            server_log_info("Adding base vm '{}'".format(command))
            execute(command, readline_callback=vagrant_box_add_readline_callback)

    return base_vms_dict


def remove_failed_recomputations():
    """
    Initialization: Removes failed recomputations
    """

    server_log_info("Removing failed recomputations")
    for recomputation in next(os.walk(recomputations_dir))[1]:
        recompute_dict = load_recomputation(recomputation)
        if recompute_dict is None:
            server_log_info("Removed '{}'".format(recomputation))
            shutil.rmtree("{dir}/{name}".format(dir=recomputations_dir, name=recomputation))


def remove_old_logs():
    """
    Initialization: Removes old logs
    """

    server_log_info("Removing old logs")
    for recomputation in next(os.walk(logs_dir))[1]:
        server_log_info("Removed '{}'".format(recomputation))
        shutil.rmtree("{dir}/{name}".format(dir=logs_dir, name=recomputation))


def get_recomputation_dir(name):
    """
    Returns the recomputation directory path
    """

    return "{dir}/{name}".format(dir=recomputations_dir, name=name)


def get_log_dir(name):
    """
    Returns the recomputation log directory path
    """

    return "{dir}/{name}".format(dir=logs_dir, name=name)


def get_recomputation_vm_dir(name, tag, version):
    """
    Returns the recomputation vm directory path
    """

    return "{dir}/vms/{tag}_{version}".format(dir=get_recomputation_dir(name), tag=tag, version=version)


def create_recomputation_dir(name):
    """
    Creates the recomputation & log directories
    """

    recomputation_dir = get_recomputation_dir(name)
    if not os.path.exists(recomputation_dir):
        os.makedirs(recomputation_dir)

    log_dir = get_log_dir(name)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)


def create_recomputation_vm_dir(name, tag, version):
    """
    Creates the recomputation vm directory
    """

    recomputation_build_dir = get_recomputation_vm_dir(name, tag, version)
    if not os.path.exists(recomputation_build_dir):
        os.makedirs(recomputation_build_dir)


def get_log_file(name):
    """
    Returns a new recomputation log file name, with a timestamp
    """
    return "{dir}/{name}/{time}.txt".format(dir=logs_dir, name=name, time=time.strftime("%Y%m%d-%H%M%S"))


def get_vagrantfile(name, tag, version):
    """
    Returns the recomputation vm Vagrantfile path
    """
    return "{dir}/Vagrantfile".format(dir=get_recomputation_vm_dir(name, tag, version))


def get_recomputefile(name):
    """
    Returns the recomputation recomputefile path
    """
    return "{dir}/{name}.recompute.json".format(dir=get_recomputation_dir(name), name=name)


def get_vagrantfile_template(language):
    if language in defaults.vagrantfile_templates_dict:
        return "{dir}/{template}".format(dir=base_boxes_dir, template=defaults.vagrantfile_templates_dict[language])
    else:
        return None


def get_next_vm_version(name):
    recompute_dict = load_recomputation(name)
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


def load_recomputation(name):
    """
    Returns a dictionary representation of the recomputation
    """

    recompute_file = get_file_if_exists(name, "{name}.recompute.json".format(name=name))

    if recompute_file is None:
        return None
    else:
        with open(recompute_file) as recomputation_file:
            return json.load(recomputation_file)


def load_recomputation_by_id(id):
    for recomputation in next(os.walk(recomputations_dir))[1]:
        recompute_dict = load_recomputation(recomputation)
        if recompute_dict is not None:
            if recompute_dict["id"] == id:
                return recompute_dict
    return None


def load_all_recomputations(count=0):
    """
    Returns a list of dictionaries, each representing a recomputation, ordered by decreasing ids
    """

    recomputations_summary = list()
    for recomputation in next(os.walk(recomputations_dir))[1]:
        recompute_dict = load_recomputation(recomputation)
        if recompute_dict is not None:
            recomputations_summary.append(recompute_dict)
    recomputations_summary.sort(key=lambda r: r["id"])

    ordered_by_ids = list(reversed(recomputations_summary))

    if count != 0:
        return ordered_by_ids[:count]
    else:
        return ordered_by_ids


def get_next_recomputation_id():
    recomputation_summary = load_all_recomputations()
    if len(recomputation_summary) == 0:
        return 0
    else:
        return recomputation_summary[0]["id"] + 1


def get_recomputations_count():
    if os.path.exists(recomputations_dir):
        count = 0
        for recomputation in next(os.walk(recomputations_dir))[1]:
            recompute_dict = load_recomputation(recomputation)
            if recompute_dict is not None:
                count += 1
        return count
    else:
        return 0


def exists_recomputation(name):
    return os.path.exists(get_recomputation_dir(name)) and os.path.exists(get_recomputefile(name))


def exists_vm(name, tag, version):
    return os.path.exists(get_recomputation_vm_dir(name, tag, version))


def change_recomputation_name(name, new_name):
    recompute_dict = load_recomputation(name)
    recompute_dict["name"] = new_name
    override_recomputefile(name, recompute_dict)

    new_recomputation_dir = get_recomputation_dir(new_name)
    shutil.move(get_recomputation_dir(name), new_recomputation_dir)

    old_recomputefile = "{}.recompute.json".format(name)
    new_recomputefile = "{}.recompute.json".format(new_name)
    shutil.move(os.path.join(new_recomputation_dir, old_recomputefile),
                os.path.join(new_recomputation_dir, new_recomputefile))

    for vm in next(os.walk(os.path.join(new_recomputation_dir, "vms")))[1]:
        old_box_path = "{dir}/{name}.box".format(dir=os.path.join(new_recomputation_dir, "vms", vm), name=name)
        new_box_path = "{dir}/{name}.box".format(dir=os.path.join(new_recomputation_dir, "vms", vm), name=new_name)
        shutil.move(old_box_path, new_box_path)


def change_recomputation_github_url(name, new_github_url):
    recompute_dict = load_recomputation(name)
    recompute_dict["github_url"] = new_github_url
    override_recomputefile(name, recompute_dict)


def change_recomputation_description(name, new_description):
    recompute_dict = load_recomputation(name)
    recompute_dict["description"] = new_description
    override_recomputefile(name, recompute_dict)


def destroy_recomputation(name):
    recomputation_dir = get_recomputation_dir(name)

    command = "vagrant destroy --force"

    task = None

    def vagrant_destroy_readline_callback(line):
        server_log_info(task=task, info=line.strip())

    for vm in next(os.walk(os.path.join(recomputation_dir, "vms")))[1]:
        cwd = os.path.join(recomputation_dir, "vms", vm)
        task = "Destroying recomputation {name} {vm}".format(name=name, vm=vm)
        server_log_info("{task} '{command}'".format(task=task, command=command))
        execute(command, cwd=cwd, readline_callback=vagrant_destroy_readline_callback)

    shutil.rmtree(recomputation_dir, ignore_errors=True)


def override_recomputefile(name, recompute_dict):
    recomputefile_path = get_recomputefile(name)
    with open(recomputefile_path, "w") as recomputef:
        recomputef.write(json.dumps(recompute_dict, indent=4, sort_keys=True))


def destroy_vm(name, tag, version):
    # update recomputefile
    recompute_dict = load_recomputation(name)
    recompute_dict["vms"] = [vm for vm in recompute_dict["vms"] if vm["tag"] != tag or vm["version"] != version]

    override_recomputefile(name, recompute_dict)
    shutil.rmtree(get_recomputation_vm_dir(name, tag, version), ignore_errors=True)
