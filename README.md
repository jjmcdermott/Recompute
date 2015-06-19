# Recompute

[![Build Status](https://travis-ci.org/cjw-charleswu/Recompute.svg?branch=master)](https://travis-ci.org/cjw-charleswu/Recompute)

A web application for recomputating your projects and experiments. See [recomputation.org](http://www.recomputation.org/) for more details.

## Running the server

- `$ python run.py --port=[port]`

![recompute](https://raw.github.com/cjw-charleswu/Recompute/master/images/recompute.png)

## Dependencies

The server is written in Python, using Tornado and Flask. See requirements.txt.

## How it works

It takes a GitHub URL and repackages your project into a virtual machine with all of its dependencies.
It looks for a [Travis](https://travis-ci.org/) script inside the Github repository. If there is a Travis script,
reproduce the steps to its best ability. If there is no Travis script, guess the instructions on how to rebuild the project.
For example, try `./congigure && make && sudo make install' to build a C++ project. If everything fails, come back again
in a few weeks, and try again.

## Support

It currently supports projects written in C, C++, Python, and Node.js

## Future work

- UI
- "Play" button
- Multiple languages
- Scalability
- AI
- Reproducible experiments
- Distributed systems, parallel programs
- Virtual mobile operating systems, sensors
