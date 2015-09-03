# Recompute
[![Build Status][1]][2]

A web application for recomputating your projects and experiments. It is a summer project for [recomputation.org][3].
The idea is that "If we can compute your experiment now, anyone can recompute it 20 years from now." We want to keep
multiple revisions of the software and allow other people to run, maintain and test them. Recompute builds your GitHub
project by following the build instructions from the [Travis](https://travis-ci.org/) script in the project directory.

The application provides a user interface to submit the GitHub url for recomputation. It also allows you to browse
through recomputed projects and access the virtual machines through an in-browser terminal.


## Report
The complete report is available [here][4].


## Prerequisites
- Python 2.7x (recommend [virtualenv][5])
- [VirtualBox][6]
- [Vagrant][7]


## Install
Install virtualenv.

    $ sudo pip install virtualenv

Git clone the repository and create a virtual environment named venv

    $ git clone git@github.com:cjw-charleswu/Recompute.git
    $ cd Recompute/
    $ virtualenv venv

Activate the virtual environment and install the dependencies.

In Bash:

    $ source venv/bin/activate
    (venv) $ pip install -r requirements.txt

In Windows Command Prompt (or Powershell):

    $ .\venv\Scripts\activate
    (venv) $ pip install -r requirements.txt

Exit the virtual environment:

    (venv) $ deactivate


## Run
The server is a Python Tornado + Flask application.

#### Server
The IP address and port number are optional. By default, the server will run at localhost:5000.

    $ cd Recompute/
    $ source venv/bin/activate
    # run at the default IP address and port
    (venv) $ python run.py
    # run at a specific IP address and port
    (venv) $ python run.py --host=[host] --port=[port]


Visit the front page of the web application at [host]:[port]

![recompute][8]


## Recomputation example: gecode
[gecode](https://github.com/ampl/gecode) is a constraint programming solver.

1. Follow the steps to run the server and visit the front page

3. Enter the name `gecode` and url `https://github.com/ampl/gecode` and choose a base virtual machine.

4. The browser will start recomputation download the virtual machine once it is finished.

To start the virtual machine:

    $ cd /path/to/gecode.box
    $ vagrant init gecode.box
    $ vagrant up
    $ vagrant ssh


[1]: https://travis-ci.org/cjw-charleswu/Recompute.svg?branch=master
[2]: https://travis-ci.org/cjw-charleswu/Recompute
[3]: http://www.recomputation.org/
[4]: https://github.com/cjw-charleswu/Recompute/blob/master/report/report.pdf
[5]: http://docs.python-guide.org/en/latest/dev/virtualenvs/
[6]: https://www.virtualbox.org/
[7]: https://www.vagrantup.com/
[8]: https://raw.github.com/cjw-charleswu/Recompute/master/screenshots/recompute.png