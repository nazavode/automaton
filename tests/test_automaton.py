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

# flake8: noqa

import pytest

from automaton import *

###############################################################################
# Fixtures

@pytest.fixture
def TrafficLight():
    class _TrafficLight(Automaton):
        __default_initial_state__ = 'red'
        __default_accepting_states__ = ('red', 'green')
        go = Event('red', 'green')
        slowdown = Event('green', 'yellow')
        stop = Event('yellow', 'red')
    return _TrafficLight


@pytest.fixture
def Sink():
    class _Sink(Automaton):
        __default_initial_state__ = 'state_a'
        event1 = Event('state_a', 'state_b')
        event2 = Event(('state_a', 'state_b', 'state_c', 'state_d'), 'sink1')
        event3 = Event(('state_a', 'state_b', 'state_c', 'state_d'), 'sink2')
        event4 = Event('sink2', 'state_a')
    return _Sink


@pytest.fixture(params=[None, lambda G: G.edges(data=False)])
def traversal(request):
    return request.param

###############################################################################
# Tests

def test_str_transition(TrafficLight):
    auto = TrafficLight()
    assert str(auto) == '<{}@{}>'.format(TrafficLight.__name__, auto.state)
    auto.go()
    assert str(auto) == '<{}@{}>'.format(TrafficLight.__name__, auto.state)


@pytest.mark.parametrize('fmt', [''] +
                         list(transitiontable.SUPPORTED_FORMATS) +
                         list(stategraph.SUPPORTED_FORMATS))
def test_format_specifiers(TrafficLight, fmt):
    auto = TrafficLight()
    fmtstr = '{:' + fmt + '}'
    formatted_inst = fmtstr.format(auto)
    formatted_class = fmtstr.format(TrafficLight)
    if fmt:
        assert formatted_inst == formatted_class
    assert formatted_class
    assert formatted_class != fmtstr
    assert formatted_inst
    assert formatted_inst != fmtstr


def test_docstring_substitution():
    class NoDoc(Automaton):
        event1 = Event('state_a', 'state_b')

    class EmptyDoc(Automaton):
        """"""
        e = Event('a', 'b')

    class FullDoc(Automaton):
        """This is a test class"""
        event1 = Event('state_a', 'state_b')

    class SubstitutionDoc(Automaton):
        """ This is the automaton representation:
        {automaton:plantuml}
        """
        event1 = Event('state_a', 'state_b')

    assert NoDoc.__doc__ is None
    assert EmptyDoc.__doc__ == """"""
    assert FullDoc.__doc__ == """This is a test class"""
    assert SubstitutionDoc.__doc__
    assert SubstitutionDoc.__doc__ != """ This is the automaton representation:
    {automaton:plantuml}
    """
    '{automaton:plantuml}'.format(automaton=SubstitutionDoc) in SubstitutionDoc.__doc__
    assert stategraph(SubstitutionDoc) in SubstitutionDoc.__doc__


def test_definition():
    class Simple(Automaton):
        __default_initial_state__ = 'state_a'
        event1 = Event('state_a', 'state_b')
        event2 = Event('state_b', 'state_c')

    # Class properties
    assert Simple.get_default_initial_state() == 'state_a'
    assert 'event1' in Simple.events()
    assert 'event2' in Simple.events()
    assert 'event3' not in Simple.events()
    assert 'state_a' in Simple.states()
    assert 'state_b' in Simple.states()
    assert 'state_c' in Simple.states()
    assert 'unknown' not in Simple.states()
    # Instantiation
    simple_obj = Simple()
    # Class properties through instance
    assert simple_obj.get_default_initial_state() == 'state_a'
    assert 'event1' in simple_obj.events()
    assert 'event2' in simple_obj.events()
    assert 'event3' not in simple_obj.events()


def test_proxy():
    class Simple(Automaton):
        __default_initial_state__ = 'state_a'
        event1 = Event('state_a', 'state_b')

    s = Simple()

    assert Simple.event1.name == s.event1.name
    assert Simple.event1.source_states == s.event1.source_states
    assert Simple.event1.dest_state == s.event1.dest_state
    with pytest.raises(TypeError):
        Simple.event1()
    s.event1()


def test_initial_state():
    # Invalid initial state
    with pytest.raises(DefinitionError):
        class Wrong(Automaton):
            __default_initial_state__ = 'unknown'
            event1 = Event('state_a', 'state_b')
            event2 = Event('state_b', 'state_c')

    # Initial state not defined
    class NoInit(Automaton):
        event1 = Event('state_a', 'state_b')
        event2 = Event('state_b', 'state_c')

    assert NoInit.get_default_initial_state() is None
    with pytest.raises(DefinitionError):
        noinit_obj = NoInit()
    with pytest.raises(DefinitionError):
        noinit_obj = NoInit(initial_state='unknown')
    for state in 'state_a', 'state_b', 'state_c':
        noinit_obj = NoInit(initial_state=state)
        assert noinit_obj.get_default_initial_state() is None
        assert noinit_obj.state == state


def test_unconnected_naive():
    # The graph representing the FSM must be connected.
    with pytest.raises(DefinitionError):
        class Unconnected(Automaton):
            cluster1 = Event('state_a', 'state_b')
            cluster2 = Event('state_c', 'state_d')


@pytest.mark.xfail
def test_empty():
    class Empty(Automaton):
        pass
    assert not list(Empty.events())
    assert not list(Empty.states())


def test_unconnected():
    # The graph representing the FSM must be connected.
    with pytest.raises(DefinitionError):
        class Unconnected(Automaton):
            cluster1_1 = Event('state_a', 'state_b')
            cluster1_2 = Event('state_b', 'state_c')
            cluster1_3 = Event('state_c', 'state_d')
            #
            cluster2_1 = Event('state_e', 'state_f')
            cluster2_2 = Event('state_f', 'state_g')
            cluster2_3 = Event('state_g', 'state_h')
            #
            cluster3_1 = Event('state_1', 'state_2')
            cluster3_2 = Event('state_2', 'state_3')
            cluster3_3 = Event('state_3', 'state_4')
            cluster3_4 = Event('state_4', 'state_5')
            cluster3_5 = Event('state_5', 'state_6')
            cluster3_6 = Event('state_6', 'state_7')


def test_connected_clusters():
    # Connect the clusters:
    class Unconnected(Automaton):
        cluster1_1 = Event('state_a', 'state_b')
        cluster1_2 = Event('state_b', 'state_c')
        cluster1_3 = Event('state_c', 'state_d')
        #
        cluster2_1 = Event('state_e', 'state_f')
        cluster2_2 = Event('state_f', 'state_g')
        cluster2_3 = Event('state_g', 'state_h')
        #
        cluster3_1 = Event('state_1', 'state_2')
        cluster3_2 = Event('state_2', 'state_3')
        cluster3_3 = Event('state_3', 'state_4')
        cluster3_4 = Event('state_4', 'state_5')
        cluster3_5 = Event('state_5', 'state_6')
        cluster3_6 = Event('state_6', 'state_7')
        #
        conn_1_2 = Event('state_d', 'state_e')
        conn_2_3 = Event('state_h', 'state_1')


def test_multiple_arcs():
    # It's ok to have multiple directed arcs between two states,
    # it seems like an elegant (but somehow not efficient) way
    # to support multiple events per transition.
    class Multiple(Automaton):
        event1 = Event('state_a', 'state_b')
        event2 = Event('state_a', 'state_b')
        event3 = Event('state_a', 'state_b')

    assert 'event1' in Multiple.events()
    assert 'event2' in Multiple.events()
    assert 'event3' in Multiple.events()


def test_auto_arc():
    class Auto(Automaton):
        loop = Event('state_a', 'state_a')

    assert 'loop' in Auto.events()
    auto_obj = Auto(initial_state='state_a')
    assert auto_obj.state == 'state_a'
    auto_obj.event('loop')
    assert auto_obj.state == 'state_a'


def test_transition(TrafficLight):
    crossroads = TrafficLight()
    # Initial state
    assert crossroads.state == 'red'
    # Transitions
    crossroads.event('go')
    assert crossroads.state == 'green'
    crossroads.event('slowdown')
    assert crossroads.state == 'yellow'
    crossroads.event('stop')
    assert crossroads.state == 'red'
    crossroads.event('go')
    assert crossroads.state == 'green'
    # Invalid transitions
    with pytest.raises(InvalidTransitionError):
        crossroads.event('stop')
    assert crossroads.state == 'green'
    with pytest.raises(InvalidTransitionError):
        crossroads.event('unknown')
    assert crossroads.state == 'green'


def test_event_binding(TrafficLight):
    assert TrafficLight.go.name == 'go'
    assert TrafficLight.slowdown.name == 'slowdown'
    assert TrafficLight.stop.name == 'stop'


def test_event_descriptor(TrafficLight):
    crossroads = TrafficLight()
    with pytest.raises(AttributeError):
        crossroads.go = None


def test_event_methods(TrafficLight):
    crossroads = TrafficLight()
    # Initial state
    assert crossroads.state == 'red'
    # Transitions
    crossroads.go()
    assert crossroads.state == 'green'
    crossroads.slowdown()
    assert crossroads.state == 'yellow'
    crossroads.stop()
    assert crossroads.state == 'red'
    crossroads.go()
    assert crossroads.state == 'green'
    # Invalid transitions
    with pytest.raises(InvalidTransitionError):
        crossroads.stop()
    assert crossroads.state == 'green'


def test_invalid_default_accepting_states():
    with pytest.raises(DefinitionError):
        class Wrong(Automaton):
            __default_accepting_states__ = ('event1', 'unknown')
            event1 = Event('state_a', 'state_b')


def test_default_accepting_states(TrafficLight):
    crossroads = TrafficLight()
    # Initial state
    assert crossroads.state == 'red'
    assert crossroads.is_accepted
    # Transitions
    crossroads.go()
    assert crossroads.state == 'green'
    assert crossroads.is_accepted
    crossroads.slowdown()
    assert crossroads.state == 'yellow'
    assert not crossroads.is_accepted
    crossroads.stop()
    assert crossroads.state == 'red'
    assert crossroads.is_accepted
    crossroads.go()
    assert crossroads.state == 'green'
    assert crossroads.is_accepted
    # Invalid transitions
    with pytest.raises(InvalidTransitionError):
        crossroads.stop()
    assert crossroads.state == 'green'
    assert crossroads.is_accepted


def test_custom_accepting_states(TrafficLight):
    crossroads = TrafficLight(accepting_states=('yellow', ))
    # Initial state
    assert crossroads.state == 'red'
    assert not crossroads.is_accepted
    # Transitions
    crossroads.go()
    assert crossroads.state == 'green'
    assert not crossroads.is_accepted
    crossroads.slowdown()
    assert crossroads.state == 'yellow'
    assert crossroads.is_accepted
    crossroads.stop()
    assert crossroads.state == 'red'
    assert not crossroads.is_accepted
    crossroads.go()
    assert crossroads.state == 'green'
    assert not crossroads.is_accepted
    # Invalid transitions
    with pytest.raises(InvalidTransitionError):
        crossroads.stop()
    assert crossroads.state == 'green'
    assert not crossroads.is_accepted


def test_invalid_custom_accepting_states(TrafficLight):
    with pytest.raises(DefinitionError):
        crossroads = TrafficLight(accepting_states=('yellow', 'unknown'))


def test_sink_state():
    sources = ('state_a', 'state_b', 'state_c', 'state_d')

    class Sink(Automaton):
        event1 = Event(sources, 'sink')

    for initial in sources:
        auto = Sink(initial_state=initial)
        assert auto.state == initial
        auto.event1()
        assert auto.state == 'sink'
        with pytest.raises(InvalidTransitionError):
            auto.event1()


def test_sink_state_complex():
    class Sink(Automaton):
        event1 = Event('state_a', 'state_b')
        event2 = Event(('state_a', 'state_b', 'state_c', 'state_d'), 'sink1')
        event3 = Event(('state_a', 'state_b', 'state_c', 'state_d', 'sink1'), 'sink2')

    auto = Sink(initial_state='state_a')
    auto.event1()
    assert auto.state == 'state_b'
    auto.event2()
    assert auto.state == 'sink1'
    auto.event3()
    assert auto.state == 'sink2'


def test_sink_state_loop():
    class Sink(Automaton):
        event1 = Event('state_a', 'state_b')
        event2 = Event(('state_a', 'state_b', 'state_c', 'state_d'), 'sink1')
        event3 = Event(('state_a', 'state_b', 'state_c', 'state_d', 'sink1'), 'sink2')
        event4 = Event('sink2', 'state_a')

    auto = Sink(initial_state='state_a')
    auto.event1()
    assert auto.state == 'state_b'
    auto.event2()
    assert auto.state == 'sink1'
    auto.event3()
    assert auto.state == 'sink2'
    auto.event4()
    assert auto.state == 'state_a'
    auto.event1()
    assert auto.state == 'state_b'
    auto.event2()
    assert auto.state == 'sink1'
    auto.event3()
    assert auto.state == 'sink2'
    auto.event4()
    assert auto.state == 'state_a'


def test_star():
    edges = ('state_a', 'state_b', 'state_c', 'state_d', 'state_e')

    class Star(Automaton):
        collapse = Event(edges, 'center')

    for edge in edges:
        auto = Star(initial_state=edge)
        assert auto.state == edge
        auto.collapse()
        assert auto.state == 'center'
        with pytest.raises(InvalidTransitionError):
            auto.collapse()
        assert auto.state == 'center'


def test_in_events():
    edges = ('state_a', 'state_b', 'state_c', 'state_d', 'state_e')

    class Star(Automaton):
        collapse = Event(edges, 'center')
        collapse2 = Event('state_f', 'center')

    for state in edges:
        assert set(Star.in_events(state)) == set()

    assert set(Star.in_events(*edges)) == set()

    assert set(Star.in_events('center')) == {'collapse', 'collapse2'}

    assert set(Star.in_events()) == set()

    with pytest.raises(KeyError):
        set(Star.in_events('unknown1', 'unknown2'))  # Unknown state

    with pytest.raises(KeyError):
        set(Star.in_events('unknown1', 'unknown2', 'center'))  # Unknown state


def test_out_events():
    edges = ('state_a', 'state_b', 'state_c', 'state_d', 'state_e')

    class Star(Automaton):
        collapse = Event(edges, 'center')
        collapse2 = Event('state_f', 'center')
        collapse3 = Event('state_f', 'center')
        collapse4 = Event('state_f', 'center')

    for state in edges:
        assert set(Star.out_events(state)) == {'collapse'}

    assert set(Star.out_events(*edges)) == {'collapse'}

    assert set(Star.out_events('state_f')) == {'collapse2', 'collapse3', 'collapse4'}

    assert set(Star.out_events('center')) == set()

    assert set(Star.out_events()) == set()

    with pytest.raises(KeyError):
        set(Star.out_events('unknown1', 'unknown2'))  # Unknown state

    with pytest.raises(KeyError):
        set(Star.out_events('unknown1', 'unknown2', 'center'))  # Unknown state


def test_event_edges(Sink):
    event = Event('a', 'b')
    event._bind('testevent')
    assert list(event.edges()) == [('a', 'b')]
    assert list(event.edges(data=True)) == [('a', 'b', {'event': 'testevent'})]
    #
    event = Event(('a', 'b', 'c', 'd'), 'x')
    event._bind('testevent')
    assert list(event.edges()) == [('a', 'x'), ('b', 'x'), ('c', 'x'), ('d', 'x')]
    assert list(event.edges(data=True)) == [('a', 'x', {'event': 'testevent'}),
        ('b', 'x', {'event': 'testevent'}), ('c', 'x', {'event': 'testevent'}),
        ('d', 'x', {'event': 'testevent'})]
    # Class
    assert list(Sink.event2.edges()) == \
        [('state_a', 'sink1'), ('state_b', 'sink1'), ('state_c', 'sink1'), ('state_d', 'sink1')]
    # Instance
    assert list(Sink().event2.edges()) == \
        [('state_a', 'sink1'), ('state_b', 'sink1'), ('state_c', 'sink1'), ('state_d', 'sink1')]


@pytest.mark.parametrize('header', [None, [], [1, 2, 3], ['a', 'b', 'c']])
@pytest.mark.parametrize('fmt', [None, ''] + list(transitiontable.SUPPORTED_FORMATS))
def test_transitiontable(Sink, header, fmt, traversal):
    # Class
    assert transitiontable(Sink, header=header, fmt=fmt, traversal=traversal)
    # Instance
    assert transitiontable(Sink(), header=header, fmt=fmt, traversal=traversal)


@pytest.mark.parametrize('fmt', [None, ''] + list(stategraph.SUPPORTED_FORMATS))
def test_stategraph(Sink, fmt, traversal):
    # Class
    assert stategraph(Sink, fmt=fmt, traversal=traversal)
    # Instance
    assert stategraph(Sink(), fmt=fmt, traversal=traversal)


def test_get_table(Sink, traversal):
    # Class
    table = list(get_table(Sink, traversal=traversal))
    assert table
    assert len(table) == 10
    for row in table:
        assert len(row) == 3
    # Instance
    assert list(get_table(Sink(), traversal=traversal)) == table


def test_get_dest_state(Sink):
    # Class
    assert Sink.event1.dest_state == 'state_b'
    assert Sink.event2.dest_state == 'sink1'
    assert Sink.event3.dest_state == 'sink2'
    assert Sink.event4.dest_state == 'state_a'
    # Instance
    s = Sink()
    assert s.event1.dest_state == 'state_b'
    assert s.event2.dest_state == 'sink1'
    assert s.event3.dest_state == 'sink2'
    assert s.event4.dest_state == 'state_a'


@pytest.mark.xfail
def test_initial_event(Sink):
    s = Sink(initial_event='event1')
    assert s.state == 'state_b'
    s.event2()
    assert s.state == 'sink1'
    s = Sink(initial_event='event2')
    assert s.state == 'sink1'
    s = Sink(initial_event='event3')
    assert s.state == 'sink2'
    s = Sink(initial_event='event4')
    assert s.state == 'state_1'
    with pytest.raises(InvalidTransitionError):
        s = Sink(initial_event='unknown')
    with pytest.raises(InvalidTransitionError):
        s = Sink(initial_event=1.0)
