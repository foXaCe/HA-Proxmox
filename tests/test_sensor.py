"""Tests for the sensor platform."""

from __future__ import annotations

import pytest
from homeassistant.const import PERCENTAGE
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

from custom_components.proxmoxve.coordinator import ProxmoxCoordinator

from .conftest import (
    STORAGE,
)


async def test_node_sensor_created(hass: HomeAssistant, setup_integration) -> None:
    """Node sensors are created with the right unique_id."""
    registry = er.async_get(hass)
    entry = registry.async_get("sensor.pve_cpu_usage")
    assert entry is not None
    assert "node/pve_node_cpu" in entry.unique_id


async def test_node_sensor_value(hass: HomeAssistant, setup_integration) -> None:
    """Node CPU sensor reflects coordinator data."""
    state = hass.states.get("sensor.pve_cpu_usage")
    assert state is not None
    assert state.state == "25.0"
    assert state.attributes["unit_of_measurement"] == PERCENTAGE


async def test_vm_sensor_created(hass: HomeAssistant, setup_integration) -> None:
    """VM sensors are created."""
    registry = er.async_get(hass)
    entry = registry.async_get("sensor.test_vm_status")
    assert entry is not None


async def test_vm_sensor_values(hass: HomeAssistant, setup_integration) -> None:
    """VM CPU and memory sensors reflect coordinator data."""
    cpu = hass.states.get("sensor.test_vm_cpu_usage")
    assert cpu is not None
    assert cpu.state == "12.0"

    # The memory sensor is disabled by default; it exists in the registry.
    registry = er.async_get(hass)
    mem_entry = registry.async_get("sensor.test_vm_memory_usage")
    assert mem_entry is not None
    assert mem_entry.disabled_by is not None


async def test_container_sensor_created(hass: HomeAssistant, setup_integration) -> None:
    """Container sensors are created."""
    state = hass.states.get("sensor.test_container_status")
    assert state is not None
    assert state.state == "running"


async def test_storage_sensor_created(hass: HomeAssistant, setup_integration) -> None:
    """Storage sensors are created."""
    state = hass.states.get("sensor.storage_local_used_storage")
    assert state is not None
    # native bytes exposed by the entity; HA normalizes to GiB in the state
    assert float(state.state) == pytest.approx(STORAGE["used"] / (1024**3))


async def test_storage_used_percentage(hass: HomeAssistant, setup_integration) -> None:
    """Storage used percentage is derived from used_fraction."""
    state = hass.states.get("sensor.storage_local_storage_usage_percentage")
    assert state is not None
    assert state.state == "12.5"


async def test_entities_unavailable_when_coordinator_fails(
    hass: HomeAssistant,
    setup_integration: ProxmoxCoordinator,
    mock_client,
) -> None:
    """Entities become unavailable when the coordinator fails."""
    mock_client.fetch_all_nodes.side_effect = Exception("down")
    await setup_integration.async_refresh()
    await hass.async_block_till_done()

    state = hass.states.get("sensor.pve_cpu_usage")
    assert state is not None
    assert state.state == "unavailable"
