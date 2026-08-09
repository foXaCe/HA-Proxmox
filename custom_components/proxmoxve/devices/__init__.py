"""Devices package for Proxmox VE."""

from .container import (
    CONTAINER_BINARY_SENSORS,
    CONTAINER_BUTTONS,
    CONTAINER_SENSORS,
    ProxmoxContainerBinarySensor,
    ProxmoxContainerButtonEntity,
    ProxmoxContainerSensor,
)
from .node import (
    NODE_BINARY_SENSORS,
    NODE_BUTTONS,
    NODE_SENSORS,
    ProxmoxNodeBinarySensor,
    ProxmoxNodeButtonEntity,
    ProxmoxNodeSensor,
)
from .storage import (
    STORAGE_BINARY_SENSORS,
    STORAGE_SENSORS,
    ProxmoxStorageBinarySensor,
    ProxmoxStorageSensor,
)
from .vm import (
    VM_BINARY_SENSORS,
    VM_BUTTONS,
    VM_SENSORS,
    ProxmoxVMBinarySensor,
    ProxmoxVMButtonEntity,
    ProxmoxVMSensor,
)

__all__ = [
    "CONTAINER_BINARY_SENSORS",
    "CONTAINER_BUTTONS",
    "CONTAINER_SENSORS",
    "NODE_BINARY_SENSORS",
    "NODE_BUTTONS",
    "NODE_SENSORS",
    "ProxmoxContainerBinarySensor",
    "ProxmoxContainerButtonEntity",
    "ProxmoxContainerSensor",
    "ProxmoxNodeBinarySensor",
    "ProxmoxNodeButtonEntity",
    "ProxmoxNodeSensor",
    "ProxmoxStorageBinarySensor",
    "ProxmoxStorageSensor",
    "ProxmoxVMBinarySensor",
    "ProxmoxVMButtonEntity",
    "ProxmoxVMSensor",
    "STORAGE_BINARY_SENSORS",
    "STORAGE_SENSORS",
    "VM_BINARY_SENSORS",
    "VM_BUTTONS",
    "VM_SENSORS",
]
