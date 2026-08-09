"""Models for Proxmox VE API responses."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True, kw_only=True)
class NodeResources:
    """Raw API resources fetched for a single Proxmox node."""

    vms: list[dict[str, Any]]
    containers: list[dict[str, Any]]
    storages: list[dict[str, Any]]
    backups: list[dict[str, Any]]


@dataclass(slots=True, kw_only=True)
class ProxmoxNodeData:
    """All resources for a single Proxmox node."""

    node: dict[str, Any] = field(default_factory=dict)
    vms: dict[int, dict[str, Any]] = field(default_factory=dict)
    containers: dict[int, dict[str, Any]] = field(default_factory=dict)
    storages: dict[str, dict[str, Any]] = field(default_factory=dict)
    backups: list[dict[str, Any]] = field(default_factory=list)
