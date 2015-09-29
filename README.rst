=========
Automaton
=========

A minimal Python finite-state machine.

**Automaton requires Python version 3.4 or greater.**


|build-status| |coverage-status| |documentation-status| |license-status|

Automaton is an easy to use, easy to maintain `finite-state machine`_ package for Python 3.4 or greater.
The goal here is to have something minimal to enforce correctness and to avoid clutter from useless features.

In order to define an automaton, just subclass a provided base::

    from automaton import *

    class TrafficLight(Automaton):

        go = Event("red", "green")
        slowdown = Event("green", "yellow")
        stop = Event("yellow", "red")

You're done: you now have a new *automaton* class that can be instantiated and used as a state machine::

    >>> crossroads = TrafficLight(initial_state="red")
    >>> crossroads.state
    "red"

The automaton can be operated via *events*::

    >>> crossroads.event("go")
    >>> crossroads.state
    "green"
    >>> crossroads.event("slowdown")
    >>> crossroads.state
    "yellow"

Documentation
=============

You can find the full documentation at http://automaton.readthedocs.org.

Contributors
============

Thanks to `@simone-campagna <http://github.com/simone-campagna>`_.

.. _finite-state machine:
    https://en.wikipedia.org/wiki/Finite-state_machine

.. |build-status| image:: https://travis-ci.org/fmontag451/automaton.svg?branch=master
    :target: https://travis-ci.org/fmontag451/automaton
    :alt: Build status

.. |documentation-status| image:: https://readthedocs.org/projects/automaton/badge/?version=latest
    :target: http://automaton.readthedocs.org/en/latest/?badge=latest
    :alt: Documentation status

.. |coverage-status| image:: https://coveralls.io/repos/fmontag451/automaton/badge.svg?branch=master&service=github
    :target: https://coveralls.io/github/fmontag451/automaton?branch=master
    :alt: Coverage report

.. |license-status| image:: https://img.shields.io/badge/license-Apache2.0-blue.svg
    :target: http://opensource.org/licenses/Apache2.0
    :alt: License