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

import abc

import six


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
    def node_string(cls, info_func, fmt_func, orphan, indent, node):
        """
        Get a string corresponding to the node.

        :param info_func: a function that yields information about the node
        :param fmt_func: a function that helps format the info
        :param bool orphan: True if this node has no parents, otherwise False
        :param int indent: start printing after ``indent`` spaces
        :param `Node` node: the node to print

        :returns: a string representation of the node info
        :rtype: str
        """
        # pylint: disable=too-many-arguments
        return (" " * indent) + \
           ("" if orphan else cls._EDGE_STR) + \
           fmt_func(info_func(node))

    @classmethod
    def node_strings(
       cls,
       info_func,
       fmt_func,
       sort_key,
       graph,
       orphan,
       indent,
       node
    ):
        """
        Print nodes reachable from ``node`` including itself.

        :param `file` out: the output stream to print to
        :param info_func: a function that yields information about a node
        :param fmt_func: a function that helps format the info
        :param str sort_key: key to sort on
        :param `DiGraph` graph: the graph
        :param bool orphan: True if this node has no parents, otherwise False
        :param int indent: start printing after ``indent`` spaces
        :param `Node` node: the node to print
        """
        # pylint: disable=too-many-arguments
        yield cls.node_string(info_func, fmt_func, orphan, indent, node)


        successors = sorted(
           graph.successors(node),
           key=lambda x: info_func(x, [sort_key])[sort_key]
        )
        for succ in successors:
            lines = cls.node_strings(
               info_func,
               fmt_func,
               sort_key,
               graph,
               False,
               indent if orphan else indent + cls.indentation(),
               succ
            )
            for line in lines:
                yield line


@six.add_metaclass(abc.ABCMeta)
class LineInfo(object):
    """
    Abstract parent class of classes that generate information for a
    single line.
    """

    supported_keys = abc.abstractproperty(
       doc="the keys this class supports"
    )

    @abc.abstractmethod
    def func_table(self, key): # pragma: no cover
        """
        Calculate the function for a particular index.

        :param str key: the key
        :returns: a function to apply to a node for ``key``
        :rtype: `Node` -> str or `Node` -> NoneType
        """
        raise NotImplementedError()

    def info(self, node, keys=None):
        """
        Function to generate information to be printed for ``node``.

        :param `Node` node: the node
        :param keys: list of keys for values or None
        :type keys: list of str or NoneType
        :returns: a mapping of keys to values
        :rtype: dict of str * str

        Only values for elements at x in keys are calculated.
        If keys is None, return an item for every index.
        If keys is the empty list, return an empty dict.
        Return None for key in keys that can not be satisfied.
        """
        if keys is None:
            keys = self.supported_keys
        return dict((k, self.func_table(k)(node)) for k in keys)
