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

from collections import namedtuple, defaultdict

from .exceptions import (
    DefinitionError,
    InvalidTransitionError,
)

__all__ = (
    "Event",
    "Automaton",
)

Event = namedtuple("Event", ["source_state", "dest_state"])


def connected_components(edges):
    inbound = defaultdict(set)
    nodes = set()
    for source_node, dest_node in edges:
        # Nodes set
        nodes.add(source_node)
        nodes.add(dest_node)
        # Inbound grade
        inbound[dest_node].add(source_node)
    #
    parent = {node: node for node in nodes}
    #
    def find(n):  # pylint: disable=invalid-name
        if parent[n] == n:
            return n
        else:
            return find(parent[n])
    #
    def union(x, y):  # pylint: disable=invalid-name
        x_root = find(x)
        y_root = find(y)
        parent[x_root] = y_root
    #
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
        if len(states) != 0:
            # Ok, we are treating the class that defines the actual FSM.
            #
            # Check graph connection:
            components = connected_components(states_to_events.keys())
            if len(components) != 1:
                raise DefinitionError("The state graph contains {} connected components: "
                                      "it must be connected.".format(len(components)))
            # Internal class members:
            cls.__states__ = states
            cls.__events__ = events_to_states
            cls.__transitions__ = states_to_events
            if cls.__default_initial_state__ is not None and cls.__default_initial_state__ not in cls.__states__:
                raise DefinitionError("Default initial state '{}' unknown.".format(cls.__default_initial_state__))
        return cls


class Automaton(metaclass=AutomatonMeta):
    __default_initial_state__ = None

    def __init__(self, initial_state=None):
        # Setup initial state
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
        #
        self._state = initial_state

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, next_state):
        transition = (self.state, next_state)
        if transition not in self.__transitions__:  # pylint: disable=no-member
            raise InvalidTransitionError("No event {} found.".format(transition))
        self._state = next_state

    def event(self, do_event):
        if do_event not in self.events():
            raise InvalidTransitionError("Unrecognized event '{}'.".format(do_event))
        next_state = self.__events__[do_event][1]  # pylint: disable=no-member
        self.state = next_state

    @classmethod
    def states(cls):
        yield from cls.__states__  # pylint: disable=no-member

    @classmethod
    def events(cls):
        yield from cls.__events__  # pylint: disable=no-member

    @classmethod
    def transitions(cls):
        yield from cls.__transitions__  # pylint: disable=no-member

    @classmethod
    def get_default_initial_state(cls):
        return cls.__default_initial_state__
