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
    tests.test_decorations
    ======================

    Tests graph decorations.

    .. moduleauthor:: mulhern <amulhern@redhat.com>
"""


from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import networkx as nx

import pyblk

from ._constants import CONTEXT


class TestGraphNodeDecorations(object):
    """
    Test decorating structure graphs.
    """
    # pylint: disable=too-few-public-methods

    def test_devpath(self):
        """
        Test that the value of DEVPATH is the same as the key of the node.
        """
        graph = pyblk.PartitionGraphs.complete(CONTEXT)
        props = pyblk.UdevProperties.udev_properties(
           CONTEXT,
           graph,
           ['DEVPATH']
        )
        devpaths = props['UDEV']
        assert all(devpaths[k]['DEVPATH'] == k for k in devpaths)

    def test_empty_differences(self):
        """
        Test that an empty difference value leads to an empty attribute table.
        """
        graph = pyblk.PartitionGraphs.complete(CONTEXT)
        markers = pyblk.DifferenceMarkers.node_differences(
           graph,
           nx.DiGraph(),
           "present"
        )
        assert not markers['diffstatus']

    def test_equal_differences(self):
        """
        Test that an equal difference gives an attribute table w/ an entry
        for every node.
        """
        graph = pyblk.PartitionGraphs.complete(CONTEXT)
        markers = pyblk.DifferenceMarkers.node_differences(
           graph,
           graph.copy(),
           "present"
        )
        diffstats = markers['diffstatus']
        assert len(diffstats) == len(graph)
        assert all(diffstats[n] == 'present' for n in graph)


class TestNodeDecorating(object):
    """
    Test actually decorating a graph.
    """
    # pylint: disable=too-few-public-methods

    def test_decorating(self):
        """
        Test that decorating actually sets the proper value.
        """
        graph = pyblk.PartitionGraphs.complete(CONTEXT)
        nodes = graph.nodes()
        properties = {
           "dummy": dict((n, "dummy") for n in nodes)
        }
        pyblk.Decorator.decorate(graph, properties)
        values = nx.get_node_attributes(graph, "dummy").values()
        assert all(n == "dummy" for n in values)
