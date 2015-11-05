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
    pyblk._graphs
    =============

    Tools to build graphs of various kinds.

    .. moduleauthor::  mulhern <amulhern@redhat.com>
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from collections import defaultdict

import networkx as nx

from ._decorations import Decorator
from ._decorations import UdevProperties

from . import _attributes
from . import _compare
from . import _display
from . import _print
from . import _structure
from . import _utils
from . import _write


class GenerateGraph(object):
    """
    Coordinate graph generating activities.
    """

    @staticmethod
    def get_graph(context, name):
        """
        Get a complete graph storage graph.

        :param `Context` context: the libudev context
        :return: the generated graph
        :rtype: `DiGraph`
        """
        graph_classes = [
           _structure.DMPartitionGraphs,
           _structure.PartitionGraphs,
           _structure.SpindleGraphs,
           _structure.SysfsBlockGraphs
        ]
        return nx.compose_all(
           (t.complete(context) for t in graph_classes),
           name=name
        )

    @staticmethod
    def decorate_graph(context, graph):
        """
        Decorate a graph with additional properties.

        :param `Context` context: the libudev context
        :param `DiGraph` graph: the graph
        """
        properties = ['DEVNAME', 'DEVPATH', 'DEVTYPE']
        table = UdevProperties.udev_properties(context, graph, properties)
        Decorator.decorate_nodes(graph, table)


class RewriteGraph(object):
    """
    Convert graph so that it is writable.
    """
    # pylint: disable=too-few-public-methods

    @staticmethod
    def convert_graph(graph):
        """
        Do any necessary graph conversions so that it can be output.

        """
        _write.Rewriter.stringize(graph)

    @staticmethod
    def deconvert_graph(graph):
        """
        Do any necessary graph conversions to a just read graph.
        """
        _write.Rewriter.destringize(graph)


class DisplayGraph(object):
    """
    Displaying a generated multigraph by transformation to a graphviz graph.
    """
    # pylint: disable=too-few-public-methods

    @staticmethod
    def convert_graph(graph):
        """
        Convert graph to graphviz format.

        :param `DiGraph` graph: the graph
        :returns: a graphviz graph

        Designate its general layout and mark or rearrange nodes as appropriate.
        """
        dot_graph = nx.to_agraph(graph)
        dot_graph.graph_attr.update(rankdir="LR")
        dot_graph.layout(prog="dot")

        xformers = [
           _display.SpindleTransformer,
           _display.PartitionTransformer,
           _display.PartitionEdgeTransformer,
           _display.CongruenceEdgeTransformer,
           _display.AddedNodeTransformer,
           _display.RemovedNodeTransformer,
           _display.AddedEdgeTransformer,
           _display.RemovedEdgeTransformer
        ]

        _display.GraphTransformers.xform(dot_graph, xformers)
        return dot_graph

class SimpleLineInfo(_print.LineInfo):
    """
    This class just generates the name by which the device is displayed.
    """

    def __init__(self, graph):
        """
        Constructor.

        :param `DiGraph` graph: the graph
        """
        self.key_map = nx.get_node_attributes(graph, 'identifier')
        self.udev_map = nx.get_node_attributes(graph, 'UDEV')
        self.diffstatus_map = nx.get_node_attributes(graph, 'diffstatus')
        self.typemap = nx.get_node_attributes(graph, 'nodetype')

    supported_keys = ['NAME', 'DEVTYPE']

    alignment = defaultdict(lambda: '<')

    def _func_name(self, node):
        """
        Calculates the field for key NAME.

        :param `Node` node: the node
        :returns: the value to display for ``node`` for key 'NAME'.
        :rtype: str
        """
        udev_info = self.udev_map.get(node)
        devname = udev_info and udev_info.get('DEVNAME')
        diffstatus = self.diffstatus_map.get(node)
        name = devname or self.key_map[node]
        if diffstatus is not None:
            if diffstatus is _attributes.DiffStatuses.ADDED:
                name = "<<%s>>" % name
            elif diffstatus is _attributes.DiffStatuses.REMOVED:
                name = ">>%s<<" % name
        return name

    def _func_type(self, node):
        """
        Calculates the field for key DEVTYPE.

        :param node: the node

        :returns: the value to display for ``node`` for key 'DEVTYPE'.
        :rtype: str
        """
        udev_info = self.udev_map.get(node)
        return udev_info and udev_info.get('DEVTYPE')

    def func_table(self, index):
        if index == 'NAME':
            return self._func_name
        if index == 'DEVTYPE':
            return self._func_type
        return lambda x: None

class PrintGraph(object):
    """
    Print a textual representation of the graph.
    """
    # pylint: disable=too-few-public-methods

    @staticmethod
    def print_graph(out, graph):
        """
        Print a graph.

        :param `file` out: print destination
        :param `DiGraph` graph: the graph
        """
        line_info = SimpleLineInfo(graph)

        roots = sorted(
           _utils.GraphUtils.get_roots(graph),
           key=lambda n: line_info.info(n)['NAME']
        )

        def node_func(node):
            """
            A function that returns the line arrangements for a root node.
            """
            return _print.LineArrangements.node_strings_from_root(
               line_info.info,
               'NAME',
               graph,
               node
            )

        lines = [l for root in roots for l in node_func(root)]
        lines = list(_print.XformLines.xform(line_info.supported_keys, lines))
        lines = _print.Print.lines(
           line_info.supported_keys,
           lines,
           2,
           line_info.alignment
        )
        for line in lines:
            print(line, end="\n", file=out)


class DiffGraph(object):
    """
    Take the difference of two graphs.
    """
    # pylint: disable=too-few-public-methods

    @staticmethod
    def do_diff(graph1, graph2, diff):
        """
        Generate the appropriate graph.

        :param `DiGraph` graph1: a graph
        :param `DiGraph` graph2: a graph
        :param str diff: the diff to perform
        """
        node_matcher = _compare.Matcher(['identifier', 'nodetype'], 'node')
        match_func = node_matcher.get_match
        edge_matcher = lambda g1, g2: lambda x, y: x == y
        if diff == "full":
            return _compare.Differences.full_diff(
               graph1,
               graph2,
               match_func,
               edge_matcher
            )
        elif diff == "left":
            return _compare.Differences.left_diff(
               graph1,
               graph2,
               match_func,
               edge_matcher
            )
        elif diff == "right":
            return _compare.Differences.right_diff(
               graph1,
               graph2,
               match_func,
               edge_matcher
            )
        else:
            assert False


class CompareGraph(object):
    """
    Compare graphs with boolean result.
    """

    @staticmethod
    def equivalent(graph1, graph2):
        """
        Do ``graph1`` and ``graph2`` have the same shape?

        The type of storage entity that a node represents is considered
        significant, but not its identity.

        :param `DiGraph` graph1: a graph
        :param `DiGraph` graph2: a graph
        :returns: True if the graphs are equivalent, otherwise False
        :rtype: bool
        """
        return _compare.Compare.is_equivalent(
           graph1,
           graph2,
           lambda x, y: x['nodetype'] is y['nodetype'],
           lambda x, y: x['edgetype'] is y['edgetype']
        )

    @staticmethod
    def identical(graph1, graph2):
        """
        Are ``graph1`` and ``graph2`` identical?

        The identity of every node matters.

        :param `DiGraph` graph1: a graph
        :param `DiGraph` graph2: a graph

        :returns: True if the graphs are identical, otherwise False
        :rtype: boolean
        """
        node_matcher = _compare.Matcher(['identifier', 'nodetype'], 'node')

        return _compare.Compare.is_equivalent(
           graph1,
           graph2,
           node_matcher.get_iso_match(),
           lambda x, y: True
        )

    @classmethod
    def compare(cls, graph1, graph2):
        """
        Calculate relationship between ``graph1`` and ``graph2``.

        :param `DiGraph` graph1: a graph
        :param `DiGraph` graph2: a graph

        :returns: 0 if identical, 1 if equivalent, otherwise 2
        :rtype: int
        """

        if cls.identical(graph1, graph2):
            return 0

        if cls.equivalent(graph1, graph2):
            return 1

        return 2
