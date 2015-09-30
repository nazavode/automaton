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

from collections import defaultdict

from .exceptions import (
    DefinitionError,
    InvalidTransitionError,
)

__all__ = (
    "Event",
    "Automaton",
)


class EventBoundDelegate(object):
    def __init__(self, automaton_instance, event_name):
        self._automaton_instance = automaton_instance
        self._event_name = event_name

    def __call__(self, *args, **kwargs):
        return self._automaton_instance.event(self._event_name)


class Event(object):
    def __init__(self, source_state, dest_state):
        self._source_state = source_state
        self._dest_state = dest_state
        self._event_name = None

    @property
    def source_state(self):
        return self._source_state

    @property
    def dest_state(self):
        return self._dest_state

    def bind(self, name):
        self._event_name = name

    def __get__(self, instance, owner):
        if instance is None:
            return self
        else:
            return EventBoundDelegate(instance, self._event_name)


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
        events_to_states = {}
        states_to_events = {}
        states = set()
        for attr in dir(cls):
            value = getattr(cls, attr)
            if isinstance(value, Event):
                # Define transition
                transition = (value.source_state, value.dest_state)
                # Add states
                states.add(transition[0])
                states.add(transition[1])
                # Update mappings
                events_to_states[attr] = transition
                states_to_events[transition] = attr
                # Bind event names
                value.bind(attr)
        if len(states) != 0:
            # Ok, we are treating the class that defines the actual FSM.
            #
            # 1. Check graph connection:
            #
            components = connected_components(states_to_events.keys())
            if len(components) != 1:
                raise DefinitionError("The state graph contains {} connected components: "
                                      "it must be connected.".format(len(components)))
            #
            # 2. Internal class members:
            #
            cls.__states__ = states
            cls.__events__ = events_to_states
            cls.__transitions__ = states_to_events
            if cls.__default_initial_state__ is not None and cls.__default_initial_state__ not in cls.__states__:
                raise DefinitionError("Default initial state '{}' unknown.".format(cls.__default_initial_state__))
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

    @state.setter
    def state(self, next_state):
        """ Sets the current state of the automaton instance.

        Parameters
        ----------
        next_state: any
            The state to be set as automaton's state.

        Returns
        -------
        any
            The current state.

        Raises
        ------
        InvalidTransitionError
            If the specified state is incompatible given the
            automaton's transitions.
        """
        transition = (self.state, next_state)
        if transition not in self.__transitions__:  # pylint: disable=no-member
            raise InvalidTransitionError("No event {} found.".format(transition))
        self._state = next_state

    def event(self, do_event):
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
        if do_event not in self.__events__:  # pylint: disable=no-member
            raise InvalidTransitionError("Unrecognized event '{}'.".format(do_event))
        next_state = self.__events__[do_event][1]  # pylint: disable=no-member
        self.state = next_state

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
    def transitions(cls):
        """ Gives the automaton transition set.

        Returns
        -------
        iter
            The iterator over the transition set.
        """
        yield from cls.__transitions__  # pylint: disable=no-member

    @classmethod
    def get_default_initial_state(cls):
        """ Gives the automaton default initial state.

        Returns
        -------
        any
            The automaton default initial state.
        """
        return cls.__default_initial_state__
