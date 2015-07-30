default_memory = 4098
default_cpus = 2

vagrantfile_templates_dict = {
    "python": "python/python.vagrantfile.template",
    "node_js": "nodejs/nodejs.vagrantfile.template",
    "cpp": "cpp/cpp.vagrantfile.template",
    "c++": "cpp/cpp.vagrantfile.template",
    "c": "cpp/cpp.vagrantfile.template"
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
