# Recompute

[![Build Status](https://travis-ci.org/cjw-charleswu/Recompute.svg?branch=master)](https://travis-ci.org/cjw-charleswu/Recompute)

A web application for recomputating your projects and experiments. It iss a summer project for [recomputation.org](http://www.recomputation.org/).
The idea is that "If we can compute your experiment now, anyone can recompute it 20 years from now." We want to keep
multiple revisions of the software and allow other people to run, maintain and test them.

The front-end provides a user interface to recompute your project. It allows you to browse through recomputed projects
and access the virtual machines through a web-based terminal.

## Report

The complete report is available at ![here](https://raw.github.com/cjw-charleswu/Recompute/master/report/report.pdf)


## Dependencies

The server is written in Python 2.7x, using Tornado and Flask. We recommend running the server inside a virtual environment
with [virtualenv](http://docs.python-guide.org/en/latest/dev/virtualenvs/). The complete Python requirements can be found in `requirements.txt`.
The system also requires [VirtualBox](https://www.virtualbox.org/) and [Vagrant](https://www.vagrantup.com/).

### virtualenv

Create a new virtual environment:

- `$ sudo pip install virtualenv`
- `$ virtualenv venv`

Install all the dependencies inside the virtual environment:

In Bash:

- `$ source venv/bin/activate`
- `(venv) $ pip install -r requirements.txt`

In Windows Command Prompt (or Powershell):

- `$ .\venv\Scripts\activate`

Exit the virtual environment:

- `(venv) $ deactivate`


## Running the server

The server will run at port 5000 if it is not specified.

- `(venv) $ python run.py --port=[port]`

![recompute](https://raw.github.com/cjw-charleswu/Recompute/master/screenshots/recompute.png)


## Recomputation example: gecode

To recompute [gecode](https://github.com/ampl/gecode), constraint programming solver, do the following steps:

1. Start the server: `$ python run.py --port=[port]`

2. Visit: `localhost:[port]` on a web browser.

3. Enter the name `gecode` and url `https://github.com/ampl/gecode` and choose a base virtual machine.

4. The browser will download the virtual machine once recomputation is finished.

To start the virtual machine:

- `$ cd /path/to/gecode.box`
- `$ vagrant init gecode.box`
- `$ vagrant up`
- `$ vagrant ssh`


## How does it work?

Recompute takes a GitHub URL and packages your project into a virtual machine along with all of its dependencies.
It follows the build instructions from a [Travis](https://travis-ci.org/) script in the project directory. If the project
does not contain a Travis script, it will still try to build the project but may be unsuccessful.
