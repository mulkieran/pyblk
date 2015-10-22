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
        :rtype: `MultiDiGraph`
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
        :param `MultiDiGraph` graph: the graph
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


class DisplayGraph(object):
    """
    Displaying a generated multigraph by transformation to a graphviz graph.
    """
    # pylint: disable=too-few-public-methods

    @staticmethod
    def convert_graph(graph):
        """
        Convert graph to graphviz format.

        :param `MultiDiGraph` graph: the graph
        :returns: a graphviz graph

        Designate its general layout and mark or rearrange nodes as appropriate.
        """
        dot_graph = nx.to_agraph(graph)
        dot_graph.graph_attr.update(rankdir="LR")
        dot_graph.layout(prog="dot")

        xformers = [
           _display.PartitionedDiskTransformer,
           _display.SpindleTransformer,
           _display.PartitionTransformer,
           _display.PartitionEdgeTransformer,
           _display.CongruenceEdgeTransformer
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
        :param `MultiDiGraph` graph: the graph
        """
        key_map = nx.get_node_attributes(graph, 'identifier')
        udev_map = nx.get_node_attributes(graph, 'UDEV')
        diffstatus_map = nx.get_node_attributes(graph, 'diffstatus')

        def info_func(node):
            """
            Function to generate information to be printed for ``node``.

            :param `Node` node: the node
            :returns: a list of informational strings
            :rtype: list of str
            """
            udev_info = udev_map.get(node)
            devname = udev_info and udev_info.get('DEVNAME')
            diffstatus = diffstatus_map.get(node)
            name = devname or key_map[node]
            if diffstatus is not None:
                if diffstatus == "added":
                    name = "<<%s>>" % name
                elif diffstatus == "removed":
                    name = ">>%s<<" % name
            return [name]

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
