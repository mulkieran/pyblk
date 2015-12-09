graph [
  directed 1
  name "compose( ,  )"
  node [
    id 0
    label "/devices/pci0000:00/0000:00:1f.2/ata3/host2/target2:0:0/2:0:0:0/block/sr0"
    identifier "/devices/pci0000:00/0000:00:1f.2/ata3/host2/target2:0:0/2:0:0:0/block/sr0"
    nodetype "DevicePath"
    UDEV [
      DEVTYPE "disk"
      DEVNAME "/dev/sr0"
      DEVPATH "/devices/pci0000:00/0000:00:1f.2/ata3/host2/target2:0:0/2:0:0:0/block/sr0"
    ]
  ]
  node [
    id 1
    label "/devices/pci0000:00/0000:00:1f.2/ata1/host0/target0:0:0/0:0:0:0/block/sdb/sdb1"
    identifier "/devices/pci0000:00/0000:00:1f.2/ata1/host0/target0:0:0/0:0:0:0/block/sdb/sdb1"
    nodetype "DevicePath"
    UDEV [
      DEVTYPE "partition"
      DEVNAME "/dev/sdb1"
      DEVPATH "/devices/pci0000:00/0000:00:1f.2/ata1/host0/target0:0:0/0:0:0:0/block/sdb/sdb1"
    ]
  ]
  node [
    id 2
    label "/devices/pci0000:00/0000:00:1f.2/ata1/host0/target0:0:0/0:0:0:0/block/sda/sda2"
    identifier "/devices/pci0000:00/0000:00:1f.2/ata1/host0/target0:0:0/0:0:0:0/block/sda/sda2"
    nodetype "DevicePath"
    UDEV [
      DEVTYPE "partition"
      DEVNAME "/dev/sda2"
      DEVPATH "/devices/pci0000:00/0000:00:1f.2/ata1/host0/target0:0:0/0:0:0:0/block/sda/sda2"
    ]
  ]
  node [
    id 3
    label "/devices/pci0000:00/0000:00:1f.2/ata1/host0/target0:0:0/0:0:0:0/block/sda/sda1"
    identifier "/devices/pci0000:00/0000:00:1f.2/ata1/host0/target0:0:0/0:0:0:0/block/sda/sda1"
    nodetype "DevicePath"
    UDEV [
      DEVTYPE "partition"
      DEVNAME "/dev/sda1"
      DEVPATH "/devices/pci0000:00/0000:00:1f.2/ata1/host0/target0:0:0/0:0:0:0/block/sda/sda1"
    ]
  ]
  node [
    id 4
    label "/devices/pci0000:00/0000:00:1f.2/ata1/host0/target0:0:0/0:0:0:0/block/sdb"
    identifier "/devices/pci0000:00/0000:00:1f.2/ata1/host0/target0:0:0/0:0:0:0/block/sdb"
    nodetype "DevicePath"
    UDEV [
      DEVTYPE "disk"
      DEVNAME "/dev/sdb"
      DEVPATH "/devices/pci0000:00/0000:00:1f.2/ata1/host0/target0:0:0/0:0:0:0/block/sdb"
    ]
  ]
  node [
    id 5
    label "/devices/pci0000:00/0000:00:1f.2/ata1/host0/target0:0:0/0:0:0:0/block/sdb/sdb2"
    identifier "/devices/pci0000:00/0000:00:1f.2/ata1/host0/target0:0:0/0:0:0:0/block/sdb/sdb2"
    nodetype "DevicePath"
    UDEV [
      DEVTYPE "partition"
      DEVNAME "/dev/sdb2"
      DEVPATH "/devices/pci0000:00/0000:00:1f.2/ata1/host0/target0:0:0/0:0:0:0/block/sdb/sdb2"
    ]
  ]
  node [
    id 6
    label "0x5000c500640bdae3"
    identifier "0x5000c500640bdae3"
    nodetype "WWN"
  ]
  node [
    id 7
    label "/devices/pci0000:00/0000:00:1f.2/ata1/host0/target0:0:0/0:0:0:0/block/sda"
    identifier "/devices/pci0000:00/0000:00:1f.2/ata1/host0/target0:0:0/0:0:0:0/block/sda"
    nodetype "DevicePath"
    UDEV [
      DEVTYPE "disk"
      DEVNAME "/dev/sda"
      DEVPATH "/devices/pci0000:00/0000:00:1f.2/ata1/host0/target0:0:0/0:0:0:0/block/sda"
    ]
  ]
  node [
    id 8
    label "0x5000c500640bdaee"
    identifier "0x5000c500640bdaee"
    nodetype "WWN"
  ]
  edge [
    source 6
    target 7
    edgetype "Spindle"
  ]
  edge [
    source 8
    target 4
    edgetype "Spindle"
  ]
  edge [
    source 4
    target 1
    edgetype "Partition"
  ]
  edge [
    source 7
    target 2
    edgetype "Partition"
  ]
  edge [
    source 7
    target 3
    edgetype "Partition"
  ]
  edge [
    source 4
    target 5
    edgetype "Partition"
  ]
]
