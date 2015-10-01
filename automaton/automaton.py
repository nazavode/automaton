# -*- coding: utf-8 -*-
#
# Copyright 2015 Federico Ficarelli
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
A minimal Python finite-state machine implementation.
"""

from collections import namedtuple, defaultdict

from .exceptions import (
    DefinitionError,
    InvalidTransitionError,
)

__all__ = (
    "Event",
    "Automaton",
)


class EventBoundDelegate(object):  # pylint: disable=too-few-public-methods
    """ Class that delegates a call to an :class:`~automaton.automaton.Event`
    bound to a specific :class:`~automaton.automaton.Automaton` definition subclass. """

    def __init__(self, automaton_instance, event_name):
        self._automaton_instance = automaton_instance
        self._event_name = event_name

    def __call__(self, *args, **kwargs):
        return self._automaton_instance.event(self._event_name)


EventBase = namedtuple("Event", ("source_state", "dest_state"))


class Event(EventBase):
    """ Class that represents a state transition.

     Parameters
     ----------
     source_state : any
         The transition source state.
     dest_state : any
         The transition destination state.
    """

    def __new__(cls, *args, **kwargs):
        instance = super().__new__(cls, *args, **kwargs)
        instance._event_name = None  # pylint: disable=protected-access
        instance._event_delegate = None  # pylint: disable=protected-access
        return instance

    @property
    def name(self):
        """ The actual user-defined name of the event as an
        :class:`~automaton.automaton.Automaton` class member.
        If None, the Event isn't bounded to any specific
        :class:`~automaton.automaton.Automaton` subclass. """
        return self._event_name

    def bind(self, name):
        """ Binds the :class:`~automaton.automaton.Event` instance
        to a particular event name.

        .. warning::
            This method is intended to be called by the automaton
            definition mechanics.

        Parameters
        ----------
        name : str
            The event name to be bounded.
        """
        self._event_name = name

    def __get__(self, instance, owner):
        """ Enables the descriptor semantics on
        :class:`~automaton.automaton.Event` instances. """
        if instance is None:
            return self
        else:
            if self._event_delegate is None:
                self._event_delegate = EventBoundDelegate(instance, self._event_name)
            return self._event_delegate


def connected_components(edges):
    """ Finds the connected components in a graph.

    Given a graph, this function finds its connected components using the
    `Union Find`_ algorithm.

    Parameters
    ----------
    edges : dict
        The list of graph edges.
        The dictionary must have the following form::
            {
                ('source_node_1', 'dest_node_1'),
                # ...
                ('source_node_n', 'dest_node_n'),
            }

    Returns
    -------
    set
        The set containing the nodes grouped by connected components.

    .. _Union Find: https://en.wikipedia.org/wiki/Disjoint-set_data_structure
    """
    inbound = defaultdict(set)
    nodes = set()
    for source_node, dest_node in edges:
        # Nodes set
        nodes.add(source_node)
        nodes.add(dest_node)
        # Inbound grade
        inbound[dest_node].add(source_node)
    parent = {node: node for node in nodes}

    def find(n):  # pylint: disable=invalid-name, missing-docstring
        if parent[n] == n:
            return n
        else:
            return find(parent[n])

    def union(x, y):  # pylint: disable=invalid-name, missing-docstring
        x_root = find(x)
        y_root = find(y)
        parent[x_root] = y_root

    for u in nodes:  # pylint: disable=invalid-name
        for v in inbound[u]:  # pylint: disable=invalid-name
            if find(u) != find(v):
                union(u, v)
    components = set()
    for node in nodes:
        if parent[node] == node:
            components.add(node)
    return components


class AutomatonMeta(type):
    """ The metaclass that must be applied on the ``automaton``-enabled classes'
    hierarchy.

    The :meth:`~automaton.automaton.AutomatonMeta.__new__` method builds the
    actual finite-state machine based on the user-provided events definition.
    """

    def __new__(mcs, class_name, class_bases, class_dict):
        cls = super().__new__(mcs, class_name, class_bases, class_dict)
        events = {}
        states = set()
        for attr in dir(cls):
            value = getattr(cls, attr)
            if isinstance(value, Event):
                # Important: bind event to its name as a class member
                value.bind(attr)
                # Collect states
                states.add(value[0])
                states.add(value[1])
                # Collect events
                events[attr] = value
        if len(states) != 0:  # if we are dealing with an automaton definition class...
            # 1. Setup class members:
            cls.__states__ = states
            cls.__events__ = events
            if cls.__default_initial_state__ is not None \
                    and cls.__default_initial_state__ not in cls.__states__:
                raise DefinitionError("Default initial state '{}' unknown.".format(cls.__default_initial_state__))
            # 2. Check states graph consistency:
            components = connected_components(events.values())
            if len(components) != 1:
                raise DefinitionError("The state graph contains {} connected components: "
                                      "it must be connected.".format(len(components)))
        return cls


class Automaton(metaclass=AutomatonMeta):
    """ Base class for automaton types.

    In order to define an automaton, this class must be the base for the
    provided machine definition:

    >>> class MyClass(Automaton):
    ...     transition = Event("state_a", "state_b")

    Parameters
    ----------
    initial_state : any, optional
        The initial state for this automaton instance. Defaults to None.
        Note that if automaton type has no default initial state
        (specified via :attr:`~automaton.automaton.__default_initial_state__`),
        this argument must be specified.

    Raises
    ------
    DefinitionError
        The automaton type has no default initial state while no
        custom initial state specified during construction *or* the
        specified initial state is unknown.
    """

    __default_initial_state__ = None

    def __init__(self, initial_state=None):
        #
        # 1. Initial state setup
        #
        if initial_state is None:
            if self.__default_initial_state__ is None:
                raise DefinitionError(
                    "No default initial state defined for '{}', must be specified "
                    "in costruction.".format(self.__class__)
                )
            else:
                initial_state = self.__default_initial_state__
        # Check initial state correctness
        if initial_state not in self.__states__:  # pylint: disable=no-member
            raise DefinitionError("Initial state '{}' unknown.".format(initial_state))
        # And finally set initial state
        self._state = initial_state

    @property
    def state(self):
        """ Gets the current state of the automaton instance.

        Returns
        -------
        any
            The current state.
        """
        return self._state

    def event(self, event_name):
        """ Signals the occurrence of an event and evolves the automaton
        to the destination state.

        Parameters
        ----------
        do_event : any
            The event to be performed on the automaton.

        Raises
        ------
        InvalidTransitionError
            The specified event is unknown.
        """
        if event_name not in self.__events__:  # pylint: disable=no-member
            raise InvalidTransitionError("Unrecognized event '{}'.".format(event_name))
        transition = self.__events__[event_name]  # pylint: disable=no-member
        if transition.source_state != self._state:
            raise InvalidTransitionError(
                "The specified event '{}' is invalid in current state '{}'.".format(transition, self._state))
        self._state = transition.dest_state

    @classmethod
    def states(cls):
        """ Gives the automaton state set.

        Returns
        -------
        iter
            The iterator over the state set.
        """
        yield from cls.__states__  # pylint: disable=no-member

    @classmethod
    def events(cls):
        """ Gives the automaton events set.

        Returns
        -------
        iter
            The iterator over the events set.
        """
        yield from cls.__events__  # pylint: disable=no-member

    @classmethod
    def get_default_initial_state(cls):
        """ Gives the automaton default initial state.

        Returns
        -------
        any
            The automaton default initial state.
        """
        return cls.__default_initial_state__
