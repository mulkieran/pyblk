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
    tests.test_graphs
    =================

    Tests graph generation.

    .. moduleauthor:: mulhern <amulhern@redhat.com>
"""


from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import networkx as nx

import pyblk

import pytest

from hypothesis import given
from hypothesis import strategies
from hypothesis import Settings

from ._constants import CONTEXT
from ._constants import EITHERS

# pylint: disable=too-many-function-args

NUM_TESTS = 5

# Use conditional to avoid processing tests if number of examples is too small.
# pytest.mark.skipif allows the test to be built, resulting in a hypothesis
# error if SLAVES or HOLDERS is empty.
if len(EITHERS) == 0:
    @pytest.mark.skipif(
       True,
       reason="no slaves or holders data for tests"
    )
    class TestSysfsTraversal(object):
        # pylint: disable=too-few-public-methods
        """
        An empty test class which is always skipped.
        """
        def test_dummy(self):
            """
            A dummy test, for which pytest can show a skip message.
            """
            pass
else:
    class TestSysfsTraversal(object):
        """
        A class for testing graphs generated entirely from sysfs traversals.
        """
        @given(
           strategies.sampled_from(EITHERS),
           settings=Settings(max_examples=NUM_TESTS)
        )
        def test_slaves(self, device):
            """
            Verify slaves graph has same number of nodes as traversal.

            Traversal may contain duplicates, while graph should eliminate
            duplicates during its construction. Traversal results does not
            include origin device, graph nodes do.
            """
            slaves = list(pyblk.slaves(CONTEXT, device))
            graph = pyblk.SysfsTraversal.slaves(CONTEXT, device)
            graph_len = len(graph)
            assert len(set(slaves)) == (graph_len - 1 if graph_len else 0)

        @given(
           strategies.sampled_from(EITHERS),
           settings=Settings(max_examples=NUM_TESTS)
        )
        def test_holders(self, device):
            """
            Verify holders graph has same number of nodes as traversal.

            Traversal may contain duplicates, while graph should eliminate
            duplicates during its construction. Traversal results does not
            include origin device, graph nodes do.
            """
            holders = list(pyblk.holders(CONTEXT, device))
            graph = pyblk.SysfsTraversal.holders(CONTEXT, device)
            graph_len = len(graph)
            assert len(set(holders)) == (graph_len - 1 if graph_len else 0)

class TestSysfsGraphs(object):
    """
    Test building various graphs.
    """
    # pylint: disable=too-few-public-methods

    def test_complete(self):
        """
        There is an equivalence between the nodes in the graph
        and the devices graphed.

        Moreover, all nodes have node_type DEVICE_PATH and all edges have
        type SLAVE.
        """
        graph = pyblk.SysfsGraphs.complete(CONTEXT, subsystem="block")
        devs = list(CONTEXT.list_devices(subsystem="block"))
        assert nx.number_of_nodes(graph) == len(set(devs))
        assert set(nx.nodes(graph)) == set(d.device_path for d in devs)

        types = nx.get_node_attributes(graph, "nodetype")
        assert all(t is pyblk.NodeTypes.DEVICE_PATH for t in types.values())

        types = nx.get_edge_attributes(graph, "edgetype")
        assert all(t is pyblk.EdgeTypes.SLAVE for t in types.values())


class TestPartitionGraphs(object):
    """
    Test the partition graph.
    """
    # pylint: disable=too-few-public-methods

    def test_complete(self):
        """
        The number of nodes in the graph is strictly greater than the number of
        partition devices, as partitions have to belong to some device.
        """
        graph = pyblk.PartitionGraphs.complete(CONTEXT)
        block_devices = CONTEXT.list_devices(subsytem="block")
        partitions = list(block_devices.match_property('DEVTYPE', 'partition'))
        num_partitions = len(partitions)
        num_nodes = nx.number_of_nodes(graph)

        assert (num_partitions == 0 and num_nodes == 0) or \
           nx.number_of_nodes(graph) > len(partitions)


class TestSpindleGraphs(object):
    """
    Test spindle graphs.
    """
    # pylint: disable=too-few-public-methods

    def test_complete(self):
        """
        Assert that the graph has no cycles.
        """
        graph = pyblk.SpindleGraphs.complete(CONTEXT)
        assert nx.is_directed_acyclic_graph(graph)


class TestDMPartitionGraphs(object):
    """
    Test device mapper partition graphs.
    """
    # pylint: disable=too-few-public-methods

    def test_complete(self):
        """
        Assert that the graph has no cycles.
        """
        graph = pyblk.DMPartitionGraphs.complete(CONTEXT)
        assert nx.is_directed_acyclic_graph(graph)


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


class TestGraphComparison(object):
    """
    Compare storage graphs more or less stringently.
    """
    # pylint: disable=too-few-public-methods

    def test_equal(self, tmpdir):
        """
        Verify that two identical graphs are equivalent.
        """
        home_graph = pyblk.GenerateGraph.get_graph(CONTEXT, "home")
        pyblk.RewriteGraph.convert_graph(home_graph)
        filepath = str(tmpdir.join('test.gml'))
        nx.write_gml(home_graph, filepath)

        graph1 = nx.read_gml(filepath)
        graph2 = nx.read_gml(filepath)

        assert pyblk.Compare.is_equivalent(graph1, graph2)
