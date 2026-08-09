"""Tests for the binary_sensor platform."""

from __future__ import annotations

from homeassistant.core import HomeAssistant


async def test_node_running_binary_sensor(
    hass: HomeAssistant, setup_integration
) -> None:
    """The node status binary sensor reflects the online state."""
    state = hass.states.get("binary_sensor.pve_status")
    assert state is not None
    assert state.state == "on"


async def test_vm_status_binary_sensor(hass: HomeAssistant, setup_integration) -> None:
    """The VM status binary sensor is on when running."""
    state = hass.states.get("binary_sensor.test_vm_status")
    assert state is not None
    assert state.state == "on"


async def test_container_status_binary_sensor(
    hass: HomeAssistant, setup_integration
) -> None:
    """The container status binary sensor is on when running."""
    state = hass.states.get("binary_sensor.test_container_status")
    assert state is not None
    assert state.state == "on"


async def test_storage_active_binary_sensor(
    hass: HomeAssistant, setup_integration
) -> None:
    """The storage active binary sensor is on."""
    state = hass.states.get("binary_sensor.storage_local_storage_active")
    assert state is not None
    assert state.state == "on"
