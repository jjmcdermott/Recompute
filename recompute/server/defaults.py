vm_memory = 4098
vm_cpus = 2

vagrantfile_templates_dict = {
    "python": "python/python.vagrantfile",
    "node_js": "nodejs/nodejs.vagrantfile",
    "cpp": "cpp/cpp.vagrantfile",
    "c++": "cpp/cpp.vagrantfile",
    "c": "cpp/cpp.vagrantfile"
}

languages_version_dict = {
    "python": "2.7",
    "node_js": "0.10",
    "cpp": "",
    "c++": "",
    "c": ""
}

languages_install_dict = {
    "python": ["pip install -r requirements.txt"],
    "node_js": ["npm install"],
    "cpp": ["chmod +x configure", "./configure", "make", "sudo make install"],
    "c++": ["chmod +x configure", "./configure", "make", "sudo make install"],
    "c": ["chmod +x configure", "./configure", "make", "sudo make install"]
}

boxes_install_scripts = {
    "gecode": ["echo 'export LD_LIBRARY_PATH=/home/vagrant/gecode' >> ~/.bashrc", "source ~/.bashrc"]
}
