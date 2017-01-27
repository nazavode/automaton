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

from weakref import WeakKeyDictionary
from itertools import chain, product, filterfalse
from collections import namedtuple, Iterable

import tabulate as tabulator
import networkx as nx


__all__ = (
    "Event",
    "Automaton",
    "AutomatonError",
    "DefinitionError",
    "InvalidTransitionError",
    "transition_table",
    "plantuml",
    "tabulate",
)


class AutomatonError(Exception):
    """ Exception representing a generic error occurred in the automaton. """
    pass


class DefinitionError(AutomatonError):
    """ Exception representing an error occurred during the automaton definition. """
    pass


class InvalidTransitionError(AutomatonError):
    """ Exception representing an invalid transition. """
    pass


EventBase = namedtuple("Event", ("source_states", "dest_state"))


def unique_everseen(iterable, key=None):  # pragma: no cover
    """List unique elements, preserving order. Remember all elements ever seen.

        >>> list(unique_everseen('AAAABBBCCDAABBB'))
        ['A', 'B', 'C', 'D']
        >>> list(unique_everseen('ABBCcAD', str.lower))
        ['A', 'B', 'C', 'D']

    .. note::
        Recipe taken from: https://docs.python.org/3.6/library/itertools.html
    """
    seen = set()
    seen_add = seen.add
    if key is None:
        for element in filterfalse(seen.__contains__, iterable):
            seen_add(element)
            yield element
    else:
        for element in iterable:
            k = key(element)
            if k not in seen:
                seen_add(k)
                yield element


class Event(EventBase):
    """ Class that represents a state transition.

    .. important::
        This is a read-only data descriptor type.

    Parameters
    ----------
    source_states : any
        The transition source state.
    dest_state : any
        The transition destination state.
    """

    def __new__(cls, source_states, dest_state):
        # Fix source states:
        if isinstance(source_states, str) or not isinstance(source_states, Iterable):
            source_states = (source_states,)
        instance = super().__new__(cls, source_states, dest_state)
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

    def edges(self, data=False):
        """ Provides all the single transition edges associated
        to this event.

        .. note::
            Since an event can have multiple source states,
            in graph terms it represents a set of state-to-state
            edges.

        Parameters
        ----------
        data : bool, optional
            If set, data associated to the corresponding edge
            will be added to the edge tuple. Defaults to `False`.

        Yields
        ------
        (any, any) or (any, any, dict)
            All the `(source, dest)` tuples representing the graph
            edges associated to the event. If `data` parameter is set,
            each tuple will be appended with the `dict` containing
            edge data (by default the `'event'` key containing the
            event name).
        """
        components = [self.source_states, (self.dest_state, )]
        if data:
            components.append((dict(event=self.name), ))
        yield from product(*components)

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
            if not hasattr(self, '__bound_instances'):
                # pylint: disable=attribute-defined-outside-init
                self.__bound_instances = WeakKeyDictionary()
            if instance not in self.__bound_instances:
                self.__bound_instances[instance] = lambda: instance.event(self._event_name)
            return self.__bound_instances[instance]

    def __set__(self, instance, value):
        """ Enables the descriptor semantics on
        :class:`~automaton.automaton.Event` instances.

        Raises
        ------
        AttributeError
            To enforce read-only data descriptor semantics.
        """
        raise AttributeError("Can't set attribute")


class AutomatonMeta(type):
    """ The metaclass that must be applied on the ``automaton``-enabled classes'
    hierarchy.

    The :meth:`~automaton.automaton.AutomatonMeta.__new__` method builds the
    actual finite-state machine based on the user-provided events definition.

    Raises
    ------
    DefinitionError
        If the states graph isn't connected (that is leads to unreachable states).
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
                states.update(value[0])  # Iterable of sources states, let's update the set
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
            if cls.__default_accepting_states__ is not None:
                for state in cls.__default_accepting_states__:
                    if state not in cls.__states__:
                        raise DefinitionError("Default accepting state '{}' unknown.".format(state))
            # 2. Build graph
            graph = nx.MultiDiGraph()
            graph.add_nodes_from(states)
            graph.add_edges_from(chain.from_iterable(list(event.edges(data=True)) for event in events.values()))
            # 3. Check states graph consistency:
            if not nx.is_weakly_connected(graph):
                components = list(nx.weakly_connected_component_subgraphs(graph))
                raise DefinitionError(
                    "The state graph contains {} connected components: {}".format(
                        len(components), ", ".join("{}".format(c.nodes()) for c in components))
                )
            # 4. Save
            cls.__graph__ = nx.freeze(graph)
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

    accepting_states : iterable, optional
        The accepting states for this automaton instance. Defaults to None.
        Note that if automaton type has default accepting states
        (specified via :attr:`~automaton.automaton.__default_accepting_states__`),
        this argument takes precedence over that.

    Raises
    ------
    DefinitionError
        The automaton type has no default initial state while no
        custom initial state specified during construction *or* the
        specified initial state is unknown.
    """

    __default_initial_state__ = None
    """any: The default initial state for the automaton type."""

    __default_accepting_states__ = None
    """iterable: The default accepting states for the automaton type."""

    def __init__(self, initial_state=None, accepting_states=None):
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
        # ...and finally set initial state.
        self._state = initial_state
        #
        # 2. Accepting states setup
        #
        if accepting_states is None:
            if self.__default_accepting_states__ is None:
                accepting_states = ()
            else:
                accepting_states = self.__default_accepting_states__
        for state in accepting_states:
            if state not in self.__states__:  # pylint: disable=no-member
                raise DefinitionError("Accepting state '{}' unknown.".format(state))
        # ...and finally set accepting states.
        self._accepting_states = frozenset(accepting_states)

    @property
    def state(self):
        """ Gets the current state of the automaton instance.

        Returns
        -------
        any
            The current state.
        """
        return self._state

    @property
    def is_accepted(self):
        """ Gets the current automaton's acceptance state.

        Returns
        -------
        bool
            True if the current state is an accepting state, False otherwise.
        """
        return self._state in self._accepting_states

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
        if self._state not in transition.source_states:
            raise InvalidTransitionError(
                "The specified event '{}' is invalid in current state '{}'.".format(transition, self._state))
        self._state = transition.dest_state

    @classmethod
    def _get_cut(cls, *states, inbound=True):
        """ Retrieves all the events that form a cut for the
        all the specified subgraphs.

        Parameters
        ----------
        states : tuple(any)
            The states subset.
        inbound : bool
            If set, the inbound events will be returned,
            outbound otherwise. Defaults to `True`.

        Raises
        ------
        KeyError
            When an unknown state is found while iterating.

        Yields
        ------
        any
            All the inbound or outbound events.
        """
        unknown = set(states) - cls.__states__  # pylint: disable=no-member
        if unknown:
            raise KeyError("Unknown states: {}".format(unknown))
        edges_getter = \
            cls.__graph__.in_edges if inbound else cls.__graph__.out_edges  # pylint: disable=no-member
        yield from unique_everseen(
            edge[2]['event'] for edge in edges_getter(states, data=True)
        )

    @classmethod
    def states(cls):
        """ Gives the automaton state set.

        Yields
        ------
        any
            The iterator over the state set.
        """
        yield from cls.__states__  # pylint: disable=no-member

    @classmethod
    def events(cls):
        """ Gives the automaton events set.

        Yields
        ------
        any
            The iterator over the events set.
        """
        yield from cls.__events__  # pylint: disable=no-member

    @classmethod
    def in_events(cls, *states):
        """ Retrieves all the inbound events entering the
        specified states with no duplicates.

        Parameters
        ----------
        states : tuple(any)
            The states subset.

        Raises
        ------
        KeyError
            When an unknown state is found while iterating.

        Yields
        ------
        any
            The events entering the specified states.
        """
        yield from cls._get_cut(*states, inbound=True)

    @classmethod
    def out_events(cls, *states):
        """ Retrieves all the outbound events leaving the
        specified states with no duplicates.

        Raises
        ------
        KeyError
            When an unknown state is found while iterating.

        Parameters
        ----------
        states : tuple(any)
            The states subset.

        Yields
        ------
        any
            The events that exit the specified states.
        """
        yield from cls._get_cut(*states, inbound=False)

    @classmethod
    def get_default_initial_state(cls):
        """ Gives the automaton default initial state.

        Returns
        -------
        any
            The automaton default initial state.
        """
        return cls.__default_initial_state__

    def __str__(self):
        return '<{}@{}>'.format(self.__class__.__name__, self.state)


#########################################################################
# Rendering stuff, everything beyond this point is formatting for humans.

def plantuml(automaton, traversal=None):
    """ Render an automaton's state-transition graph as a
    `PlantUML state diagram <http://plantuml.com/state-diagram>`_.

    A simple example will be formatted as follows:

        >>> class TrafficLight(Automaton):
        ...     go = Event('red', 'green')
        ...     slowdown = Event('green', 'yellow')
        ...     stop = Event('yellow', 'red')
        >>> print( plantuml(TrafficLight) )  # doctest: +SKIP

        @startuml
            green --> yellow : slowdown
            yellow --> red : stop
            red --> green : go
        @enduml

    Parameters
    ----------
    automaton : `~automaton.Automaton`
        The automaton to be rendered. It can be both
        a class and an instance.
    traversal : callable(graph), optional
        An optional callable used to sort the events.
        It has the same meaning as the ``traversal``
        parameter of `automaton.transition_table`.

    Returns
    -------
    str
        Returns the formatted state graph.
    """
    graph = automaton.__graph__
    source_nodes = filter(lambda n: not graph.in_edges(n), graph.nodes())
    sink_nodes = filter(lambda n: not graph.out_edges(n), graph.nodes())
    sources = [('[*]', node) for node in source_nodes]
    sinks = [(node, '[*]') for node in sink_nodes]
    table = transition_table(automaton, traversal=traversal)
    return """@startuml
{}
{}
{}
@enduml""".format('\n'.join(['    {} --> {}'.format(*row) for row in sources]),
                  '\n'.join(['    {} --> {} : {}'.format(*row) for row in table]),
                  '\n'.join(['    {} --> {}'.format(*row) for row in sinks]))


def transition_table(automaton, traversal=None):
    """ Build the adjacency table of the given graph.

    Parameters
    ----------
    automaton : `~automaton.Automaton`
        The automaton to be rendered. It can be both
        a class and an instance.
    traversal : callable(graph), optional
        An optional callable used to yield the
        edges of the graph representation of the
        automaton. It must accept a `networkx.MultiDiGraph`
        as the first positional argument
        and yield one edge at a time as a tuple in the
        form ``(source_state, destination_state)``. The default
        traversal sorts the states in ascending order by
        inbound grade (number of incoming events).

    Yields
    ------
    (source, dest, event)
        Yields one row at a time as a tuple containing
        the source and destination node of the edge and
        the name of the event associated with the edge.
    """
    graph = automaton.__graph__
    if not traversal:
        traversal = lambda G: sorted(G.edges(), key=lambda e: len(G.in_edges(e[0])))
    # Retrieve event names since networkx traversal
    # functions lack data retrieval
    events = nx.get_edge_attributes(graph, 'event')  # -> (source, dest, key==0): event
    # Build raw data table to be rendered
    for source, dest in traversal(graph):
        yield (source, dest, events[source, dest, 0])


def tabulate(automaton, header=None, tablefmt=None, traversal=None):
    """ Render an automaton's transition table as in
    text format.

    The transition table has three columns: source node,
    destination node and the name of the event.

    A simple example will be formatted as follows:

        >>> class TrafficLight(Automaton):
        ...     go = Event('red', 'green')
        ...     slowdown = Event('green', 'yellow')
        ...     stop = Event('yellow', 'red')
        >>> tabulate(TrafficLight) # doctest: +SKIP

        ========  ======  ========
        Source    Dest    Event
        ========  ======  ========
        green     yellow  slowdown
        yellow    red     stop
        red       green   go
        ========  ======  ========

    Parameters
    ----------
    automaton : `~automaton.Automaton`
        The automaton to be rendered. It can be both
        a class and an instance.
    header : list[str, str, str]
        An optional list of fields to be used as table
        headers. Defaults to a predefined header.
    tablefmt str, optional
        Specifies the output format for the table.
        All formats supported by
        `tabulate <https://pypi.python.org/pypi/tabulate>`_
        package are supported (e.g.: ``rst`` for
        reStructuredText, ``pipe`` for Markdown).
        Defaults to ``rst``.
    traversal : callable(graph), optional
        An optional callable used to sort the events.
        It has the same meaning as the ``traversal``
        parameter of `automaton.transition_table`.

    Returns
    -------
    str
        Returns the formatted transition table.
    """
    header = header or ['Source', 'Dest', 'Event']
    tablefmt = tablefmt or 'rst'
    table = transition_table(automaton=automaton, traversal=traversal)
    return tabulator.tabulate(table, header, tablefmt=tablefmt)
