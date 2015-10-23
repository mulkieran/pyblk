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
    pyblk._write
    ============

    Tools to write out a graph.

    .. moduleauthor::  mulhern <amulhern@redhat.com>
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import networkx as nx

from ._types import EdgeTypes
from ._types import NodeTypes


class Rewriter(object):
    """
    Rewrite graph for output.
    """
    # pylint: disable=too-few-public-methods

    @staticmethod
    def stringize(graph):
        """
        Xform node and edge types to strings.
        """
        edge_types = nx.get_edge_attributes(graph, 'edgetype')
        for key, value in edge_types.items():
            edge_types[key] = str(value)
        nx.set_edge_attributes(graph, 'edgetype', edge_types)

        node_types = nx.get_node_attributes(graph, 'nodetype')
        for key, value in node_types.items():
            node_types[key] = str(value)
        nx.set_node_attributes(graph, 'nodetype', node_types)

    @staticmethod
    def destringize(graph):
        """
        Xform node and edge type strings to objects.
        """
        edge_types = nx.get_edge_attributes(graph, 'edgetype')
        for key, value in edge_types.items():
            edge_types[key] = EdgeTypes.get_type(value)
        nx.set_edge_attributes(graph, 'edgetype', edge_types)

        node_types = nx.get_node_attributes(graph, 'nodetype')
        for key, value in node_types.items():
            node_types[key] = NodeTypes.get_type(value)
        nx.set_node_attributes(graph, 'nodetype', node_types)
