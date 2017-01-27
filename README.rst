=========
Automaton
=========

A minimal Python finite-state machine.

*Automaton requires Python version 3.4 or greater.*


|build-status| |coverage-status| |documentation-status| |codeqa| |pypi| |license-status|

Automaton is an easy to use, easy to maintain `finite-state machine`_ package for Python 3.4 or greater.
The goal here is to have something minimal to enforce correctness and to avoid clutter from useless features.

In order to define an automaton, just subclass a provided base:

    >>> from automaton import *
    >>>
    >>> class TrafficLight(Automaton):
    >>>
    >>>     go = Event("red", "green")
    >>>     slowdown = Event("green", "yellow")
    >>>     stop = Event("yellow", "red")

You're done: you now have a new *automaton* definition that can be instantiated and used as a state machine:

    >>> crossroads = TrafficLight(initial_state="red")
    >>> crossroads.state
    "red"

The automaton can be operated via *events*: signalling the occurrence of an event to the state machine triggers the
evolution of the automaton from an initial state to a final state. You can trigger an event calling the class
attributes themeselves:

    >>> crossroads.go()
    >>> crossroads.state
    "green"
    >>> crossroads.slowdown()
    >>> crossroads.state
    "yellow"

An alternative way, more convenient if triggering events progammatically, is to call the ``event()`` method:

    >>> crossroads.event("stop")
    >>> crossroads.state
    "red"

Automaton enforces correctness in two ways:

1. checking that the requested event is *valid*, that is a transition from the current state to the destination
   state exists in the state machine definition;
#. checking whether the *state graph* representing the automaton is *connected* or not (that is it must have only
   one `connected component`_).


Documentation
=============

You can find the full documentation at http://automaton.readthedocs.org.


Changes
=======

**unreleased**


.. _finite-state machine:
    https://en.wikipedia.org/wiki/Finite-state_machine

.. _connected component:
    https://en.wikipedia.org/wiki/Connected_component_(graph_theory)

.. |build-status| image:: https://travis-ci.org/nazavode/automaton.svg?branch=master
    :target: https://travis-ci.org/nazavode/automaton
    :alt: Build status

.. |documentation-status| image:: https://readthedocs.org/projects/automaton/badge/?version=latest
    :target: http://automaton.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

.. |coverage-status| image:: https://codecov.io/gh/nazavode/automaton/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/nazavode/automaton
    :alt: Coverage report

.. |license-status| image:: https://img.shields.io/badge/license-Apache2.0-blue.svg
    :target: http://opensource.org/licenses/Apache2.0
    :alt: License

.. |codeqa| image:: https://api.codacy.com/project/badge/Grade/0eb6d3a1a1b04030852e153b13f7cbc9
   :target: https://www.codacy.com/app/federico-ficarelli/automaton?utm_source=github.com&utm_medium=referral&utm_content=nazavode/automaton&utm_campaign=badger
   :alt: Codacy Badge
   
.. |pypi| image:: https://badge.fury.io/py/python-automaton.svg
    :target: https://badge.fury.io/py/python-automaton
    :alt: PyPI
   
