"""Tests for the Proxmox API client."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from proxmoxer import AuthenticationError
from proxmoxer.core import ResourceException
import requests

from custom_components.proxmoxve.api.client import ProxmoxClient
from custom_components.proxmoxve.api.exceptions import (
    ProxmoxAuthError,
    ProxmoxConnectionError,
    ProxmoxNodesNotFoundError,
    ProxmoxPermissionsError,
    ProxmoxServerError,
    ProxmoxSSLError,
    ProxmoxTimeoutError,
)

from .conftest import (
    CONTAINER,
    MOCK_HOST,
    MOCK_PASSWORD,
    MOCK_TOKEN_ID,
    MOCK_TOKEN_SECRET,
    NODE,
    VM,
    _config_entry_data,
)


def _client(**overrides: object) -> ProxmoxClient:
    """Build a client from config data."""
    data = _config_entry_data()
    for key, value in overrides.items():
        data[key] = value
    return ProxmoxClient(data)


def test_client_host_property() -> None:
    """host property returns configured host."""
    client = _client()
    assert client.host == MOCK_HOST


def test_client_password_auth_kwargs() -> None:
    """Password auth produces password kwargs."""
    client = _client()
    kwargs = client._auth_kwargs()
    assert kwargs == {"password": MOCK_PASSWORD}


def test_client_token_auth_kwargs() -> None:
    """Token auth produces token kwargs."""
    client = _client(
        **{
            "token": True,
            "password": None,
            "token_id": MOCK_TOKEN_ID,
            "token_value": MOCK_TOKEN_SECRET,
        }
    )
    kwargs = client._auth_kwargs()
    assert kwargs == {
        "token_name": "mock",
        "token_value": MOCK_TOKEN_SECRET,
    }


@patch("custom_components.proxmoxve.api.client.ProxmoxAPI")
def test_connect_success(mock_api: MagicMock) -> None:
    """connect initializes the API and fetches permissions."""
    instance = mock_api.return_value
    instance.access.permissions.get.return_value = {"/vms": {"VM.Audit": 1}}
    instance.nodes.get.return_value = [NODE]
    client = _client()
    client.connect()
    mock_api.assert_called_once()
    assert client.permissions == {"/vms": {"VM.Audit": 1}}


@patch("custom_components.proxmoxve.api.client.ProxmoxAPI")
def test_connect_auth_error(mock_api: MagicMock) -> None:
    """AuthenticationError during init raises ProxmoxAuthError."""
    mock_api.side_effect = AuthenticationError("bad")
    client = _client()
    with pytest.raises(ProxmoxAuthError):
        client.connect()


@patch("custom_components.proxmoxve.api.client.ProxmoxAPI")
def test_connect_ssl_error(mock_api: MagicMock) -> None:
    """SSLError during init raises ProxmoxSSLError."""
    mock_api.side_effect = requests.exceptions.SSLError("cert")
    client = _client()
    with pytest.raises(ProxmoxSSLError):
        client.connect()


@patch("custom_components.proxmoxve.api.client.ProxmoxAPI")
def test_connect_timeout(mock_api: MagicMock) -> None:
    """ConnectTimeout during init raises ProxmoxTimeoutError."""
    mock_api.side_effect = requests.exceptions.ConnectTimeout("slow")
    client = _client()
    with pytest.raises(ProxmoxTimeoutError):
        client.connect()


@patch("custom_components.proxmoxve.api.client.ProxmoxAPI")
def test_connect_connection_error(mock_api: MagicMock) -> None:
    """ConnectionError during init raises ProxmoxConnectionError."""
    mock_api.side_effect = requests.exceptions.ConnectionError("down")
    client = _client()
    with pytest.raises(ProxmoxConnectionError):
        client.connect()


@patch("custom_components.proxmoxve.api.client.ProxmoxAPI")
def test_connect_permissions_forbidden(mock_api: MagicMock) -> None:
    """4xx on permissions raises ProxmoxPermissionsError."""
    instance = mock_api.return_value
    instance.access.permissions.get.side_effect = ResourceException(
        403, "forbidden", ""
    )
    client = _client()
    with pytest.raises(ProxmoxPermissionsError):
        client.connect()


@patch("custom_components.proxmoxve.api.client.ProxmoxAPI")
def test_connect_permissions_server_error(mock_api: MagicMock) -> None:
    """5xx on permissions raises ProxmoxServerError."""
    instance = mock_api.return_value
    instance.access.permissions.get.side_effect = ResourceException(500, "boom", "")
    client = _client()
    with pytest.raises(ProxmoxServerError):
        client.connect()


@patch("custom_components.proxmoxve.api.client.ProxmoxAPI")
def test_connect_nodes_forbidden(mock_api: MagicMock) -> None:
    """4xx on nodes raises ProxmoxNodesNotFoundError."""
    instance = mock_api.return_value
    instance.access.permissions.get.return_value = {}
    instance.nodes.get.side_effect = ResourceException(401, "forbidden", "")
    client = _client()
    with pytest.raises(ProxmoxNodesNotFoundError):
        client.connect()


@patch("custom_components.proxmoxve.api.client.ProxmoxAPI")
def test_get_nodes(mock_api: MagicMock) -> None:
    """get_nodes returns the raw node list."""
    instance = mock_api.return_value
    instance.nodes.get.return_value = [NODE]
    client = _client()
    client.proxmox = instance
    assert client.get_nodes() == [NODE]


@patch("custom_components.proxmoxve.api.client.ProxmoxAPI")
def test_fetch_all_nodes(mock_api: MagicMock) -> None:
    """fetch_all_nodes gathers resources per node."""
    instance = mock_api.return_value
    instance.nodes.get.return_value = [NODE]
    instance.nodes(NODE["node"]).qemu.get.return_value = []
    instance.nodes(NODE["node"]).lxc.get.return_value = []
    instance.nodes(NODE["node"]).storage.get.return_value = []
    instance.nodes(NODE["node"]).tasks.get.return_value = []
    client = _client()
    client.proxmox = instance
    pairs = client.fetch_all_nodes()
    assert len(pairs) == 1
    node, resources = pairs[0]
    assert node["node"] == NODE["node"]
    assert resources.vms == []
    assert resources.containers == []
    assert resources.storages == []


@patch("custom_components.proxmoxve.api.client.ProxmoxAPI")
def test_fetch_all_nodes_offline_skips_fetch(mock_api: MagicMock) -> None:
    """Offline nodes skip VM/container/storage fetch."""
    offline_node = {**NODE, "status": "offline"}
    instance = mock_api.return_value
    instance.nodes.get.return_value = [offline_node]
    client = _client()
    client.proxmox = instance
    pairs = client.fetch_all_nodes()
    assert len(pairs) == 1
    _, resources = pairs[0]
    assert resources.vms == []
    instance.nodes(NODE["node"]).qemu.get.assert_not_called()


@patch("custom_components.proxmoxve.api.client.ProxmoxAPI")
def test_fetch_all_nodes_auth_error(mock_api: MagicMock) -> None:
    """Auth error on nodes fetch raises ProxmoxAuthError."""
    instance = mock_api.return_value
    instance.nodes.get.side_effect = AuthenticationError("expired")
    client = _client()
    client.proxmox = instance
    with pytest.raises(ProxmoxAuthError):
        client.fetch_all_nodes()


@patch("custom_components.proxmoxve.api.client.ProxmoxAPI")
def test_start_container_calls_route(mock_api: MagicMock) -> None:
    """start_container posts to the status/start route."""
    instance = mock_api.return_value
    client = _client()
    client.proxmox = instance
    client.start_container("pve", 105)
    instance.nodes("pve").lxc(105).status.start.post.assert_called_once()


@patch("custom_components.proxmoxve.api.client.ProxmoxAPI")
def test_stop_vm_calls_route(mock_api: MagicMock) -> None:
    """stop_vm posts to the qemu status/stop route."""
    instance = mock_api.return_value
    client = _client()
    client.proxmox = instance
    client.stop_vm("pve", 100)
    instance.nodes("pve").qemu(100).status.stop.post.assert_called_once()


@patch("custom_components.proxmoxve.api.client.ProxmoxAPI")
def test_shutdown_node_calls_route(mock_api: MagicMock) -> None:
    """shutdown_node posts command=shutdown to the node status route."""
    instance = mock_api.return_value
    client = _client()
    client.proxmox = instance
    client.shutdown_node("pve")
    instance.nodes("pve").status.post.assert_called_once_with(command="shutdown")


@patch("custom_components.proxmoxve.api.client.ProxmoxAPI")
def test_create_vm_snapshot(mock_api: MagicMock) -> None:
    """create_vm_snapshot posts name to the snapshot route."""
    instance = mock_api.return_value
    client = _client()
    client.proxmox = instance
    client.create_vm_snapshot("pve", 100, "snap-1")
    instance.nodes("pve").qemu(100).snapshot.post.assert_called_once_with(name="snap-1")


@patch("custom_components.proxmoxve.api.client.ProxmoxAPI")
def test_get_nodes_auth_error(mock_api: MagicMock) -> None:
    """Auth error on get_nodes raises ProxmoxAuthError."""
    instance = mock_api.return_value
    instance.nodes.get.side_effect = AuthenticationError("expired")
    client = _client()
    client.proxmox = instance
    with pytest.raises(ProxmoxAuthError):
        client.get_nodes()


@patch("custom_components.proxmoxve.api.client.ProxmoxAPI")
def test_get_nodes_ssl_error(mock_api: MagicMock) -> None:
    """SSL error on get_nodes raises ProxmoxSSLError."""
    instance = mock_api.return_value
    instance.nodes.get.side_effect = requests.exceptions.SSLError("cert")
    client = _client()
    client.proxmox = instance
    with pytest.raises(ProxmoxSSLError):
        client.get_nodes()


@patch("custom_components.proxmoxve.api.client.ProxmoxAPI")
def test_get_nodes_timeout(mock_api: MagicMock) -> None:
    """Timeout on get_nodes raises ProxmoxTimeoutError."""
    instance = mock_api.return_value
    instance.nodes.get.side_effect = requests.exceptions.ConnectTimeout("slow")
    client = _client()
    client.proxmox = instance
    with pytest.raises(ProxmoxTimeoutError):
        client.get_nodes()


@patch("custom_components.proxmoxve.api.client.ProxmoxAPI")
def test_get_nodes_forbidden(mock_api: MagicMock) -> None:
    """4xx on get_nodes raises ProxmoxPermissionsError."""
    instance = mock_api.return_value
    instance.nodes.get.side_effect = ResourceException(403, "forbidden", "")
    client = _client()
    client.proxmox = instance
    with pytest.raises(ProxmoxPermissionsError):
        client.get_nodes()


@patch("custom_components.proxmoxve.api.client.ProxmoxAPI")
def test_get_nodes_server_error(mock_api: MagicMock) -> None:
    """5xx on get_nodes raises ProxmoxServerError."""
    instance = mock_api.return_value
    instance.nodes.get.side_effect = ResourceException(500, "boom", "")
    client = _client()
    client.proxmox = instance
    with pytest.raises(ProxmoxServerError):
        client.get_nodes()


@patch("custom_components.proxmoxve.api.client.ProxmoxAPI")
def test_get_nodes_connection_error(mock_api: MagicMock) -> None:
    """ConnectionError on get_nodes raises ProxmoxConnectionError."""
    instance = mock_api.return_value
    instance.nodes.get.side_effect = requests.exceptions.ConnectionError("down")
    client = _client()
    client.proxmox = instance
    with pytest.raises(ProxmoxConnectionError):
        client.get_nodes()


@patch("custom_components.proxmoxve.api.client.ProxmoxAPI")
def test_get_vms(mock_api: MagicMock) -> None:
    """get_vms returns the VM list."""
    instance = mock_api.return_value
    instance.nodes("pve").qemu.get.return_value = [VM]
    client = _client()
    client.proxmox = instance
    assert client.get_vms("pve") == [VM]


@patch("custom_components.proxmoxve.api.client.ProxmoxAPI")
def test_get_vms_forbidden(mock_api: MagicMock) -> None:
    """4xx on get_vms raises ProxmoxPermissionsError."""
    instance = mock_api.return_value
    instance.nodes("pve").qemu.get.side_effect = ResourceException(403, "forbidden", "")
    client = _client()
    client.proxmox = instance
    with pytest.raises(ProxmoxPermissionsError):
        client.get_vms("pve")


@patch("custom_components.proxmoxve.api.client.ProxmoxAPI")
def test_get_containers(mock_api: MagicMock) -> None:
    """get_containers returns the container list."""
    instance = mock_api.return_value
    instance.nodes("pve").lxc.get.return_value = [CONTAINER]
    client = _client()
    client.proxmox = instance
    assert client.get_containers("pve") == [CONTAINER]


@patch("custom_components.proxmoxve.api.client.ProxmoxAPI")
def test_fetch_all_nodes_server_error(mock_api: MagicMock) -> None:
    """5xx on node list fetch raises ProxmoxServerError."""
    instance = mock_api.return_value
    instance.nodes.get.side_effect = ResourceException(500, "boom", "")
    client = _client()
    client.proxmox = instance
    with pytest.raises(ProxmoxServerError):
        client.fetch_all_nodes()


@patch("custom_components.proxmoxve.api.client.ProxmoxAPI")
def test_connect_server_error_on_api_init(mock_api: MagicMock) -> None:
    """ResourceException during API init raises ProxmoxServerError."""
    mock_api.side_effect = ResourceException(500, "boom", "")
    client = _client()
    with pytest.raises(ProxmoxServerError):
        client.connect()


@patch("custom_components.proxmoxve.api.client.ProxmoxAPI")
def test_fetch_all_nodes_timeout(mock_api: MagicMock) -> None:
    """Timeout on node list fetch raises ProxmoxTimeoutError."""
    instance = mock_api.return_value
    instance.nodes.get.side_effect = requests.exceptions.ConnectTimeout("slow")
    client = _client()
    client.proxmox = instance
    with pytest.raises(ProxmoxTimeoutError):
        client.fetch_all_nodes()


@patch("custom_components.proxmoxve.api.client.ProxmoxAPI")
def test_fetch_all_nodes_ssl_error(mock_api: MagicMock) -> None:
    """SSL error on node list fetch raises ProxmoxSSLError."""
    instance = mock_api.return_value
    instance.nodes.get.side_effect = requests.exceptions.SSLError("cert")
    client = _client()
    client.proxmox = instance
    with pytest.raises(ProxmoxSSLError):
        client.fetch_all_nodes()


@patch("custom_components.proxmoxve.api.client.ProxmoxAPI")
def test_get_vms_connection_error(mock_api: MagicMock) -> None:
    """ConnectionError on get_vms raises ProxmoxConnectionError."""
    instance = mock_api.return_value
    instance.nodes("pve").qemu.get.side_effect = requests.exceptions.ConnectionError(
        "down"
    )
    client = _client()
    client.proxmox = instance
    with pytest.raises(ProxmoxConnectionError):
        client.get_vms("pve")


@patch("custom_components.proxmoxve.api.client.ProxmoxAPI")
def test_get_containers_server_error(mock_api: MagicMock) -> None:
    """5xx on get_containers raises ProxmoxServerError."""
    instance = mock_api.return_value
    instance.nodes("pve").lxc.get.side_effect = ResourceException(500, "boom", "")
    client = _client()
    client.proxmox = instance
    with pytest.raises(ProxmoxServerError):
        client.get_containers("pve")


@patch("custom_components.proxmoxve.api.client.ProxmoxAPI")
def test_reboot_node_route(mock_api: MagicMock) -> None:
    """reboot_node posts command=reboot."""
    instance = mock_api.return_value
    client = _client()
    client.proxmox = instance
    client.reboot_node("pve")
    instance.nodes("pve").status.post.assert_called_once_with(command="reboot")


@patch("custom_components.proxmoxve.api.client.ProxmoxAPI")
def test_start_all_vms_route(mock_api: MagicMock) -> None:
    """start_all_vms posts to the startall route."""
    instance = mock_api.return_value
    client = _client()
    client.proxmox = instance
    client.start_all_vms("pve")
    instance.nodes("pve").startall.post.assert_called_once()


@patch("custom_components.proxmoxve.api.client.ProxmoxAPI")
def test_remaining_vm_actions(mock_api: MagicMock) -> None:
    """The remaining VM actions hit their routes."""
    instance = mock_api.return_value
    client = _client()
    client.proxmox = instance
    client.reboot_vm("pve", 100)
    client.suspend_vm("pve", 100)
    client.resume_vm("pve", 100)
    client.reset_vm("pve", 100)
    client.shutdown_vm("pve", 100)
    instance.nodes("pve").qemu(100).status.reboot.post.assert_called_once()
    instance.nodes("pve").qemu(100).status.suspend.post.assert_called_once()
    instance.nodes("pve").qemu(100).status.resume.post.assert_called_once()
    instance.nodes("pve").qemu(100).status.reset.post.assert_called_once()
    instance.nodes("pve").qemu(100).status.shutdown.post.assert_called_once()


@patch("custom_components.proxmoxve.api.client.ProxmoxAPI")
def test_remaining_container_actions(mock_api: MagicMock) -> None:
    """The remaining container actions hit their routes."""
    instance = mock_api.return_value
    client = _client()
    client.proxmox = instance
    client.stop_container("pve", 105)
    client.reboot_container("pve", 105)
    client.create_container_snapshot("pve", 105, "snap-1")
    instance.nodes("pve").lxc(105).status.stop.post.assert_called_once()
    instance.nodes("pve").lxc(105).status.reboot.post.assert_called_once()
    instance.nodes("pve").lxc(105).snapshot.post.assert_called_once_with(name="snap-1")
