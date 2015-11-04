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
import functools

import six

from ._attributes import DiffStatuses


class LineArrangements(object):
    """
    Sort out nodes and their relationship to each other in printing.
    """

    @classmethod
    def node_strings_from_root(
       cls,
       info_func,
       sort_key,
       graph,
       node
    ):
        """
        Generates print information about nodes reachable from
        ``node`` including itself. Assumes that the node is a root and
        supplies some appropriate defaults.

        :param info_func: a function that yields information about a node
        :param str sort_key: key to sort on
        :param `DiGraph` graph: the graph
        :param `Node` node: the node to print

        :returns: a table of information to be used for further display
        :rtype: dict of str * object

        Fields in table:
        * diffstatus - the diffstatus of the edge to this node
        * indent - the level of indentation
        * last - whether this node is the last child of its parent
        * node - the table of information about the node itself
        * orphan - whether this node has no parents
        """
        return cls.node_strings(
           info_func,
           sort_key,
           graph,
           True,
           True,
           None,
           0,
           node
        )

    @classmethod
    def node_strings(
       cls,
       info_func,
       sort_key,
       graph,
       orphan,
       last,
       diffstatus,
       indent,
       node
    ):
        """
        Generates print information about nodes reachable from
        ``node`` including itself.

        :param info_func: a function that yields information about a node
        :param str sort_key: key to sort on
        :param `DiGraph` graph: the graph
        :param bool orphan: True if this node has no parents, otherwise False
        :param bool last: True if this node is the last child, otherwise False
        :param `DiffStatus` diffstatus: the diffstatus of the edge
        :param int indent: the indentation level
        :param `Node` node: the node to print

        :returns: a table of information to be used for further display
        :rtype: dict of str * object

        Fields in table:
        * diffstatus - the diffstatus of the edge to this node
        * indent - the level of indentation
        * last - whether this node is the last child of its parent
        * node - the table of information about the node itself
        * orphan - whether this node has no parents
        """
        # pylint: disable=too-many-arguments
        yield {
           'diffstatus' : diffstatus,
           'indent' : indent,
           'last' : last,
           'node' : info_func(node),
           'orphan' : orphan,
        }


        successors = sorted(
           graph.successors(node),
           key=lambda x: info_func(x, [sort_key])[sort_key]
        )

        for succ in successors:
            lines = cls.node_strings(
               info_func,
               sort_key,
               graph,
               False,
               succ is successors[-1],
               graph[node][succ].get('diffstatus'),
               indent if orphan else indent + 1,
               succ
            )
            for line in lines:
                yield line


class XformLines(object):
    """
    Use information to transform the fields in the line.
    """

    _EDGE_STR = "|-"
    _LAST_STR = "`-"

    @classmethod
    def indentation(cls):
        """
        Return the number of spaces for the next indentation level.

        :returns: indentation
        :rtype: int
        """
        return len(cls._EDGE_STR)

    @staticmethod
    def format_edge(edge_str, diffstatus):
        """
        Format the edge based on the ``diffstatus``.

        :returns: a formatted string
        :rtype: str
        """
        if diffstatus is None:
            return edge_str

        if diffstatus is DiffStatuses.ADDED:
            return edge_str.replace('-', '+')

        if diffstatus is DiffStatuses.REMOVED:
            return edge_str.replace('-', ' ')

        assert False

    @classmethod
    def calculate_prefix(cls, line_info):
        """
        Calculate left trailing spaces and edge characters to initial value.

        :param line_info: a map of information about the line
        :type line_info: dict of str * object

        :returns: the prefix str for the first column value
        :rtype: str
        """
        edge_string = "" if line_info['orphan'] else \
           cls.format_edge(
              (cls._LAST_STR if line_info['last'] else cls._EDGE_STR),
              line_info['diffstatus']
           )
        return " " * (line_info['indent'] * cls.indentation()) + edge_string

    @classmethod
    def xform(cls, column_headers, lines):
        """
        Transform column values and yield just the line info.

        :param column_headers: the column headers
        :type column_headers: list of str
        :param lines: information about each line
        :type lines: dict of str * object
        """
        key = column_headers[0]

        for line in lines:
            line_info = line['node']
            line_info[key] = cls.calculate_prefix(line) + line_info[key]
            yield line_info


class Print(object):
    """
    Methods to print a list of lines representing a graph.
    """

    @staticmethod
    def calculate_widths(column_headers, lines, padding):
        """
        Calculate widths of every column.

        :param column_headers: column headers
        :type column_headers: list of str
        :param lines: line infos
        :type lines: list of dict
        :param int padding: number of spaces to pad on right

        :returns: a table of key/length pairs
        :rtype: dict of str * int
        """
        widths = functools.reduce(
           lambda d, l: dict((k, max(len(l[k]), d[k])) for k in l),
           lines,
           dict((k, len(k)) for k in column_headers)
        )

        return dict((k, widths[k] + padding) for k in widths)

    @staticmethod
    def header_str(column_widths, column_headers, alignment):
        """
        Get the column headers.

        :param column_widths: map of widths of each column
        :type column_widths: dict of str * int
        :param column_headers: column headers
        :type column_headers: list of str
        :param alignment: alignment for column headers
        :type alignment: dict of str * str {'<', '>', '^'}

        :returns: the column headers
        :rtype: str
        """
        format_str = "".join(
           '{:%s%d}' % (alignment[k], column_widths[k]) for k in column_headers
        )
        return format_str.format(*column_headers)

    @staticmethod
    def format_str(column_widths, column_headers, alignment):
        """
        Format string for every data value.

        :param column_widths: map of widths of each column
        :type column_widths: dict of str * int
        :param column_headers: column headers
        :type column_headers: list of str
        :param alignment: alignment for column headers
        :type alignment: dict of str * str {'<', '>', '^'}

        :returns: a format string
        :rtype: str
        """
        return "".join(
           '{%s:%s%d}' % (k, alignment[k], column_widths[k]) \
              for k in column_headers
        )

    @classmethod
    def lines(cls, column_headers, lines, padding, alignment):
        """
        Yield lines to be printed.

        :param column_headers: column headers
        :type column_headers: list of str
        :param lines: line infos
        :type lines: list of dict
        :param int padding: number of spaces to pad on right
        :param alignment: alignment for column headers
        :type alignment: dict of str * str {'<', '>', '^'}
        """
        column_widths = cls.calculate_widths(column_headers, lines, padding)

        yield cls.header_str(column_widths, column_headers, alignment)

        fmt_str = cls.format_str(column_widths, column_headers, alignment)
        for line in lines:
            yield fmt_str.format(**line)


@six.add_metaclass(abc.ABCMeta)
class LineInfo(object):
    """
    Abstract parent class of classes that generate information for a
    single line.
    """

    supported_keys = abc.abstractproperty(
       doc="the keys this class supports"
    )

    alignment = abc.abstractproperty(
       doc='alignment for each key'
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
