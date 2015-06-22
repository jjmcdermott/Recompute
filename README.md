# Recompute

[![Build Status](https://travis-ci.org/cjw-charleswu/Recompute.svg?branch=master)](https://travis-ci.org/cjw-charleswu/Recompute)

A web application for recomputating your projects and experiments. See [recomputation.org](http://www.recomputation.org/) for more information.

## What is recomputation?

Recomputation is the idea that "If we can compute your experiment now, anyone can recompute it 20 years from now".
Recompute means to build and run a piece of software. We want to keep your software in a state that it
can be discovered, ran, maintained, and tested by other people effortlessly.

## Running the server

- `$ python run.py --port=[port]`

![recompute](https://raw.github.com/cjw-charleswu/Recompute/master/images/recompute.png)

## Dependencies

The server is written in Python, using Tornado and Flask. You will need Python2.7x. We recommend running the server
inside a virtual environment. Read [virtualenv](http://docs.python-guide.org/en/latest/dev/virtualenvs/) for more information.
To run recomputation, you will need [VirtualBox](https://www.virtualbox.org/) and [Vagrant](https://www.vagrantup.com/).
Vagrant is a nice tool, you will like it.

You can install Python's virtual environment virtualenv with pip:

- `$ pip install virtualenv`

To create and use a virtual environment:

- `$ virtualenv venv`
- `$ source venv/bin/activate`

Inside the virtual environment, install all the dependencies:

- `$(venv) pip install -r requirements.txt`

To exit the virtual environment:

- `$(venv) deactivate`

Starting the virtual environment on Windows is slightly different:

- `$ .\venv\Scripts\activate`

## How it works

It takes a GitHub URL and repackages your project into a virtual machine with all of its dependencies.
It looks for a [Travis](https://travis-ci.org/) script inside the Github repository. If there is a Travis script,
reproduce the steps to its best ability. If there is no Travis script, guess the instructions on how to rebuild the project.
For example, try `./congigure && make && sudo make install' to build a C++ project. If everything fails, come back again
in a few weeks, and try again.

## Tests

Currently there are no tests to show that it actually works, but it does (to some extent).

## Limitations

The applications only supports projects written in C, C++, Python, and Node.js.

## Future work

- UI
- "Play" button
- Multiple languages
- Scalability
- AI
- Reproducible experiments
- Distributed systems, parallel programs
- Virtual mobile operating systems, sensors
