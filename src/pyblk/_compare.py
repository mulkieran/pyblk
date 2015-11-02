# -*- coding: utf-8 -*-
# Copyright (C) 2015  Red Hat, Inc.
#
# This copyrighted material is made available to anyone wishing to use,
# modify, copy, or redistribute it subject to the terms and conditions of
# the GNU General Public License v.2, or (at your option) any later version.
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY expressed or implied, including the implied warranties of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
# Public License for more details.  You should have received a copy of the
# GNU General Public License along with this program; if not, write to the
# Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.  Any Red Hat trademarks that are incorporated in the
# source code or documentation are not subject to the GNU General Public
# License and may only be used or replicated with the express permission of
# Red Hat, Inc.
#
# Red Hat Author(s): Anne Mulhern <amulhern@redhat.com>

"""
    pyblk._compare
    ==============

    Compare graphs to determine if they represent the same storage
    configuration.

    .. moduleauthor::  mulhern <amulhern@redhat.com>
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import networkx as nx
import networkx.algorithms.isomorphism as iso

from ._attributes import DiffStatuses

from ._decorations import Decorator
from ._decorations import DifferenceMarkers

def _get_node_match(graph1, graph2):
    """
    Returns a function that checks equality of two nodes.

    :param `DiGraph` graph1: a graph
    :param `DiGraph` graph2: a graph
    :returns: a function that compares two graph nodes
    :rtype: node * node -> bool
    """
    attr1_dict = {
       'identifier' : nx.get_node_attributes(graph1, 'identifier'),
       'nodetype' : nx.get_node_attributes(graph1, 'nodetype')
    }

    attr2_dict = {
       'identifier' : nx.get_node_attributes(graph2, 'identifier'),
       'nodetype' : nx.get_node_attributes(graph2, 'nodetype')
    }

    def the_func(node1, node2):
        """
        Checks equality of two nodes.

        :param node1: a node
        :param node2: a node
        :returns: True if nodes are equal, otherwise False
        :rtype: bool
        """
        node1_dict = {
           'identifer' : attr1_dict['identifier'][node1],
           'nodetype' : attr1_dict['nodetype'][node1]
        }
        node2_dict = {
           'identifer' : attr2_dict['identifier'][node2],
           'nodetype' : attr2_dict['nodetype'][node2]
        }
        return node1_dict == node2_dict

    return the_func

def _node_match(attr1, attr2):
    """
    Returns True if nodes with the given attrs should be considered
    equivalent.

    :param dict attr1: attributes of first node
    :param dict attr2: attributes of second node

    :return: True if nodes are equivalent, otherwise False
    :rtype: bool
    """
    node1_dict = {
       'identifer' : attr1['identifier'],
       'nodetype' : attr1['nodetype']
    }
    node2_dict = {
       'identifer' : attr2['identifier'],
       'nodetype' : attr2['nodetype']
    }
    return node1_dict == node2_dict

class Compare(object):
    """
    Compare two storage graphs.
    """
    # pylint: disable=too-few-public-methods

    @classmethod
    def is_equivalent(cls, graph1, graph2):
        """
        Whether these graphs represent equivalent storage configurations.

        :param graph1: a graph
        :param graph2: a graph

        :returns: True if the graphs are equivalent, otherwise False
        :rtype: bool
        """
        return iso.is_isomorphic(
           graph1,
           graph2,
           _node_match,
           iso.categorical_edge_match('edgetype', None)
        )

class Differences(object):
    """
    Find the differences between two graphs, if they exist.
    """

    @staticmethod
    def node_differences(graph1, graph2, node_equal=_get_node_match):
        """
        Find the differences between graph1 and graph2 as a pair of graphs.

        :param `DiGraph` graph1: a graph
        :param `DiGraph` graph2: a graph
        :param node_equal: a function that checks if two nodes are equal
        :type node_equal: `DiGraph` * `DiGraph` -> node * node -> bool

        :returns: a pair of graphs, representing graph1 - graph2 and vice-versa
        :rtype: tuple of `DiGraph`
        """
        diff_1 = nx.DiGraph()
        diff_2 = nx.DiGraph()

        nodes_1 = graph1.nodes()
        nodes_2 = graph2.nodes()

        node_equal = node_equal(graph1, graph2)

        diff_nodes_1 = (n for n in nodes_1 if\
           not any(node_equal(n, o) for o in nodes_2))
        diff_nodes_2 = (n for n in nodes_2 if \
           not any(node_equal(n, o) for o in nodes_1))

        diff_1.add_nodes_from(diff_nodes_1)
        diff_2.add_nodes_from(diff_nodes_2)

        return (diff_1, diff_2)

    @classmethod
    def full_diff(cls, graph1, graph2):
        """
        Return a graph that shows the full difference between graph1 and graph2.

        :param `DiGraph` graph1: a graph
        :param `DiGraph` graph2: a graph
        :returns: an annotated graph composed of ``graph1`` and ``graph2``
        :rtype: DiGraph
        """
        (ldiff, rdiff) = cls.node_differences(graph1, graph2)
        graph = nx.compose(graph1, graph2, name="union")
        removed = DifferenceMarkers.node_differences(
           graph,
           ldiff,
           DiffStatuses.REMOVED
        )
        Decorator.decorate_nodes(graph, removed)
        added = DifferenceMarkers.node_differences(
           graph,
           rdiff,
           DiffStatuses.ADDED
        )
        Decorator.decorate_nodes(graph, added)
        return graph

    @classmethod
    def left_diff(cls, graph1, graph2):
        """
        Return a graph of the left difference between graph1 and graph2.

        :param `DiGraph` graph1: a graph
        :param `DiGraph` graph2: a graph
        :returns: ``graph1`` with removed nodes marked
        :rtype: DiGraph
        """
        (ldiff, _) = cls.node_differences(graph1, graph2)

        graph = graph1.copy()
        removed = DifferenceMarkers.node_differences(
           graph,
           ldiff,
           DiffStatuses.REMOVED
        )
        Decorator.decorate_nodes(graph, removed)
        return graph

    @classmethod
    def right_diff(cls, graph1, graph2):
        """
        Return a graph of the right difference between graph1 and graph2.

        :param `DiGraph` graph1: a graph
        :param `DiGraph` graph2: a graph
        :returns: ``graph2`` with added nodes marked
        :rtype: DiGraph
        """
        (_, rdiff) = cls.node_differences(graph1, graph2)

        graph = graph2.copy()
        added = DifferenceMarkers.node_differences(
           graph,
           rdiff,
           DiffStatuses.ADDED
        )
        Decorator.decorate_nodes(graph, added)
        return graph
