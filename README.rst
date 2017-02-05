=========
Automaton
=========

Pythonic finite-state machines.

|build-status| |coverage-status| |documentation-status| |codeqa| |pypi| |license-status|

Automaton is an easy to use, *pythonic* `finite-state machine`_ module for Python 3.4 or greater.
The goal here is to have something to define finite-state machines in a minimal, straightforward
and elegant way that enforces **clarity** and **correctness**.

Installation
============
Automaton is available on `pypi <https://pypi.python.org/pypi/python-automaton>`_,
so to install it just use:

.. code::

    $ pip3 install python-automaton


Dependencies
============

* `Python >= 3.4`
* `networkx <https://github.com/networkx/networkx>`_
* `tabulate <https://pypi.python.org/pypi/tabulate>`_


Getting started
===============

In order to define an automaton, just subclass a provided base:

.. code-block:: python

    from automaton import *

    class TrafficLight(Automaton):

        go = Event("red", "green")
        slowdown = Event("green", "yellow")
        stop = Event("yellow", "red")

You're done: you now have a new *automaton* definition that can be instantiated to an **initial state**:

.. code-block:: python

    crossroads = TrafficLight(initial_state="red")
    assert crossroads.state == "red"

Each **event** (also known as **transition**) is a class attribute defined by its **source state** and
**destination state**. When an *event fires*, the automaton changes its state from the *source* to the *destination*:
you can *fire* an event by calling it:

.. code-block:: python

    crossroads.go()
    assert crossroads.state == "green"
    crossroads.slowdown()
    assert crossroads.state == "yellow"

An alternative way, more convenient if triggering events progammatically, is to call the ``event()`` method:

.. code-block:: python

    crossroads.event("stop")
    assert crossroads.state == "red"

Correctness
-----------

Automaton enforces correctness in two ways:

1. checking that the requested event is *valid*, that is a transition from the current state to the destination
   state exists in the state machine definition;
#. checking whether the *state graph* representing the automaton is *connected* or not (that is it must have only
    one `connected component`_).

So, if you try to trigger an invalid event...

.. code-block:: python

    crossroads = TrafficLight(initial_state="red")
    crossroads.stop()

...you will end up with an error:

.. code::

    automaton.InvalidTransitionError: The specified event 'Event(source_states=('yellow',), dest_state='red')'
                                      is invalid in current state 'red'.


Again, trying to define a class like this...

.. code-block:: python

    class BrokenTrafficLight(Automaton):

       go = Event("red", "green")
       slowdown = Event("green", "yellow")
       # broken!
       stop = Event("black", "purple")

...will trigger an error:

.. code::

    automaton.DefinitionError: The state graph contains 2 connected components:
                               ['green', 'yellow', 'red'], ['purple', 'black']


How to visualize an automaton?
------------------------------

When things are getting complex and it seems that our automata are becoming autonomous life forms grasping to escape
our control, it could be useful to have a *human friendly* representation of their behaviour.

You can ask for the *transition table*...

.. code-block:: python

    transitiontable(TrafficLight, fmt='rst')

...and you will be presented with a nice ``reStructuredText`` snippet:

.. code::

    ========  ======  ========
    Source    Dest    Event
    ========  ======  ========
    green     yellow  slowdown
    yellow    red     stop
    red       green   go
    ========  ======  ========

You can ask for the *state graph* as well...

.. code-block:: python

    stategraph(TrafficLight, fmt='plantuml')

...and you'll end up with a proper `PlantUML <http://plantuml.com/>`_ representation...

.. code::

    @startuml
        [*] --> red
        green --> yellow : slowdown
        red --> green : go
        yellow --> red : stop
    @enduml

...that can of course be rendered through ``plantuml``:

.. image:: https://github.com/nazavode/automaton/raw/master/docs/source/_static/trafficlight.png
   :alt: Traffic Light Graph


Keep your docstrings tidy!
--------------------------

Since *automata are classes* here, it would be great to have a textual representation of the automaton's behaviour
in our docstrings. What about having one that updates itself in order to stay up-to-date with the
actual code?

Here you have it:

.. code-block:: python

    class TrafficLight(Automaton):
        """ This is a pretty standard traffic light.

        This automaton follows the behaviour defined by
        the following transition table:

        {automaton:rst}

        """

        go = Event("red", "green")
        slowdown = Event("green", "yellow")
        stop = Event("yellow", "red")

Using a standard format specifier with the ``automaton`` keyword and the proper output format (e.g.: ``rst``), *the
automaton representation will be inserted in the docstring during the class definition*, **just where it should be**:

.. code-block:: python

    >>> print(TrafficLight.__doc__)
    """ This is a pretty standard traffic light.

    This automaton follows the behaviour defined by
    the following transition table:

    ========  ======  ========
    Source    Dest    Event
    ========  ======  ========
    green     yellow  slowdown
    yellow    red     stop
    red       green   go
    ========  ======  ========

    """

*Easy!*


Documentation
=============

You can find the full documentation at http://automaton.readthedocs.org.


Changes
=======


1.3.0 *(2017-02-05)*
--------------------

Added
`````
- Enabled access to all event's attributes from automaton instances.
- New constructor parameter to initialize an automaton given an initial
  *startup* event.

Changed
```````
- Misc bugs fixed.
- Tests cleanup.
- Improved reference and documentation.


1.2.1 *(2017-01-30)*
--------------------

Fixed
`````
- Severe distribution issue: package was missing some files.
- Tox testing: ``py.test`` was running against *source files*,
  **not against the package installed in ``tox`` virtualenv**.


1.2.0 *(2017-01-29)*
--------------------

Added
`````
- Custom format specifiers for ``Automaton`` definitions (classes and instances).
- Auto-docstring completion: if requested, the automaton textual representation
  is automatically added to the ``__doc__`` class attribute.

Changed
```````
- Refactored formatting functions to more streamlined and coherent interfaces.
- Removed package, now the whole library lives in one module file.


1.1.0 *(2017-01-28)*
--------------------

Added
`````
- Automaton representation as transition table or state-transition graph.


1.0.0 *(2017-01-25)*
--------------------

Added
`````
- Functions to retrieve incoming and outgoing events from a state or a set of states.


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
