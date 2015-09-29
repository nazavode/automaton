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

from .classproperty import classproperty

from .exceptions import (
    AutomatonError,
    DefinitionError,
    InvalidTransitionError
)

__all__ = (
    "Event",
    "Automaton",
)


class Event(object):
    def __init__(self, source_state, dest_state):
        self.source_state = source_state
        self.dest_state = dest_state

    def __repr__(self):
        return "<Event '{}' -> '{}'>".format(self.source_state, self.dest_state)


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
        if not hasattr(cls, "__default_initial_state__"):
            cls.__default_initial_state__ = None
        # Static properties
        cls.states = classproperty(lambda kls: kls.__states__)
        cls.events = classproperty(lambda kls: kls.__events__)
        cls.default_initial_state = classproperty(lambda kls: kls.__default_initial_state__)
        return cls




class Automaton(metaclass=AutomatonMeta):

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



