"""Container (LXC) entities for Proxmox VE."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, override

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.components.button import (
    ButtonDeviceClass,
    ButtonEntityDescription,
)
from homeassistant.components.sensor import (
    EntityCategory,
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
    StateType,
)
from homeassistant.const import PERCENTAGE, UnitOfInformation, UnitOfTime
from homeassistant.util import dt as dt_util

from ..const import VM_CONTAINER_RUNNING, ProxmoxPermission
from ..coordinator import ProxmoxCoordinator
from ..entity import (
    ProxmoxBaseButton,
    ProxmoxContainerEntity,
)


@dataclass(frozen=True, kw_only=True)
class ProxmoxContainerSensorEntityDescription(SensorEntityDescription):
    """Class to hold Proxmox container sensor description."""

    value_fn: Callable[[dict[str, Any]], StateType]


@dataclass(frozen=True, kw_only=True)
class ProxmoxContainerBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Class to hold Proxmox container binary sensor description."""

    state_fn: Callable[[dict[str, Any]], bool | None]


@dataclass(frozen=True, kw_only=True)
class ProxmoxContainerButtonEntityDescription(ButtonEntityDescription):
    """Class to hold Proxmox container button description."""

    press_action: Callable[[ProxmoxCoordinator, str, int], None]
    permission: ProxmoxPermission = ProxmoxPermission.POWER
    permission_target: str = "vms"


CONTAINER_SENSORS: tuple[ProxmoxContainerSensorEntityDescription, ...] = (
    ProxmoxContainerSensorEntityDescription(
        key="container_max_cpu",
        translation_key="container_max_cpu",
        value_fn=lambda data: data["cpus"],
        entity_category=EntityCategory.DIAGNOSTIC,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    ),
    ProxmoxContainerSensorEntityDescription(
        key="container_cpu",
        translation_key="container_cpu",
        value_fn=lambda data: data["cpu"] * 100,
        native_unit_of_measurement=PERCENTAGE,
        entity_category=EntityCategory.DIAGNOSTIC,
        suggested_display_precision=2,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    ProxmoxContainerSensorEntityDescription(
        key="container_memory",
        translation_key="container_memory",
        value_fn=lambda data: data["mem"],
        device_class=SensorDeviceClass.DATA_SIZE,
        native_unit_of_measurement=UnitOfInformation.BYTES,
        suggested_unit_of_measurement=UnitOfInformation.GIBIBYTES,
        suggested_display_precision=1,
        entity_category=EntityCategory.DIAGNOSTIC,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    ),
    ProxmoxContainerSensorEntityDescription(
        key="container_max_memory",
        translation_key="container_max_memory",
        value_fn=lambda data: data["maxmem"],
        device_class=SensorDeviceClass.DATA_SIZE,
        native_unit_of_measurement=UnitOfInformation.BYTES,
        suggested_unit_of_measurement=UnitOfInformation.GIBIBYTES,
        suggested_display_precision=1,
        entity_category=EntityCategory.DIAGNOSTIC,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    ProxmoxContainerSensorEntityDescription(
        key="container_memory_percentage",
        translation_key="container_memory_percentage",
        value_fn=lambda data: int(data["mem"]) / int(data["maxmem"]) * 100,
        native_unit_of_measurement=PERCENTAGE,
        entity_category=EntityCategory.DIAGNOSTIC,
        suggested_display_precision=2,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    ProxmoxContainerSensorEntityDescription(
        key="container_uptime",
        translation_key="container_uptime",
        value_fn=lambda data: data.get("uptime"),
        device_class=SensorDeviceClass.DURATION,
        native_unit_of_measurement=UnitOfTime.SECONDS,
        suggested_unit_of_measurement=UnitOfTime.HOURS,
        entity_category=EntityCategory.DIAGNOSTIC,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    ProxmoxContainerSensorEntityDescription(
        key="container_disk",
        translation_key="container_disk",
        value_fn=lambda data: data["disk"],
        device_class=SensorDeviceClass.DATA_SIZE,
        native_unit_of_measurement=UnitOfInformation.BYTES,
        suggested_unit_of_measurement=UnitOfInformation.GIBIBYTES,
        suggested_display_precision=1,
        entity_category=EntityCategory.DIAGNOSTIC,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    ),
    ProxmoxContainerSensorEntityDescription(
        key="container_max_disk",
        translation_key="container_max_disk",
        value_fn=lambda data: data["maxdisk"],
        device_class=SensorDeviceClass.DATA_SIZE,
        native_unit_of_measurement=UnitOfInformation.BYTES,
        suggested_unit_of_measurement=UnitOfInformation.GIBIBYTES,
        suggested_display_precision=1,
        entity_category=EntityCategory.DIAGNOSTIC,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    ),
    ProxmoxContainerSensorEntityDescription(
        key="container_status",
        translation_key="container_status",
        value_fn=lambda data: data["status"],
        device_class=SensorDeviceClass.ENUM,
        options=["running", "stopped", "suspended"],
    ),
    ProxmoxContainerSensorEntityDescription(
        key="container_netin",
        translation_key="container_netin",
        value_fn=lambda data: data["netin"],
        device_class=SensorDeviceClass.DATA_SIZE,
        native_unit_of_measurement=UnitOfInformation.BYTES,
        suggested_unit_of_measurement=UnitOfInformation.GIBIBYTES,
        suggested_display_precision=1,
        entity_category=EntityCategory.DIAGNOSTIC,
        state_class=SensorStateClass.TOTAL_INCREASING,
        entity_registry_enabled_default=False,
    ),
    ProxmoxContainerSensorEntityDescription(
        key="container_netout",
        translation_key="container_netout",
        value_fn=lambda data: data["netout"],
        device_class=SensorDeviceClass.DATA_SIZE,
        native_unit_of_measurement=UnitOfInformation.BYTES,
        suggested_unit_of_measurement=UnitOfInformation.GIBIBYTES,
        suggested_display_precision=1,
        entity_category=EntityCategory.DIAGNOSTIC,
        state_class=SensorStateClass.TOTAL_INCREASING,
        entity_registry_enabled_default=False,
    ),
)

CONTAINER_BINARY_SENSORS: tuple[ProxmoxContainerBinarySensorEntityDescription, ...] = (
    ProxmoxContainerBinarySensorEntityDescription(
        key="status",
        translation_key="status",
        state_fn=lambda data: data["status"] == VM_CONTAINER_RUNNING,
        device_class=BinarySensorDeviceClass.RUNNING,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
)

CONTAINER_BUTTONS: tuple[ProxmoxContainerButtonEntityDescription, ...] = (
    ProxmoxContainerButtonEntityDescription(
        key="start",
        translation_key="start",
        press_action=lambda coordinator, node, vmid: coordinator.client.start_container(
            node, vmid
        ),
        entity_category=EntityCategory.CONFIG,
    ),
    ProxmoxContainerButtonEntityDescription(
        key="stop",
        translation_key="stop",
        press_action=lambda coordinator, node, vmid: coordinator.client.stop_container(
            node, vmid
        ),
        entity_category=EntityCategory.CONFIG,
    ),
    ProxmoxContainerButtonEntityDescription(
        key="restart",
        press_action=lambda coordinator, node, vmid: (
            coordinator.client.reboot_container(node, vmid)
        ),
        entity_category=EntityCategory.CONFIG,
        device_class=ButtonDeviceClass.RESTART,
    ),
    ProxmoxContainerButtonEntityDescription(
        key="snapshot_create",
        translation_key="snapshot_create",
        press_action=lambda coordinator, node, vmid: (
            coordinator.client.create_container_snapshot(
                node,
                vmid,
                name=(
                    "homeassistant_snapshot_"
                    f"{coordinator.data[node].containers[vmid]['name']}_"
                    f"{dt_util.utcnow().strftime('%Y%m%d%H%M%S')}"
                ),
            )
        ),
        permission=ProxmoxPermission.SNAPSHOT,
        entity_category=EntityCategory.CONFIG,
    ),
)


class ProxmoxContainerSensor(ProxmoxContainerEntity, SensorEntity):
    """Represents a Proxmox VE container sensor."""

    entity_description: ProxmoxContainerSensorEntityDescription

    @property
    @override
    def native_value(self) -> StateType:
        """Return the native value of the sensor."""
        return self.entity_description.value_fn(self.container_data)


class ProxmoxContainerBinarySensor(ProxmoxContainerEntity, BinarySensorEntity):
    """Representation of a Proxmox Container binary sensor."""

    entity_description: ProxmoxContainerBinarySensorEntityDescription

    @property
    @override
    def is_on(self) -> bool | None:
        """Return true if the binary sensor is on."""
        return self.entity_description.state_fn(self.container_data)


class ProxmoxContainerButtonEntity(ProxmoxContainerEntity, ProxmoxBaseButton):
    """Represents a Proxmox Container button entity."""

    entity_description: ProxmoxContainerButtonEntityDescription

    @override
    async def _async_press_call(self) -> None:
        """Execute the container button action via executor."""
        await self.hass.async_add_executor_job(
            self.entity_description.press_action,
            self.coordinator,
            self._node_name,
            self.container_data["vmid"],
        )
