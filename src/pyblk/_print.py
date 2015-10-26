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
    pyblk._print
    ============

    Textual display of graph.

    .. moduleauthor::  mulhern <amulhern@redhat.com>
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import networkx as nx

from ._attributes import DiffStatuses


class Print(object):
    """
    Methods to print a graph as a sort of forest.
    """

    _EDGE_STR = "|--"

    @classmethod
    def indentation(cls):
        """
        Return the number of spaces for the next indentation level.

        :returns: indentation
        :rtype: int
        """
        return len(cls._EDGE_STR)

    @classmethod
    def node_string(cls, info_func, fmt, orphan, indent, node):
        """
        Get a string corresponding to the node.

        :param info_func: a function that yields information about the node
        :param fmt: a function that helps format the info
        :param bool orphan: True if this node has no parents, otherwise False
        :param int indent: start printing after ``indent`` spaces
        :param `Node` node: the node to print

        :returns: a string representation of the node info
        :rtype: str
        """
        # pylint: disable=too-many-arguments
        return (" " * indent) + \
           ("" if orphan else cls._EDGE_STR) + \
           fmt.format(*info_func(node))

    @classmethod
    def node_strings(cls, info_func, fmt, graph, orphan, indent, node):
        """
        Print nodes reachable from ``node`` including itself.

        :param `file` out: the output stream to print to
        :param info_func: a function that yields information about a node
        :param fmt: a function that helps format the info
        :param `DiGraph` graph: the graph
        :param bool orphan: True if this node has no parents, otherwise False
        :param int indent: start printing after ``indent`` spaces
        :param `Node` node: the node to print
        """
        # pylint: disable=too-many-arguments
        yield cls.node_string(info_func, fmt, orphan, indent, node)


        successors = sorted(
           graph.successors(node),
           key=lambda x: info_func(x, [0])[0]
        )
        for succ in successors:
            lines = cls.node_strings(
               info_func,
               fmt,
               graph,
               False,
               indent if orphan else indent + cls.indentation(),
               succ
            )
            for line in lines:
                yield line


class LineInfo(object):
    """
    Class that generates information for a single line.
    """
    # pylint: disable=too-few-public-methods

    @staticmethod
    def info_func(graph):
        """
        Get function that obtains information for a single line.

        :param `DiGraph` graph: the graph
        :return: a function that calculates information for a single node
        :rtype: a function
        """
        key_map = nx.get_node_attributes(graph, 'identifier')
        udev_map = nx.get_node_attributes(graph, 'UDEV')
        diffstatus_map = nx.get_node_attributes(graph, 'diffstatus')

        def the_func(node, indices=None):
            """
            Function to generate information to be printed for ``node``.

            :param `Node` node: the node
            :param indices: list of numeric indices for values or None
            :type indices: list of int or NoneType
            :returns: a list of informational strings
            :rtype: list of str

            Only values for elements at x in indices are calculated.
            If indices is None, return an item for every index.
            If indices is the empty list, return an empty list.
            """
            if indices == []:
                return []

            udev_info = udev_map.get(node)
            devname = udev_info and udev_info.get('DEVNAME')
            diffstatus = diffstatus_map.get(node)
            name = devname or key_map[node]
            if diffstatus is not None:
                if diffstatus is DiffStatuses.ADDED:
                    name = "<<%s>>" % name
                elif diffstatus is DiffStatuses.REMOVED:
                    name = ">>%s<<" % name
            return [name]

        return the_func
