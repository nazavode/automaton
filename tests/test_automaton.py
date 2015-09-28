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

import pytest

from automaton import *


def test_unconnected():
    # The graph representing the FSM must be connected.
    with pytest.raises(DefinitionError):
        class Unconnected(metaclass=AutomatonMeta):
            cluster1 = Event("state_a", "state_b")
            cluster2 = Event("state_c", "state_d")


def test_double_event():
    # It's ok to have multiple directed arcs between two states,
    # it seems like an elegant (but somehow not efficient) way
    # to support multiple events per transition.
    class DoubleEvent(metaclass=AutomatonMeta):
        event1 = Event("state_a", "state_b")
        event2 = Event("state_a", "state_b")


def test_definition():
    class TrafficLight(metaclass=AutomatonMeta):
        go = Event("red", "green")
        slowdown = Event("green", "yellow")
        stop = Event("yellow", "red")