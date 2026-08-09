"""Tests for system health."""

from __future__ import annotations

from unittest.mock import MagicMock

from homeassistant.core import HomeAssistant

from custom_components.proxmoxve.system_health import system_health_info

from .conftest import NODE, MockNodeResources


async def test_system_health_info_with_entry(
    hass: HomeAssistant, config_entry, mock_client: MagicMock
) -> None:
    """system_health_info returns instance and version info."""
    mock_client.fetch_all_nodes.return_value = [(NODE, MockNodeResources())]
    config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    mock_client.proxmox = MagicMock()
    mock_client.proxmox.version.get.return_value = {"version": "9.2"}

    info = await system_health_info(hass)
    assert info["instances"] == 1
    assert info["client_version"] == "9.2"

    await hass.config_entries.async_unload(config_entry.entry_id)
    await hass.async_block_till_done()


async def test_system_health_info_without_entry(hass: HomeAssistant) -> None:
    """system_health_info with no entries reports zero instances."""
    info = await system_health_info(hass)
    assert info["instances"] == 0
    assert "client_version" not in info
