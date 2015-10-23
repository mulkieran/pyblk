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
    tests.test_write
    ================

    Tests rewriting of graph to string values.

    .. moduleauthor:: mulhern <amulhern@redhat.com>
"""


from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import networkx as nx

import pyblk

from ._constants import CONTEXT


class TestGraphWrite(object):
    """
    Test aspects of rewriting graph attributes.
    """

    def test_isomorphic(self):
        """
        Verify that after rewriting the graphs are isomorphic.
        """
        home_graph = pyblk.GenerateGraph.get_graph(CONTEXT, "home")
        new_graph = home_graph.copy()

        pyblk.Rewriter.stringize(new_graph)

        assert nx.is_isomorphic(home_graph, new_graph)
        assert len(home_graph.edges()) == len(new_graph.edges())

    def test_node_identity(self):
        """
        Verify that stringize and destringize are inverses on nodetype
        and that they do not have no effect.
        """
        home_graph = pyblk.GenerateGraph.get_graph(CONTEXT, "home")
        new_graph = home_graph.copy()

        pyblk.Rewriter.stringize(new_graph)

        home_types = nx.get_node_attributes(home_graph, 'nodetype')
        new_types = nx.get_node_attributes(new_graph, 'nodetype')

        assert home_types != new_types

        pyblk.Rewriter.destringize(new_graph)

        home_types = nx.get_node_attributes(home_graph, 'nodetype')
        new_types = nx.get_node_attributes(new_graph, 'nodetype')

        assert home_types == new_types
