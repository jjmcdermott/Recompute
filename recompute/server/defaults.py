recomputation_vm_memory = 2048
haskell_vm_memory = 4096
recomputation_vm_cpus = 2

vagrantfile_templates_dict = {
    "python": "python/python.vagrantfile",
    "node_js": "nodejs/nodejs.vagrantfile",
    "cpp": "cpp/cpp.vagrantfile",
    "c++": "cpp/cpp.vagrantfile",
    "c": "cpp/cpp.vagrantfile",
    "haskell": "haskell/haskell.vagrantfile",
    "go": "go/go.vagrantfile"
}

languages_version_dict = {
    "python": "2.7",
    "node_js": "0.10"
}

languages_install_dict = {
    "python": ["pip install -r requirements.txt"],
    "node_js": ["npm install"],
    "cpp": ["chmod +x configure", "./configure", "make", "sudo make install"],
    "c++": ["chmod +x configure", "./configure", "make", "sudo make install"],
    "c": ["chmod +x configure", "./configure", "make", "sudo make install"],
    "haskell": ["$VAGRANT_USER 'cabal configure'", "$VAGRANT_USER 'cabal install'"]
}

boxes_install_scripts = {
    "gecode": ["echo \"export LD_LIBRARY_PATH=/home/vagrant/gecode\" >> /home/vagrant/.bashrc", "source /home/vagrant/.bashrc"],
    "Idris-dev": ["$VAGRANT_USER 'sudo cabal configure'", "$VAGRANT_USER 'sudo cabal install'"]
}

ignore_test_scripts = ["Idris-dev"]
