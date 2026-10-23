"""Tests for system health."""

from __future__ import annotations

from unittest.mock import MagicMock

from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component
from pytest_homeassistant_custom_component.common import get_system_health_info

from custom_components.proxmoxve.const import DOMAIN
from custom_components.proxmoxve.system_health import async_register, system_health_info

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


async def test_async_register_registers_the_info_callback(hass: HomeAssistant) -> None:
    """async_register is synchronous and registers the info callback.

    It used to be ``async``: a coroutine nobody awaited, so nothing registered.
    """
    register = MagicMock()
    result = async_register(hass, register)
    assert result is None
    register.async_register_info.assert_called_once_with(
        system_health_info, "/config/integrations"
    )


async def test_system_health_page_reports_proxmox(hass: HomeAssistant) -> None:
    """The real system_health component returns the Proxmox info without error."""
    assert await async_setup_component(hass, "system_health", {})
    assert await async_setup_component(hass, DOMAIN, {})
    await hass.async_block_till_done()
    info = await get_system_health_info(hass, DOMAIN)
    assert info == {"instances": 0}


async def test_system_health_info_unreachable(
    hass: HomeAssistant, config_entry, mock_client: MagicMock
) -> None:
    """A Proxmox API error is reported, not raised."""
    mock_client.fetch_all_nodes.return_value = [(NODE, MockNodeResources())]
    config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    mock_client.proxmox = MagicMock()
    mock_client.proxmox.version.get.side_effect = ConnectionError("down")

    info = await system_health_info(hass)
    assert info["client_version"] == "unreachable"

    await hass.config_entries.async_unload(config_entry.entry_id)
    await hass.async_block_till_done()
