"""Tests for the Proxmox integration setup."""

from __future__ import annotations

from unittest.mock import MagicMock

from homeassistant.core import HomeAssistant

from custom_components.proxmoxve.const import (
    DOMAIN,
)

from .conftest import (
    MOCK_HOST,
    MOCK_NODE_NAME,
    NODE,
    MockNodeResources,
)


async def test_setup_and_unload(
    hass: HomeAssistant, config_entry, mock_client: MagicMock
) -> None:
    """The integration sets up and unloads cleanly."""
    mock_client.fetch_all_nodes.return_value = [(NODE, MockNodeResources())]
    config_entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    coordinator = config_entry.runtime_data
    assert coordinator.data[MOCK_NODE_NAME].node["node"] == MOCK_NODE_NAME

    assert await hass.config_entries.async_unload(config_entry.entry_id)
    await hass.async_block_till_done()
    assert config_entry.state.value == "not_loaded"


async def test_setup_with_token_auth(
    hass: HomeAssistant,
    config_entry_data_token,
    mock_client: MagicMock,
) -> None:
    """Setup works with API token auth."""
    from pytest_homeassistant_custom_component.common import MockConfigEntry

    entry = MockConfigEntry(
        domain=DOMAIN,
        title=MOCK_HOST,
        data=config_entry_data_token,
        entry_id="token_entry_id",
        unique_id=f"mock_{MOCK_HOST}",
        version=3,
    )
    mock_client.fetch_all_nodes.return_value = [(NODE, MockNodeResources())]
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    assert entry.runtime_data is not None

    await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()


async def test_setup_auth_failed_aborts(
    hass: HomeAssistant, config_entry, mock_client: MagicMock
) -> None:
    """Authentication failure during setup aborts the entry."""
    mock_client.connect.side_effect = Exception("auth")
    config_entry.add_to_hass(hass)

    assert not await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()
    assert config_entry.state.value in ("setup_error", "setup_retry", "not_loaded")
