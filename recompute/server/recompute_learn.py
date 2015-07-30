default_memory = 4098
default_cpus = 2

vagrantfile_templates_dict = {
    "python": "python/python.vagrantfile",
    "node_js": "nodejs/nodejs.vagrantfile",
    "cpp": "cpp/cpp.vagrantfile",
    "c++": "cpp/cpp.vagrantfile",
    "c": "cpp/cpp.vagrantfile"
}

default_languages_version_dict = {
    "python": "2.7",
    "node_js": "0.10",
    "cpp": "",
    "c++": "",
    "c": ""
}

default_languages_installs_dict = {
    "python": ["pip install -r requirements.txt"],
    "node_js": ["npm install"],
    "cpp": ["chmod +x configure", "./configure", "make", "sudo make install"],
    "c++": ["chmod +x configure", "./configure", "make", "sudo make install"],
    "c": ["chmod +x configure", "./configure", "make", "sudo make install"]
}
