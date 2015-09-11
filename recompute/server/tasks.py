import time
import tornado.gen
import tornado.ioloop
import tornado.process
import tornado.iostream

import sockets
import io
import defaults
import models
import parser


class AsyncRecomputator(object):
    def __init__(self, name, cwd, output_socket=None, output_file=None):
        self.name = name
        self.cwd = cwd
        self.output_socket = output_socket
        self.output_file = output_file

    @tornado.gen.coroutine
    def run(self, command, category=""):
        io.server_log_info("{category} {name} '{command}'".format(category=category, name=self.name, command=command))

        STREAM = tornado.process.Subprocess.STREAM

        p = tornado.process.Subprocess(command.split(), cwd=self.cwd, stdout=STREAM, stderr=STREAM)

        stdout_stream = tornado.iostream.PipeIOStream(p.stdout.fileno())

        def on_stdout_readline(line):
            stdout_readline_callback(line)
            if not stdout_stream.closed():
                stdout_stream.read_until(delimiter="\n", callback=on_stdout_readline)

        def stdout_readline_callback(line):
            io.server_log_info(task="{category} {}".format(category=category, name=self.name), info=line.strip())
            if self.output_file is not None:
                with open(self.output_file, "a") as f:
                    f.write(line)
            if self.output_socket is not None:
                self.output_socket.send_progress(line)

        stdout_stream.read_until(delimiter="\n", callback=on_stdout_readline)

        stderr_stream = tornado.iostream.PipeIOStream(p.stderr.fileno())

        def on_stderr_readline(line):
            stderr_readline_callback(line)
            if not stderr_stream.closed():
                stderr_stream.read_until(delimiter="\n", callback=on_stderr_readline)

        def stderr_readline_callback(line):
            io.server_log_error(task="{category} {}".format(category=category, name=self.name), error=line.strip())
            if self.output_file is not None:
                with open(self.output_file, "a") as f:
                    f.write(line)
            if self.output_socket is not None:
                self.output_socket.send_progress(line)

        stderr_stream.read_until(delimiter="\n", callback=on_stderr_readline)

        exit_code = yield p.wait_for_exit(raise_error=False)

        if exit_code == 0:
            raise tornado.gen.Return(True)
        else:
            raise tornado.gen.Return(False)


@tornado.gen.coroutine
def make_vm(recomputation_obj):
    name = recomputation_obj.name
    tag = recomputation_obj.tag
    version = recomputation_obj.version
    vagrantbox = io.get_vm_name(name)

    cwd = io.get_recomputation_vm_dir(name, tag, version)
    output_socket = sockets.RecomputeSocket.get_socket(name)
    output_file = io.get_log_file(name)

    recomputator = AsyncRecomputator(name=name, cwd=cwd, output_socket=output_socket, output_file=output_file)

    vagrant_up = "vagrant up --provision"
    successful = yield recomputator.run(category="Recomputing", command=vagrant_up)

    vagrant_package = "vagrant package --output {}".format(vagrantbox)
    yield recomputator.run(category="Recomputing", command=vagrant_package)

    raise tornado.gen.Return(successful)


def make_recomputefile(recomputation_obj):
    old_recompute_dict = io.read_recomputefile(recomputation_obj.name)
    recomputefile_path = io.get_recomputefile(recomputation_obj.name)

    if old_recompute_dict is None:
        recomputation_obj.id = io.get_next_recomputation_id()

    with open(recomputefile_path, "w") as f:
        f.write("{}".format(recomputation_obj.to_pretty_json(old_recompute_dict)))


def make_vagrantfile(recomputation_obj):
    vagrantfile_template = io.get_vagrantfile_template(recomputation_obj.github_obj.programming_language)
    with open(vagrantfile_template, "r") as f:
        vagrantfile = f.read()

    vagrantfile = vagrantfile.replace("<NAME>", recomputation_obj.name)
    vagrantfile = vagrantfile.replace("<BOX>", recomputation_obj.box)

    github_obj = recomputation_obj.github_obj

    language_version = github_obj.programming_language_version
    if language_version is None:
        language_version = ""
    vagrantfile = vagrantfile.replace("<LANGUAGE_VERSION>", language_version)

    vagrantfile = vagrantfile.replace("<GITHUB_URL>", github_obj.github_url)
    vagrantfile = vagrantfile.replace("<GITHUB_REPO_NAME>", github_obj.repo_name)

    travis_obj = github_obj.travis_obj

    add_apt_repositories = "\n".join(["add-apt-repository -y " + r for r in travis_obj.add_apt_repositories_list])
    vagrantfile = vagrantfile.replace("<ADD_APT_REPOSITORIES>", add_apt_repositories)

    apt_get_installs = " ".join(travis_obj.apt_get_installs_list)
    vagrantfile = vagrantfile.replace("<APT_GET_INSTALLS>", apt_get_installs)

    install_scripts_list = travis_obj.install_scripts_list
    if len(install_scripts_list) == 0:
        install_scripts_list.extend(defaults.languages_install_dict[github_obj.programming_language])
    if github_obj.repo_name in defaults.boxes_install_scripts:
        install_scripts_list.extend(defaults.boxes_install_scripts[github_obj.repo_name])
    install_scripts = "\n  ".join(install_scripts_list) + "\n"
    vagrantfile = vagrantfile.replace("<INSTALL_SCRIPTS>", install_scripts)

    if github_obj.repo_name in defaults.ignore_test_scripts:
        test_scripts = ""
    else:
        test_scripts = "\n  ".join(travis_obj.test_scripts_list) + "\n"
    vagrantfile = vagrantfile.replace("<TEST_SCRIPTS>", test_scripts)

    vagrantfile = vagrantfile.replace("<MEMORY>", str(recomputation_obj.memory))
    vagrantfile = vagrantfile.replace("<CPUS>", str(recomputation_obj.cpus))

    vagrantfile_path = io.get_vagrantfile(recomputation_obj.name, recomputation_obj.tag, recomputation_obj.version)
    with open(vagrantfile_path, "w") as f:
        f.write("{}".format(vagrantfile))


def make_recomputation_object(name, github_url, box):
    """
    """

    box_url = io.get_base_vm_url(box)
    box_version = io.get_base_vm_version(box)

    github_obj = parser.GitHubParser.parse(github_url)

    language = github_obj.programming_language
    if language is None:
        raise ParseLanguageException()

    if language == "haskell":
        memory = defaults.haskell_vm_memory
    else:
        memory = defaults.recomputation_vm_memory
    cpus = defaults.recomputation_vm_cpus

    tag = "Latest"
    version = io.get_next_build_version(name)
    date = time.strftime("%Y-%m-%d %H:%M:%S")

    return models.RecomputationObject(name, github_obj, box, box_url, box_version, memory, cpus, tag, version, date)


@tornado.gen.coroutine
def recompute(name, github_url, box):
    """
    Recompute a project on GitHub. Returns a tuple (status_code, err).

    status_code: True if successful, False otherwise
    err: Error message
    """

    io.create_recomputation_dir(name)

    try:
        recomputation_obj = make_recomputation_object(name, github_url, box)
    except ParseLanguageException:
        raise tornado.gen.Return((False, "Programming language not found"))

    programming_language = recomputation_obj.github_obj.programming_language
    if programming_language not in defaults.vagrantfile_templates_dict:
        raise tornado.gen.Return((False, "{} is not recognized".format(programming_language)))

    io.create_recomputation_vm_dir(name, recomputation_obj.tag, recomputation_obj.version)

    make_vagrantfile(recomputation_obj)

    successful = yield make_vm(recomputation_obj)

    if successful:
        make_recomputefile(recomputation_obj)
        raise tornado.gen.Return((True, ""))
    else:
        raise tornado.gen.Return((False, "Failed"))


class ParseLanguageException(Exception):
    pass
