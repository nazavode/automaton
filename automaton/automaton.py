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

from collections import namedtuple

from .classproperty import classproperty

from .exceptions import (
    DefinitionError,
    InvalidTransitionError
)

__all__ = (
    "Event",
    "Automaton",
)


Event = namedtuple("Event", ["source_state", "dest_state"])


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
        # Internal class members
        cls.__states__ = states
        cls.__events__ = events_to_states
        cls.__transitions__ = states_to_events
        if cls.__default_initial_state__ is not None and cls.__default_initial_state__ not in cls.__states__:
            raise DefinitionError("Default initial state '{}' unknown.".format(cls.__default_initial_state__))
        # Static properties
        cls.states = classproperty(lambda kls: kls.__states__)
        cls.events = classproperty(lambda kls: kls.__events__)
        cls.transitions = classproperty(lambda kls: kls.__transitions__)
        cls.default_initial_state = classproperty(lambda kls: kls.__default_initial_state__)
        return cls


class Automaton(metaclass=AutomatonMeta):

    __default_initial_state__ = None

    def __init__(self, initial_state=None):
        # Setup initial state
        if initial_state is None:
            if self.default_initial_state is None:  # pylint: disable=no-member
                raise DefinitionError(
                    "No default initial state defined for '{}', must be specified "
                    "in costruction.".format(self.__class__)
                )
            else:
                initial_state = self.default_initial_state  # pylint: disable=no-member
        # Check initial state correctness
        if initial_state not in self.states:  # pylint: disable=no-member
            raise DefinitionError("Initial state '{}' unknown.".format(initial_state))
        #
        self._state = initial_state

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, next_state):
        transition = (self.state, next_state)
        if transition not in self.transitions:  # pylint: disable=no-member
            raise InvalidTransitionError("No event {} found.".format(transition))
        self._state = next_state

    def event(self, do_event):
        if do_event not in self.events:  # pylint: disable=no-member
            raise InvalidTransitionError("Unrecognized event '{}'.".format(do_event))
        next_state = self.events[do_event][1]  # pylint: disable=no-member
        self.state = next_state
