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

from ._decorations import Decorator
from ._decorations import DifferenceMarkers


def _node_match(attr1, attr2):
    """
    Returns True if nodes with the given attrs should be considered
    equivalent.

    :param dict attr1: attributes of first node
    :param dict attr2: attributes of second node

    :return: True if nodes are equivalent, otherwise False
    :rtype: bool
    """
    type1 = attr1['nodetype']
    type2 = attr2['nodetype']

    if type1 is not type2:
        return False

    return attr1['identifier'] == attr2['identifier']


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
    def node_differences(graph1, graph2):
        """
        Find the differences between graph1 and graph2 as a pair of graphs.

        :param `DiGraph` graph1: a graph
        :param `DiGraph` graph2: a graph

        :returns: a pair of graphs, representing graph1 - graph2 and vice-versa
        :rtype: tuple of `DiGraph`
        """
        return (
           graph1.subgraph(n for n in graph1 if not n in graph2),
           graph2.subgraph(n for n in graph2 if not n in graph1)
        )

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
        removed = DifferenceMarkers.node_differences(graph, ldiff, "removed")
        Decorator.decorate(graph, removed)
        added = DifferenceMarkers.node_differences(graph, rdiff, "added")
        Decorator.decorate(graph, added)
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
        removed = DifferenceMarkers.node_differences(graph, ldiff, "removed")
        Decorator.decorate(graph, removed)
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
        added = DifferenceMarkers.node_differences(graph, rdiff, "added")
        Decorator.decorate(graph, added)
        return graph
