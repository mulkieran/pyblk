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
    tests.test_compare
    ==================

    Tests graph comparison.

    .. moduleauthor:: mulhern <amulhern@redhat.com>
"""


from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import networkx as nx

import pyblk

from ._constants import CONTEXT


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


class TestGraphDifference(object):
    """
    Test ability to find differences among graphs.
    """

    def test_equal(self, tmpdir):
        """
        Verify that two identical graphs are equivalent.
        """
        home_graph = pyblk.GenerateGraph.get_graph(CONTEXT, "home")
        pyblk.RewriteGraph.convert_graph(home_graph)
        filepath = str(tmpdir.join('test.gml'))
        nx.write_gml(home_graph, filepath)

        graph1 = nx.read_gml(filepath)
        pyblk.RewriteGraph.deconvert_graph(graph1)
        graph2 = nx.read_gml(filepath)
        pyblk.RewriteGraph.deconvert_graph(graph2)

        (diff1, diff2) = pyblk.Differences.node_differences(graph1, graph2)
        assert len(diff1) == 0 and len(diff2) == 0

    def test_empty(self):
        """
        Verify that one graph and an empty graph have the correct differences.
        """
        home_graph = pyblk.GenerateGraph.get_graph(CONTEXT, "home")
        empty_graph = nx.DiGraph()

        (diff1, diff2) = pyblk.Differences.node_differences(
           home_graph,
           empty_graph
        )

        assert pyblk.Compare.is_equivalent(diff1, home_graph)
        assert pyblk.Compare.is_equivalent(diff2, empty_graph)
