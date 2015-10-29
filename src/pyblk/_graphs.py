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

import networkx as nx

from ._decorations import Decorator
from ._decorations import UdevProperties

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
        Decorator.decorate(graph, table)


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
           _display.RemovedNodeTransformer
        ]

        _display.GraphTransformers.xform(dot_graph, xformers)
        return dot_graph


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
        info_func = _print.LineInfo.info_func(graph)

        roots = sorted(
           _utils.GraphUtils.get_roots(graph),
           key=lambda n: info_func(n)[0]
        )

        for root in roots:
            lines = _print.Print.node_strings(
               info_func,
               '{0}',
               graph,
               True,
               0,
               root
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
        if diff == "full":
            return _compare.Differences.full_diff(graph1, graph2)
        elif diff == "left":
            return _compare.Differences.left_diff(graph1, graph2)
        elif diff == "right":
            return _compare.Differences.right_diff(graph1, graph2)
        else:
            assert False
