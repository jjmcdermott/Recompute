# Recompute

[![Build Status](https://travis-ci.org/cjw-charleswu/Recompute.svg?branch=master)](https://travis-ci.org/cjw-charleswu/Recompute)

A web application for recomputating your projects and experiments. It's a summer project for [recomputation.org](http://www.recomputation.org/).
The idea is that "If we can compute your experiment now, anyone can recompute it 20 years from now." We want to keep
multiple revisions of the same software, making it discoverable for other people and allowing them to maintain and test
the software.

The application uses Vagrant to create a virtual machine. Inside the virtual machine, it will try to
build your software and run any test scripts that you have. If successful, you will receive the virtual machine.

You can browse all of your recomputations through the front-end. You can also start a web-based terminal which allows
you to access the virtual machine from the browser.


## Running the server

- `$ python run.py --port=[port]`

![recompute](https://raw.github.com/cjw-charleswu/Recompute/master/screenshots/recompute.png)


## Dependencies

The server is written in Python, using Tornado and Flask. You will need Python2.7x. We recommend running the server
inside a virtual environment with [virtualenv](http://docs.python-guide.org/en/latest/dev/virtualenvs/). The complete
Python requirements can be found in `requirements.txt`.

It also requires [VirtualBox](https://www.virtualbox.org/) and [Vagrant](https://www.vagrantup.com/). The server was
developed on Fedora 21 with Virtual Box 4.3 and Vagrant 1.7.2. 

You can install Python's virtual environment virtualenv with pip:

- `$ pip install virtualenv`

To create and use a virtual environment:

- `$ virtualenv venv`
- `$ source venv/bin/activate`

Starting the virtual environment on Windows is slightly different:

- `$ .\venv\Scripts\activate`

Inside the virtual environment, install all the dependencies:

- `(venv) $ pip install -r requirements.txt`

To exit the virtual environment:

- `(venv) $ deactivate`


### Recomputation example: gecode

Gecode is a constraint programming solver. To recompute the latest version of gecode from [Github](https://github.com/ampl/gecode),
start the server. Open a web browser and type: `localhost:[port]`. You will see a front page similar to the screenshot shown above.
Enter a name, say `gecode`, and the url `https://github.com/ampl/gecode`.

If you have all the dependencies installed, you should see that the server is creating your vm from the terminal where the server
was started. The process should finish within 10 minutes or longer depending on your host machine.
Your browser will start downloading the virtual machine containing gecode once it's ready.

To start the virtual machine, use Vagrant in the directory containing the virtual machine:

- `$ vagrant init`
- `$ vagrant up`
- `$ vagrant ssh`


## How it works

Recompute takes a GitHub URL and repackages your project into a virtual machine along with all of its dependencies.
It looks for a [Travis](https://travis-ci.org/) script inside the Github repository. If there is a Travis script, it will
attempt to reproduce the same steps for building the application. If there is no Travis script, it will still try to
build the project with respect to the primary programming language.
For example, it will try `./congigure && make && sudo make install' to build a C++ project.


## Tests




## Limitations

The applications only supports projects written in C, C++, Python, and Node.js.

## Future work

- UI
- Scalability
- AI
- Reproducible experiments
- Distributed systems, parallel programs
- Mobile operating systems, sensors
