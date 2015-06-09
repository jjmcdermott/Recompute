
import subprocess
import os
from .config import DEFAULT_VM, DEFAULT_VAGRANT_FILE

def _package_vagrant_box(project_dir, hostname):
    """
    Package a Vagrant box
    """

    vagrant_up = subprocess.Popen(
        ["vagrant", "up", "--provision"],
        cwd=project_dir, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, error = vagrant_up.communicate()
    print out
    print error

    vagrant_package = subprocess.Popen(
        ["vagrant", "package", "--output", hostname+".box"],
        cwd=project_dir, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, error = vagrant_package.communicate()
    print out
    print error

def _generate_vagrant_file(hostname, github_url, base_vm, base_vagrant_file, save_path):
    """
    Generate a Vagrantfile
    """

    with open("recompute/server/vagrant_configs/"+base_vagrant_file, "r") as vagrant_file:
        vagrant_config = vagrant_file.read()

    vagrant_config = vagrant_config.replace("<HOSTNAME>", hostname)
    vagrant_config = vagrant_config.replace("<BOX>", base_vm)
    vagrant_config = vagrant_config.replace("<GITHUB_URL>", github_url)
    vagrant_config = vagrant_config.replace("<GITHUB_REPO_NAME>", github_url.split("/")[-1])

    with open(save_path, "w") as vagrant_file:
        vagrant_file.write("{0}".format(vagrant_config))

def create_vm(hostname, github_url, base_vm=DEFAULT_VM, base_vagrant_file=DEFAULT_VAGRANT_FILE):
    """
    Create a new vagrant box
    """

    project_dir = "recompute/server/vms/" + hostname + "/"
    vagrantfile_path = project_dir + "Vagrantfile"
    vagrantbox_path = project_dir + hostname + ".box"
    relative_vagrantbox_path = "vms/"+hostname+"/"+hostname+".box"

    if os.path.exists(project_dir) and os.path.isfile(vagrantbox_path):
        print "Returning the existing vm...\n{0}\n".format(vagrantbox_path)
        return relative_vagrantbox_path
    elif not os.path.exists(project_dir):
        print "Creating new project directory...\n{0}\n".format(project_dir)
        os.makedirs(project_dir)

    print "Creating new Vagrantfile...\n{0}\n".format(vagrantfile_path)
    _generate_vagrant_file(hostname, github_url, base_vm, base_vagrant_file, vagrantfile_path)

    print "Creating new Vagrant box...\n{0}\n".format(vagrantbox_path)
    _package_vagrant_box(project_dir, hostname)

    return relative_vagrantbox_path

def get_all_vms():
    pass
