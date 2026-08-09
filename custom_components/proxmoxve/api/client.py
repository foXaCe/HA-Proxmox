"""API client for Proxmox VE."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from proxmoxer import AuthenticationError, ProxmoxAPI
from proxmoxer.core import ResourceException
import requests
from requests.exceptions import ConnectTimeout, SSLError

from homeassistant.const import (
    CONF_HOST,
    CONF_PASSWORD,
    CONF_PORT,
    CONF_TOKEN,
    CONF_USERNAME,
    CONF_VERIFY_SSL,
)

from ..const import (
    CONF_NODE,
    CONF_TOKEN_ID,
    CONF_TOKEN_SECRET,
    DEFAULT_TIMEOUT,
    DEFAULT_VERIFY_SSL,
    NODE_ONLINE,
)
from ..helpers import sanitize_config_entry
from .exceptions import (
    ProxmoxAuthError,
    ProxmoxConnectionError,
    ProxmoxNodesNotFoundError,
    ProxmoxPermissionsError,
    ProxmoxServerError,
    ProxmoxSSLError,
    ProxmoxTimeoutError,
)
from .models import NodeResources

_FORBIDDEN_STATUS_CODE_RANGE = range(400, 500)


class ProxmoxClient:
    """Wrapper around the Proxmox VE API."""

    def __init__(self, data: Mapping[str, Any]) -> None:
        """Initialize the client with config entry data."""
        self._data = sanitize_config_entry(data)
        self.proxmox: ProxmoxAPI
        self.permissions: dict[str, dict[str, int]] = {}

    @property
    def host(self) -> str:
        """Return the Proxmox VE host."""
        return str(self._data[CONF_HOST])

    def _auth_kwargs(self) -> dict[str, Any]:
        """Return the authentication kwargs for proxmoxer."""
        if self._data.get(CONF_TOKEN):
            return {
                "token_name": self._data[CONF_TOKEN_ID],
                "token_value": self._data[CONF_TOKEN_SECRET],
            }
        return {"password": self._data.get(CONF_PASSWORD)}

    def connect(self) -> None:
        """Connect to the Proxmox VE server and validate access."""
        try:
            self.proxmox = ProxmoxAPI(
                host=self._data[CONF_HOST],
                port=self._data[CONF_PORT],
                user=self._data[CONF_USERNAME],
                verify_ssl=self._data.get(CONF_VERIFY_SSL, DEFAULT_VERIFY_SSL),
                timeout=DEFAULT_TIMEOUT,
                **self._auth_kwargs(),
            )
        except AuthenticationError as err:
            raise ProxmoxAuthError from err
        except SSLError as err:
            raise ProxmoxSSLError from err
        except ConnectTimeout as err:
            raise ProxmoxTimeoutError from err
        except ResourceException as err:
            raise ProxmoxServerError from err
        except requests.exceptions.ConnectionError as err:
            raise ProxmoxConnectionError from err

        self._validate_permissions()

    def _validate_permissions(self) -> None:
        """Fetch permissions and validate nodes visibility."""
        try:
            self.permissions = self.proxmox.access.permissions.get() or {}
        except ResourceException as err:
            if err.status_code in _FORBIDDEN_STATUS_CODE_RANGE:
                raise ProxmoxPermissionsError from err
            raise ProxmoxServerError from err

        try:
            self.proxmox.nodes.get()
        except ResourceException as err:
            if err.status_code in _FORBIDDEN_STATUS_CODE_RANGE:
                raise ProxmoxNodesNotFoundError from err
            raise ProxmoxServerError from err

    def get_nodes(self) -> list[dict[str, Any]]:
        """Fetch the list of nodes (sync, for executor)."""
        try:
            return self.proxmox.nodes.get() or []
        except AuthenticationError as err:
            raise ProxmoxAuthError from err
        except SSLError as err:
            raise ProxmoxSSLError from err
        except ConnectTimeout as err:
            raise ProxmoxTimeoutError from err
        except ResourceException as err:
            if err.status_code in _FORBIDDEN_STATUS_CODE_RANGE:
                raise ProxmoxPermissionsError from err
            raise ProxmoxServerError from err
        except requests.exceptions.ConnectionError as err:
            raise ProxmoxConnectionError from err

    def fetch_all_nodes(self) -> list[tuple[dict[str, Any], NodeResources]]:
        """Fetch all nodes with their VMs, containers, storages, and backups."""
        try:
            nodes = self.proxmox.nodes.get() or []
        except AuthenticationError as err:
            raise ProxmoxAuthError from err
        except SSLError as err:
            raise ProxmoxSSLError from err
        except ConnectTimeout as err:
            raise ProxmoxTimeoutError from err
        except ResourceException as err:
            raise ProxmoxServerError from err
        except requests.exceptions.ConnectionError as err:
            raise ProxmoxConnectionError from err

        return [(node, self._get_node_data(node)) for node in nodes]

    def get_vms(self, node: str) -> list[dict[str, Any]]:
        """Fetch the list of VMs for a node (sync, for executor)."""
        try:
            return self.proxmox.nodes(node).qemu.get() or []
        except ResourceException as err:
            if err.status_code in _FORBIDDEN_STATUS_CODE_RANGE:
                raise ProxmoxPermissionsError from err
            raise ProxmoxServerError from err
        except requests.exceptions.ConnectionError as err:
            raise ProxmoxConnectionError from err

    def get_containers(self, node: str) -> list[dict[str, Any]]:
        """Fetch the list of containers for a node (sync, for executor)."""
        try:
            return self.proxmox.nodes(node).lxc.get() or []
        except ResourceException as err:
            if err.status_code in _FORBIDDEN_STATUS_CODE_RANGE:
                raise ProxmoxPermissionsError from err
            raise ProxmoxServerError from err
        except requests.exceptions.ConnectionError as err:
            raise ProxmoxConnectionError from err

    def _get_node_data(self, node: dict[str, Any]) -> NodeResources:
        """Get vms, containers, storages, and backups for a node."""
        if node.get("status") != NODE_ONLINE:
            return NodeResources(vms=[], containers=[], storages=[], backups=[])

        vms = self.proxmox.nodes(node[CONF_NODE]).qemu.get() or []
        containers = self.proxmox.nodes(node[CONF_NODE]).lxc.get() or []
        storages = self.proxmox.nodes(node[CONF_NODE]).storage.get() or []
        backups = (
            self.proxmox.nodes(node[CONF_NODE]).tasks.get(typefilter="vzdump", limit=1)
            or []
        )

        return NodeResources(
            vms=vms, containers=containers, storages=storages, backups=backups
        )

    # --- Node power actions ---

    def reboot_node(self, node: str) -> None:
        """Reboot a node."""
        self.proxmox.nodes(node).status.post(command="reboot")

    def shutdown_node(self, node: str) -> None:
        """Shut down a node."""
        self.proxmox.nodes(node).status.post(command="shutdown")

    def start_all_vms(self, node: str) -> None:
        """Start all VMs and containers on a node."""
        self.proxmox.nodes(node).startall.post()

    def stop_all_vms(self, node: str) -> None:
        """Stop all VMs and containers on a node."""
        self.proxmox.nodes(node).stopall.post()

    def suspend_all_vms(self, node: str) -> None:
        """Suspend all VMs on a node."""
        self.proxmox.nodes(node).suspendall.post()

    # --- VM power actions ---

    def start_vm(self, node: str, vmid: int) -> None:
        """Start a VM."""
        self.proxmox.nodes(node).qemu(vmid).status.start.post()

    def stop_vm(self, node: str, vmid: int) -> None:
        """Stop a VM."""
        self.proxmox.nodes(node).qemu(vmid).status.stop.post()

    def reboot_vm(self, node: str, vmid: int) -> None:
        """Reboot a VM."""
        self.proxmox.nodes(node).qemu(vmid).status.reboot.post()

    def suspend_vm(self, node: str, vmid: int) -> None:
        """Suspend a VM."""
        self.proxmox.nodes(node).qemu(vmid).status.suspend.post()

    def resume_vm(self, node: str, vmid: int) -> None:
        """Resume a VM."""
        self.proxmox.nodes(node).qemu(vmid).status.resume.post()

    def reset_vm(self, node: str, vmid: int) -> None:
        """Reset a VM."""
        self.proxmox.nodes(node).qemu(vmid).status.reset.post()

    def shutdown_vm(self, node: str, vmid: int) -> None:
        """Shut down a VM."""
        self.proxmox.nodes(node).qemu(vmid).status.shutdown.post()

    def create_vm_snapshot(self, node: str, vmid: int, name: str) -> None:
        """Create a snapshot for a VM."""
        self.proxmox.nodes(node).qemu(vmid).snapshot.post(name=name)

    # --- Container power actions ---

    def start_container(self, node: str, vmid: int) -> None:
        """Start a container."""
        self.proxmox.nodes(node).lxc(vmid).status.start.post()

    def stop_container(self, node: str, vmid: int) -> None:
        """Stop a container."""
        self.proxmox.nodes(node).lxc(vmid).status.stop.post()

    def reboot_container(self, node: str, vmid: int) -> None:
        """Reboot a container."""
        self.proxmox.nodes(node).lxc(vmid).status.reboot.post()

    def create_container_snapshot(self, node: str, vmid: int, name: str) -> None:
        """Create a snapshot for a container."""
        self.proxmox.nodes(node).lxc(vmid).snapshot.post(name=name)
