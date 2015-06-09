
import subprocess
import os
from .config import DEFAULT_VM, DEFAULT_VAGRANT_FILE

def __generate_vagrant_file(hostname, github_url, base_vm, base_vagrant_file, save_path):
    """
    Generate a Vagrantfile
    """

    with open("vagrant_files/"+base_vagrant_file, "r") as vagrant_file:
        vagrant_config = vagrant_file.read()

    vagrant_config.replace("<HOSTNAME>", hostname)
    vagrant_config.replace("<BOX>", base_vm)
    vagrant_config.replace("<GITHUB_URL>", github_url)
    vagrant_config.replace("<GITHUB_REPO_NAME>", github_url.split("/")[-1])

    # with open("vagrant_fi")

    return None

def create_vm(hostname, github_url, base_vm=DEFAULT_VM, base_vagrant_file=DEFAULT_VAGRANT_FILE):
    """
    Create a new vagrant box
    """

    print ("Creating a vagrant box %s from GitHub URL %s" % (hostname, github_url))

    print ("Creating project dir %s..." % hostname)
    project_dir = "virtual_machines/"+hostname
    if not os.path.exists(project_dir):
        os.makedirs(project_dir)

    print ("Generating the Vagrantfile...")

    return None

    # vagrant_file = __generate_vagrant_file(hostname, github_url, base_vm, base_vagrant_file)

    # if vagrant_file is not None:
    #     pass
    # else:
    #     return None
    # x = subprocess.Popen(
    #     ["cd", "recompute/server/virtual_machines/", "&&", "pwd", "&&",
    #      "vagrant", "up", "--provision", "&&", "vagrant", "package", "--output", name+".box"],
    #     shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # out, error = x.communicate()
    # print out

def get_all_vms():
    pass
