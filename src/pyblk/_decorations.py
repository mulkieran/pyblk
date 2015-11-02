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
    pyblk._decorations
    ==================

    Tools to decorate networkx graphs in situ, i.e., as
    constructed rather than as read from a textual file.

    .. moduleauthor::  mulhern <amulhern@redhat.com>
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import networkx as nx

import pyudev

from ._attributes import NodeTypes


class UdevProperties(object):
    """
    Find udev properties for the device nodes of a network graph.
    """

    @staticmethod
    def decorated(graph):
        """
        Returns elements that get decorated.
        """
        node_types = nx.get_node_attributes(graph, 'nodetype')
        return (k for k in node_types \
           if node_types[k] is NodeTypes.DEVICE_PATH)

    @staticmethod
    def properties(context, element, names):
        """
        Get properties on this element.
        """
        device = pyudev.Device.from_path(context, element)
        return dict((k, device[k]) for k in names if k in device)

    @classmethod
    def udev_properties(cls, context, graph, names):
        """
        Get udev properties for graph nodes that correspond to devices.

        :param `Context` context: the udev context
        :param graph: the graph
        :param names: a list of property keys
        :type names: list of str

        :returns: dict of property name, node, property value
        :rtype: dict
        """
        udev_dict = dict()
        for node in cls.decorated(graph):
            udev_dict[node] = cls.properties(context, node, names)

        return {'UDEV' : udev_dict}


class DifferenceMarkers(object):
    """
    Difference markers, either added or removed or present.
    """
    # pylint: disable=too-few-public-methods

    @staticmethod
    def node_differences(graph, difference, value):
        """
        Get node differences in ``graph`` based on ``difference``.

        :param `DiGraph` graph: the graph
        :param `DiGraph` difference: a graph representing the difference
        :param str value: marker to add to graph

        If node is in difference, adds ``value`` as "diffstatus" attribute.
        """
        ds_dict = dict()
        for node in graph:
            if node in difference:
                ds_dict[node] = value

        return {'diffstatus': ds_dict}


class Decorator(object):
    """
    Decorate graph elements with attributes.
    """

    @staticmethod
    def _decorate(graph, properties, setter=nx.set_node_attributes):
        """
        Decorate the graph.

        :param `DiGraph` graph: the graph
        :param properties: a dict of properties
        :type properties: dict of property name -> graph element -> value
        :param setter: a function to set the attributes
        :type setter: function (one of networkx.set_{node, edge}_attributes)
        """
        for property_name, value in properties.items():
            setter(graph, property_name, value)

    @classmethod
    def decorate_nodes(cls, graph, properties):
        """
        Decorate the graph.

        :param `DiGraph` graph: the graph
        :param properties: a dict of properties
        :type properties: dict of property name -> graph element -> value
        """
        cls._decorate(graph, properties, nx.set_node_attributes)

    @classmethod
    def decorate_edges(cls, graph, properties):
        """
        Decorate the graph.

        :param `DiGraph` graph: the graph
        :param properties: a dict of properties
        :type properties: dict of property name -> graph element -> value
        """
        cls._decorate(graph, properties, nx.set_edge_attributes)
