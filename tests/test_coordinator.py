"""Tests for the Proxmox coordinator."""

from __future__ import annotations

from homeassistant.core import HomeAssistant

from custom_components.proxmoxve.api.exceptions import (
    ProxmoxAuthError,
    ProxmoxConnectionError,
    ProxmoxServerError,
)

from .conftest import MOCK_NODE_NAME, NODE, MockNodeResources


async def test_coordinator_populates_data(
    hass: HomeAssistant,
    config_entry,
    mock_client,
) -> None:
    """The coordinator fetches data during setup."""
    mock_client.fetch_all_nodes.return_value = [(NODE, MockNodeResources())]
    config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    coordinator = config_entry.runtime_data
    assert coordinator.last_update_success is True
    assert MOCK_NODE_NAME in coordinator.data
    node_data = coordinator.data[MOCK_NODE_NAME]
    assert node_data.node["node"] == MOCK_NODE_NAME
    assert 100 in node_data.vms
    assert 105 in node_data.containers
    assert "local" in node_data.storages
    assert len(node_data.backups) == 1

    await hass.config_entries.async_unload(config_entry.entry_id)
    await hass.async_block_till_done()


async def test_coordinator_auth_failed(
    hass: HomeAssistant,
    config_entry,
    mock_client,
) -> None:
    """Authentication failure during setup aborts the setup."""
    mock_client.connect.side_effect = ProxmoxAuthError
    config_entry.add_to_hass(hass)
    assert not await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()
    assert config_entry.state is not None


async def test_coordinator_refresh_failure_and_recovery(
    hass: HomeAssistant,
    config_entry,
    mock_client,
) -> None:
    """A failed refresh marks unavailable, then recovers."""
    mock_client.fetch_all_nodes.return_value = [(NODE, MockNodeResources())]
    config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    coordinator = config_entry.runtime_data
    assert coordinator.last_update_success is True

    mock_client.fetch_all_nodes.side_effect = ProxmoxConnectionError
    await coordinator.async_refresh()
    assert coordinator.last_update_success is False

    mock_client.fetch_all_nodes.side_effect = None
    mock_client.fetch_all_nodes.return_value = [(NODE, MockNodeResources())]
    await coordinator.async_refresh()
    assert coordinator.last_update_success is True

    await hass.config_entries.async_unload(config_entry.entry_id)
    await hass.async_block_till_done()


async def test_coordinator_update_failed(
    hass: HomeAssistant,
    config_entry,
    mock_client,
) -> None:
    """A server error marks the coordinator unavailable."""
    mock_client.fetch_all_nodes.return_value = [(NODE, MockNodeResources())]
    config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    coordinator = config_entry.runtime_data
    mock_client.fetch_all_nodes.side_effect = ProxmoxServerError
    await coordinator.async_refresh()
    assert coordinator.last_update_success is False

    await hass.config_entries.async_unload(config_entry.entry_id)
    await hass.async_block_till_done()


async def test_coordinator_setup_error_branches(
    hass: HomeAssistant, config_entry, mock_client
) -> None:
    """Each setup error type maps to the right exception."""
    from homeassistant.exceptions import ConfigEntryAuthFailed, ConfigEntryError
    from homeassistant.helpers.update_coordinator import UpdateFailed

    from custom_components.proxmoxve.api.exceptions import (
        ProxmoxConnectionError,
        ProxmoxNodesNotFoundError,
        ProxmoxPermissionsError,
        ProxmoxServerError,
        ProxmoxSSLError,
        ProxmoxTimeoutError,
    )

    cases = [
        (ProxmoxAuthError, ConfigEntryAuthFailed),
        (ProxmoxSSLError, ConfigEntryError),
        (ProxmoxTimeoutError, UpdateFailed),
        (ProxmoxServerError, UpdateFailed),
        (ProxmoxPermissionsError, ConfigEntryAuthFailed),
        (ProxmoxNodesNotFoundError, ConfigEntryError),
        (ProxmoxConnectionError, ConfigEntryError),
    ]

    for setup_exc, _ in cases:
        entry = config_entry.__class__(
            domain=config_entry.domain,
            title=config_entry.title,
            data=dict(config_entry.data),
            entry_id=f"err_{setup_exc.__name__}",
            version=3,
        )
        entry.add_to_hass(hass)
        mock_client.connect.side_effect = setup_exc
        result = await hass.config_entries.async_setup(entry.entry_id)
        assert not result
        await hass.config_entries.async_remove(entry.entry_id)
        await hass.async_block_till_done()
        mock_client.connect.side_effect = None


async def test_coordinator_update_error_branches(
    hass: HomeAssistant, config_entry, mock_client
) -> None:
    """Update error types all mark the coordinator unavailable."""
    from custom_components.proxmoxve.api.exceptions import (
        ProxmoxSSLError,
        ProxmoxTimeoutError,
    )

    mock_client.fetch_all_nodes.return_value = [(NODE, MockNodeResources())]
    config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    coordinator = config_entry.runtime_data

    for exc in (ProxmoxSSLError, ProxmoxTimeoutError, ProxmoxServerError):
        mock_client.fetch_all_nodes.side_effect = exc
        await coordinator.async_refresh()
        assert coordinator.last_update_success is False

    await hass.config_entries.async_unload(config_entry.entry_id)
    await hass.async_block_till_done()
