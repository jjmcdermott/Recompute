# Recompute

[![Build Status](https://travis-ci.org/cjw-charleswu/Recompute.svg?branch=master)](https://travis-ci.org/cjw-charleswu/Recompute)

A web application for recomputating your projects and experiments. It's a summer project for [recomputation.org](http://www.recomputation.org/).
The idea is that "If we can compute your experiment now, anyone can recompute it 20 years from now." We want to keep
multiple revisions of the same software and allow other people to run, maintain and test the software.

The system will build your software and run your test scripts inside a virtual machine created using Vagrant. There is
a front-end where you can browse all of your recomputation and a in-browser terminal which provides access to the virtual machine.


## Running the server locally

- `$ python run.py --port=[port]`

![recompute](https://raw.github.com/cjw-charleswu/Recompute/master/screenshots/recompute.png)


## Dependencies

The server is written in Python 2.7x, using Tornado and Flask.We recommend running the server inside a virtual environment
with [virtualenv](http://docs.python-guide.org/en/latest/dev/virtualenvs/). The complete Python requirements can be found in `requirements.txt`.
It also requires [VirtualBox](https://www.virtualbox.org/) and [Vagrant](https://www.vagrantup.com/). The server was developed
on Fedora 21 with Virtual Box 4.3 and Vagrant 1.7.2. 

### virtualenv

You can install virtualenv with pip:

- `$ pip install virtualenv`

To create a new virtual environment:

- `$ virtualenv venv`

And to use it:

- `$ source venv/bin/activate`

On Windows, do:

- `$ .\venv\Scripts\activate`

To install all the dependencies:

- `(venv) $ pip install -r requirements.txt`

To exit the virtual environment:

- `(venv) $ deactivate`


## Recomputation example: gecode

[Gecode](https://github.com/ampl/gecode) is a constraint programming solver. 

To recompute this project:

1. Start server

2. Open a web browser and visit: `localhost:[port]`

3. In the recompute form, enter name `gecode` and url `https://github.com/ampl/gecode`

4. If you have installed all the dependencies, you should see that the server is creating your vm on the terminal. Your
browser will start downloading the virtual machine once it's done.

To start the virtual machine:

1. `$ cd /path/to/gecode.box`
 
2. `$ vagrant init gecode.box`

3. `$ vagrant up`

4. `$ vagrant ssh`


## How it works

Recompute takes a GitHub URL and repackages your project into a virtual machine along with all of its dependencies.
It follows the build instructions from a [Travis](https://travis-ci.org/) script in the project directory. If there isn't a Travis script,
it will still try to build the project with respect to the primary programming language. For example, it will try
`./congigure && make && sudo make install' to build a C++ project.


## Tests


## Limitations

The applications only supports projects written in C, C++, Python, and Node.js.

## Future work

- Scalability
- AI
- Reproducible experiments
- Distributed systems, parallel programs
- Mobile operating systems, sensors
