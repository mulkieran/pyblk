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
    pyblk._structure
    ================

    Tools to build and manipulate graphs of device relationships.

    .. moduleauthor::  mulhern <amulhern@redhat.com>
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from collections import namedtuple
from itertools import chain

import networkx as nx

from . import _traversal

from ._attributes import EdgeTypes
from ._attributes import NodeTypes

SysfsTraversalConfig = namedtuple(
   'SysfsTraversalConfig',
   ['recursive', 'slaves']
)


class GraphMethods(object):
    """
    Generic graph methods.
    """

    @staticmethod
    def get_node_args(nodes, node_type):
        """
        Get node arguments, along with keys.

        :param nodes: source nodes
        :type nodes: list of object
        :param `NodeType` node_type: a node type
        :returns: arguments suitable for passing to add_nodes_from()
        """
        return (
           (n, {'nodetype' : node_type, 'identifier' : n}) \
           for n in nodes
        )

    @classmethod
    def add_nodes(cls, graph, nodes, node_type):
        """
        Add nodes in ``nodes`` to graph.

        :param `DiGraph` graph: the graph
        :param nodes: source nodes
        :type nodes: list of object
        :param `NodeType` node_type: a node type

        Nodes are device_paths of each device, as these uniquely identify
        the device.
        """
        graph.add_nodes_from(cls.get_node_args(nodes, node_type))

    @classmethod
    def add_edges( # pylint: disable=too-many-arguments
       cls,
       graph,
       sources,
       targets,
       edge_type,
       source_node_type,
       target_node_type
    ):
        """
        Add edges to graph from sources to targets.

        :param `DiGraph` graph: the graph
        :param sources: source nodes
        :type sources: list of `object`
        :param targets: target nodes
        :type targets: list of `object`
        :param `EdgeType` edge_type: type for edges
        :param `NodeType` source_node_type: type for source nodes
        :param `NodeType` target_node_type: type for target nodes

        Nodes are device_paths of each device, as these uniquely identify
        the device.
        """
        graph.add_nodes_from(cls.get_node_args(sources, source_node_type))
        graph.add_nodes_from(cls.get_node_args(targets, target_node_type))

        edges = ((x, y) for x in sources for y in targets)
        graph.add_edges_from(edges, edgetype=edge_type)


class SysfsTraversal(object):
    """
    Build simple graph from the holders or slaves of a given device.
    """

    @classmethod
    def do_level(cls, graph, context, device, config):
        """
        Recursively defined function to generate a graph from ``device``.

        :param `DiGraph` graph: the graph
        :param `Context` context: the libudev context
        :param `Device` device: the device
        :param `SysfsTraversalConfig` config: traversal configuration
        """
        func = _traversal.slaves if config.slaves else _traversal.holders
        level = list(func(context, device, False))

        if config.slaves:
            sources = [device]
            targets = level
        else:
            sources = level
            targets = [device]

        if not level:
            GraphMethods.add_nodes(
               graph,
               [device.device_path],
               NodeTypes.DEVICE_PATH
            )
            return

        GraphMethods.add_edges(
           graph,
           [dev.device_path for dev in sources],
           [dev.device_path for dev in targets],
           EdgeTypes.SLAVE,
           NodeTypes.DEVICE_PATH,
           NodeTypes.DEVICE_PATH
        )

        if config.recursive:
            for dev in level:
                cls.do_level(graph, context, dev, config)

    @classmethod
    def sysfs_traversal(cls, context, device, config):
        """
        General graph of a sysfs traversal.

        :param `Context` context: the libudev context
        :param `Device` device: the device
        :param `SysfsTraversalConfig` config: traversal configuration
        :returns: a graph
        :rtype: `DiGraph`
        """
        graph = nx.DiGraph()
        cls.do_level(graph, context, device, config)
        return graph

    @classmethod
    def holders(cls, context, device, recursive=True):
        """
        Yield graph of slaves of device, including the device.

        :param `Context` context: the libudev context
        :param `Device` device: the device
        :param bool recursive: True for recursive, False otherwise
        :returns: a graph
        :rtype: `DiGraph`
        """
        config = SysfsTraversalConfig(slaves=False, recursive=recursive)
        return cls.sysfs_traversal(context, device, config)

    @classmethod
    def slaves(cls, context, device, recursive=True):
        """
        Yield graph of slaves of device, including the device.

        :param `Context` context: the libudev context
        :param `Device` device: the device
        :param bool recursive: True for recursive, False otherwise
        :returns: a graph
        :rtype: `DiGraph`
        """
        config = SysfsTraversalConfig(slaves=True, recursive=recursive)
        return cls.sysfs_traversal(context, device, config)


class SysfsGraphs(object):
    """
    Build sysfs graphs in various ways.
    """

    @staticmethod
    def slaves_and_holders(context, device, recursive=True):
        """
        Make a graph of slaves and holders of a device.

        :param `Context` context: the libudev context
        :param `Device` device: the device
        :param bool recursive: True for recursive, False otherwise
        :returns: a graph
        :rtype: `DiGraph`
        """
        return nx.compose(
           SysfsTraversal.slaves(context, device, recursive),
           SysfsTraversal.holders(context, device, recursive)
        )

    @classmethod
    def parents_and_children(cls, context, device):
        """
        Make a graph of the parents and children of a device.

        :param `Context` context: the libudev context
        :param `Device` device: the device
        :returns: a graph
        :rtype: `DiGraph`
        """
        return cls.slaves_and_holders(context, device, recursive=False)

    @classmethod
    def complete(cls, context, **kwargs):
        """
        Build a complete graph showing all devices.

        :param `Context` context: a udev context
        :param kwargs: arguments for filtering the devices.
        :returns: a graph
        :rtype: `DiGraph`
        """
        devices = (d for d in context.list_devices(**kwargs))
        graphs = (cls.parents_and_children(context, d) for d in devices)
        return nx.compose_all(chain([nx.DiGraph()], graphs), name="sysfs")


class SysfsBlockGraphs(object): # pragma: no cover
    """
    Composes holders/slaves graphs for block devices.
    """
    # pylint: disable=too-few-public-methods

    @staticmethod
    def complete(context):
        """
        Build a complete graph showing all block devices.

        :param `Context` context: a udev context
        :returns: a graph
        :rtype: `DiGraph`
        """
        return SysfsGraphs.complete(context, subsystem="block")


class PartitionGraphs(object):
    """
    Build graphs of partition relationships.
    """

    @staticmethod
    def partition_graph(device):
        """
        Make a graph of partition relationships.

        :param `Device` device: the partition device
        :returns: a graph
        :rtype: `DiGraph`
        """
        graph = nx.DiGraph()
        parent = device.parent
        GraphMethods.add_edges(
           graph,
           [device.device_path],
           [parent.device_path],
           EdgeTypes.PARTITION,
           NodeTypes.DEVICE_PATH,
           NodeTypes.DEVICE_PATH
        )
        return graph

    @classmethod
    def complete(cls, context):
        """
        Build a complete graph of all partitions.

        :param `Context` context: a udev context
        :returns: a graph
        :rtype: `DiGraph`
        """
        block_devices = context.list_devices(subsystem="block")
        partitions = block_devices.match_property('DEVTYPE', 'partition')
        graphs = (cls.partition_graph(d) for d in partitions)
        return nx.compose_all(
           chain([nx.DiGraph()], graphs),
           name="partiton"
        )


class SpindleGraphs(object):
    """
    Build graphs of relationships with actual physical disks.
    """

    @staticmethod
    def spindle_graph(device):
        """
        Make a graph of spindle relationships.

        :param `Device` device: the partition device
        :returns: a graph
        :rtype: `DiGraph`
        """
        graph = nx.DiGraph()

        wwn = device.get('ID_WWN_WITH_EXTENSION')
        if wwn is None:
            return graph

        GraphMethods.add_edges(
           graph,
           [device.device_path],
           [wwn],
           EdgeTypes.SPINDLE,
           NodeTypes.DEVICE_PATH,
           NodeTypes.WWN
        )
        return graph

    @classmethod
    def complete(cls, context):
        """
        Build a complete graph showing path/spindle relationships.

        :param `Context` context: a udev context
        :returns: a graph
        :rtype: `DiGraph`
        """
        block_devices = context.list_devices(subsystem="block")
        disks = block_devices.match_property('DEVTYPE', 'disk')
        graphs = (cls.spindle_graph(d) for d in disks)
        return nx.compose_all(
           chain([nx.DiGraph()], graphs),
           name='spindle'
        )


class DMPartitionGraphs(object):
    """
    Build graphs of relationships between device mapper devices and partitions.
    """

    @staticmethod
    def congruence_graph(context, device):
        """
        Build a graph of congruence relation between device mapper devices and
        partition devices.

        :param `Context` context: a udev context
        :param `Device` device: the partition device
        :returns: a graph
        :rtype: `DiGraph`
        """
        graph = nx.DiGraph()

        id_part_entry_uuid = device.get('ID_PART_ENTRY_UUID')
        if id_part_entry_uuid is None:
            return graph

        block_devices = context.list_devices(subsystem="block")
        disks = block_devices.match_property('DEVTYPE', 'disk')

        block_devices = context.list_devices(subsystem="block")
        matches = block_devices.match_property(
           'ID_PART_ENTRY_UUID',
           id_part_entry_uuid
        )

        sources = set(disks) & set(matches)

        GraphMethods.add_edges(
           graph,
           [dev.device_path for dev in sources],
           [device.device_path],
           EdgeTypes.CONGRUENCE,
           NodeTypes.DEVICE_PATH,
           NodeTypes.DEVICE_PATH
        )

        return graph

    @classmethod
    def complete(cls, context):
        """
        Build a complete graph showing device mapper, partition relationships.

        :param `Context` context: a udev context
        :returns: a graph
        :rtype: `DiGraph`
        """
        block_devices = context.list_devices(subsystem="block")
        partitions = block_devices.match_property('DEVTYPE', 'partition')
        graphs = (cls.congruence_graph(context, d) for d in partitions)
        return nx.compose_all(
           chain([nx.DiGraph()], graphs),
           name='congruence'
        )

class Graph(object):
    """
    Build a graph according to specifications.
    """
    # pylint: disable=too-few-public-methods

    @staticmethod
    def graph(context, name, classes):
        """
        Build a graph using the designated classes.

        :param context: a context
        :param str name: a name for the graph
        :param classes: a list of graph classes
        :type classes: list of type
        :returns: a graph
        :rtype: nx.DiGraph
        """
        return nx.compose_all(
            (t.complete(context) for t in classes),
            name=name
        )
