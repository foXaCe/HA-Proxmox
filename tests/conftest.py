"""Shared fixtures for Proxmox VE tests."""

from __future__ import annotations

from collections.abc import Generator
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from homeassistant.const import (
    CONF_HOST,
    CONF_PASSWORD,
    CONF_PORT,
    CONF_TOKEN,
    CONF_USERNAME,
    CONF_VERIFY_SSL,
)
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.proxmoxve.const import (
    CONF_AUTH_METHOD,
    CONF_CONTAINERS,
    CONF_NODE,
    CONF_NODES,
    CONF_REALM,
    CONF_VMS,
    DEFAULT_REALM,
    DOMAIN,
)
from custom_components.proxmoxve.coordinator import ProxmoxCoordinator

pytest_plugins = "pytest_homeassistant_custom_component"

MOCK_HOST = "192.168.1.60"
MOCK_PORT = 8006
MOCK_USERNAME = "root@pam"
MOCK_PASSWORD = "mock-password"
MOCK_TOKEN_ID = "root@pam!mock"
MOCK_TOKEN_SECRET = "mock-secret"

MOCK_NODE_NAME = "pve"
MOCK_NODE_ID = "node/pve"

NODE = {
    "node": MOCK_NODE_NAME,
    "id": MOCK_NODE_ID,
    "status": "online",
    "cpu": 0.25,
    "maxcpu": 4,
    "disk": 42162511872,
    "maxdisk": 100861726720,
    "mem": 7531806720,
    "maxmem": 32535191552,
    "uptime": 1382778,
}

VM = {
    "vmid": 100,
    "name": "test-vm",
    "status": "running",
    "cpu": 0.12,
    "cpus": 2,
    "mem": 2147483648,
    "maxmem": 4294967296,
    "disk": 8589934592,
    "maxdisk": 17179869184,
    "netin": 1000000,
    "netout": 2000000,
    "uptime": 3600,
}

CONTAINER = {
    "vmid": 105,
    "name": "test-container",
    "status": "running",
    "cpu": 0.08,
    "cpus": 2,
    "mem": 1073741824,
    "maxmem": 2147483648,
    "disk": 4294967296,
    "maxdisk": 8589934592,
    "netin": 500000,
    "netout": 1000000,
    "uptime": 7200,
}

STORAGE = {
    "storage": "local",
    "type": "dir",
    "used": 1073741824,
    "total": 8589934592,
    "avail": 7516192768,
    "used_fraction": 0.125,
    "active": 1,
    "enabled": 1,
    "shared": 0,
}

BACKUP = {
    "upid": "UPID:test:0001:12345",
    "type": "vzdump",
    "status": "OK",
    "starttime": 1700000000,
    "endtime": 1700000600,
}


class MockNodeResources:
    """Mock NodeResources with list attributes."""

    def __init__(self) -> None:
        """Initialize with representative data."""
        self.vms = [VM]
        self.containers = [CONTAINER]
        self.storages = [STORAGE]
        self.backups = [BACKUP]


def _config_entry_data(**overrides: Any) -> dict[str, Any]:
    """Build config entry data with overrides."""
    data: dict[str, Any] = {
        CONF_AUTH_METHOD: DEFAULT_REALM,
        CONF_HOST: MOCK_HOST,
        CONF_PORT: MOCK_PORT,
        CONF_USERNAME: MOCK_USERNAME,
        CONF_REALM: DEFAULT_REALM,
        CONF_TOKEN: False,
        CONF_PASSWORD: MOCK_PASSWORD,
        CONF_VERIFY_SSL: False,
        CONF_NODES: [
            {
                CONF_NODE: MOCK_NODE_NAME,
                CONF_VMS: [VM["vmid"]],
                CONF_CONTAINERS: [CONTAINER["vmid"]],
            }
        ],
    }
    data.update(overrides)
    return data


@pytest.fixture(autouse=True, name="_enable_custom_integrations")
def enable_custom_integrations_autouse(enable_custom_integrations: None) -> None:
    """Ensure custom integrations are discoverable in every test."""


@pytest.fixture(name="config_entry_data")
def config_entry_data_fixture() -> dict[str, Any]:
    """Return config entry data using password auth."""
    return _config_entry_data()


@pytest.fixture(name="config_entry_data_token")
def config_entry_data_token_fixture() -> dict[str, Any]:
    """Return config entry data using API token auth."""
    return _config_entry_data(
        CONF_TOKEN=True,
        CONF_PASSWORD=None,
        CONF_TOKEN_ID=MOCK_TOKEN_ID,
        CONF_TOKEN_SECRET=MOCK_TOKEN_SECRET,
    )


@pytest.fixture(name="mock_client")
def mock_client_fixture() -> Generator[MagicMock]:
    """Mock the ProxmoxClient at its use site in the coordinator."""
    with patch(
        "custom_components.proxmoxve.coordinator.ProxmoxClient",
        autospec=True,
    ) as mock_cls:
        client = mock_cls.return_value
        client.permissions = {
            "/nodes/pve": {"Sys.Audit": 1, "Sys.PowerMgmt": 1},
            "/vms/100": {"VM.Audit": 1, "VM.PowerMgmt": 1},
            "/vms/105": {"VM.Audit": 1, "VM.PowerMgmt": 1, "VM.Snapshot": 1},
            "/": {"VM.PowerMgmt": 1, "VM.Audit": 1, "Sys.Audit": 1},
        }
        client.host = MOCK_HOST
        client.fetch_all_nodes.return_value = [(NODE, MockNodeResources())]
        yield client


@pytest.fixture(name="config_entry")
def config_entry_fixture(config_entry_data: dict[str, Any]) -> MockConfigEntry:
    """Create a mock config entry."""
    return MockConfigEntry(
        domain=DOMAIN,
        title=MOCK_HOST,
        data=config_entry_data,
        entry_id="mock_entry_id",
        unique_id=f"mock_{MOCK_HOST}",
        version=3,
    )


@pytest.fixture(name="setup_integration")
async def setup_integration_fixture(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    mock_client: MagicMock,
    enable_custom_integrations: None,
) -> Generator[ProxmoxCoordinator]:
    """Set up the integration with mocked client."""
    mock_client.fetch_all_nodes.return_value = [(NODE, MockNodeResources())]

    config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    coordinator: ProxmoxCoordinator = config_entry.runtime_data
    yield coordinator

    await hass.config_entries.async_unload(config_entry.entry_id)
    await hass.async_block_till_done()
