"""Tests for API models."""

from __future__ import annotations

from custom_components.proxmoxve.api.models import NodeResources, ProxmoxNodeData

from .conftest import BACKUP, CONTAINER, NODE, STORAGE, VM


def test_node_resources_defaults() -> None:
    """NodeResources holds raw lists."""
    resources = NodeResources(vms=[VM], containers=[], storages=[], backups=[])
    assert resources.vms == [VM]
    assert resources.containers == []


def test_proxmox_node_data_defaults() -> None:
    """ProxmoxNodeData has empty defaults."""
    node_data = ProxmoxNodeData()
    assert node_data.node == {}
    assert node_data.vms == {}
    assert node_data.containers == {}
    assert node_data.storages == {}
    assert node_data.backups == []


def test_proxmox_node_data_with_resources() -> None:
    """ProxmoxNodeData holds indexed resources."""
    node_data = ProxmoxNodeData(
        node=NODE,
        vms={int(VM["vmid"]): VM},
        containers={int(CONTAINER["vmid"]): CONTAINER},
        storages={STORAGE["storage"]: STORAGE},
        backups=[BACKUP],
    )
    assert node_data.vms[100] == VM
    assert node_data.containers[105] == CONTAINER
    assert node_data.storages["local"] == STORAGE
    assert node_data.backups[0]["status"] == "OK"
