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
    pyblk._types
    ============

    Types of graph nodes and edges.

    .. moduleauthor::  mulhern <amulhern@redhat.com>
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import abc

import six

@six.add_metaclass(abc.ABCMeta)
class NodeType(object):
    """
    Abstract class that represents a node type.
    """
    # pylint: disable=too-few-public-methods

    def __str__(self): # pragma: no cover
        return self.__class__.__name__
    __repr__ = __str__

class DevicePath(NodeType):
    """
    A device, uniquely identified by its device path.
    """
    # pylint: disable=too-few-public-methods
    pass

DevicePath = DevicePath() # pylint: disable=invalid-name

class WWN(NodeType):
    """
    WWN disk.
    """
    # pylint: disable=too-few-public-methods
    pass

WWN = WWN() # pylint: disable=invalid-name

class NodeTypes(object):
    """
    Enumeration of node types.
    """
    # pylint: disable=too-few-public-methods
    DEVICE_PATH = DevicePath
    WWN = WWN

    @staticmethod
    def is_type(node, node_type):
        """
        Whether ``node`` has type ``node_type``.

        :param `agraph.Edge` node: the node
        :param `EdgeType` node_type: an node type
        :returns: True if ``node`` has type ``node_type``, otherwise False
        :rtype: bool
        """
        return node.attr['nodetype'] == str(node_type)

    @staticmethod
    def types(): # pylint: disable=invalid-name
        """
        :returns: a list of all ``NodeType`` objects.
        :rtype: list of ``NodeType``
        """
        return [DevicePath, WWN]

@six.add_metaclass(abc.ABCMeta)
class EdgeType(object):
    """
    Superclass of edge types.
    """
    # pylint: disable=too-few-public-methods

    def __str__(self): # pragma: no cover
        return self.__class__.__name__
    __repr__ = __str__

class Slave(EdgeType):
    """
    Encodes slaves/holders relationship.
    """
    # pylint: disable=too-few-public-methods
    pass

Slave = Slave() # pylint: disable=invalid-name

class Partition(EdgeType):
    """
    Encodes partition relationship.
    """
    # pylint: disable=too-few-public-methods
    pass

Partition = Partition() # pylint: disable=invalid-name

class Spindle(EdgeType):
    """
    Path to spindle relationship.
    """
    # pylint: disable=too-few-public-methods
    pass

Spindle = Spindle() # pylint: disable=invalid-name

class Congruence(EdgeType):
    """
    Congruence relationship between dm devices and partitions.
    """
    # pylint: disable=too-few-public-methods
    pass

Congruence = Congruence() # pylint: disable=invalid-name

class EdgeTypes(object):
    """
    Enumeration of edge types.
    """
    # pylint: disable=too-few-public-methods
    SLAVE = Slave
    PARTITION = Partition
    SPINDLE = Spindle
    CONGRUENCE = Congruence

    @staticmethod
    def is_type(edge, edge_type):
        """
        Whether ``edge`` has type ``edge_type``.

        :param `agraph.Edge` edge: the edge
        :param `EdgeType` edge_type: an edge type
        :returns: True if ``edge`` has type ``edge_type``, otherwise False
        :rtype: bool
        """
        return edge.attr['edgetype'] == str(edge_type)
