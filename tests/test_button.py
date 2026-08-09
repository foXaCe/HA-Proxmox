"""Tests for the button platform."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from homeassistant.components.button import DOMAIN as BUTTON_DOMAIN
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

from custom_components.proxmoxve.coordinator import ProxmoxCoordinator

from .conftest import CONTAINER, MOCK_NODE_NAME, VM


async def test_node_buttons_created(hass: HomeAssistant, setup_integration) -> None:
    """Node buttons are created."""
    registry = er.async_get(hass)
    assert registry.async_get("button.pve_restart") is not None
    assert registry.async_get("button.pve_shut_down") is not None
    assert registry.async_get("button.pve_start_all") is not None


async def test_vm_buttons_created(hass: HomeAssistant, setup_integration) -> None:
    """VM buttons are created."""
    registry = er.async_get(hass)
    assert registry.async_get("button.test_vm_start") is not None
    assert registry.async_get("button.test_vm_stop") is not None


async def test_container_buttons_created(
    hass: HomeAssistant, setup_integration
) -> None:
    """Container buttons are created."""
    registry = er.async_get(hass)
    assert registry.async_get("button.test_container_start") is not None
    assert registry.async_get("button.test_container_restart") is not None


async def test_container_start_button_press(
    hass: HomeAssistant,
    setup_integration: ProxmoxCoordinator,
    mock_client: MagicMock,
) -> None:
    """Pressing the container start button calls the client."""
    mock_client.start_container = MagicMock()
    state = hass.states.get("button.test_container_start")
    assert state is not None

    await hass.services.async_call(
        BUTTON_DOMAIN,
        "press",
        {"entity_id": "button.test_container_start"},
        blocking=True,
    )
    await hass.async_block_till_done()

    mock_client.start_container.assert_called_once_with(
        MOCK_NODE_NAME, CONTAINER["vmid"]
    )


async def test_vm_start_button_press(
    hass: HomeAssistant,
    setup_integration: ProxmoxCoordinator,
    mock_client: MagicMock,
) -> None:
    """Pressing the VM start button calls the client."""
    mock_client.start_vm = MagicMock()
    await hass.services.async_call(
        BUTTON_DOMAIN,
        "press",
        {"entity_id": "button.test_vm_start"},
        blocking=True,
    )
    await hass.async_block_till_done()

    mock_client.start_vm.assert_called_once_with(MOCK_NODE_NAME, VM["vmid"])


async def test_container_start_button_press_connection_error(
    hass: HomeAssistant,
    setup_integration: ProxmoxCoordinator,
    mock_client: MagicMock,
) -> None:
    """A connection error during press raises a translated HomeAssistantError."""
    from homeassistant.exceptions import HomeAssistantError

    from custom_components.proxmoxve.api.exceptions import ProxmoxConnectionError

    mock_client.start_container.side_effect = ProxmoxConnectionError

    with pytest.raises(HomeAssistantError):
        await hass.services.async_call(
            BUTTON_DOMAIN,
            "press",
            {"entity_id": "button.test_container_start"},
            blocking=True,
        )
    await hass.async_block_till_done()
