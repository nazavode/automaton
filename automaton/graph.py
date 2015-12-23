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
Miscellaneous graph analysis utilities.
"""

from collections import defaultdict

__all__ = (
    "connected_components",
)


def connected_components(edges):
    """ Finds the connected components in a graph.

    Given a graph, this function finds its connected components using the
    `Union Find`_ algorithm.

    Parameters
    ----------
    edges : iterable
        Iterable of graph edges. Must have the following format::
            [
                ('source_node_1', 'dest_node_1'),
                # ...
                ('source_node_n', 'dest_node_n'),
            ]

    Returns
    -------
    set
        The set containing the nodes grouped by connected components.


    .. _Union Find: https://en.wikipedia.org/wiki/Disjoint-set_data_structure
    """
    inbound = defaultdict(set)
    nodes = set()
    for source_nodes, dest_node in edges:
        # Nodes set
        nodes.update(source_nodes)
        nodes.add(dest_node)
        # Inbound grade
        inbound[dest_node].update(source_nodes)
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
