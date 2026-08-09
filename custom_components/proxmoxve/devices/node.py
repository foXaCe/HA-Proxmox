"""Node entities for Proxmox VE."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from typing import override

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.components.button import (
    ButtonDeviceClass,
    ButtonEntity,
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

from ..api.models import ProxmoxNodeData
from ..const import (
    NODE_ONLINE,
    STATUS_OK,
    ProxmoxPermission,
)
from ..coordinator import ProxmoxCoordinator
from ..entity import ProxmoxNodeEntity


@dataclass(frozen=True, kw_only=True)
class ProxmoxNodeSensorEntityDescription(SensorEntityDescription):
    """Class to hold Proxmox node sensor description."""

    value_fn: Callable[[ProxmoxNodeData], StateType | datetime]
    permission: ProxmoxPermission = ProxmoxPermission.SYSAUDIT
    permission_target: str = "nodes"


@dataclass(frozen=True, kw_only=True)
class ProxmoxNodeBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Class to hold Proxmox node binary sensor description."""

    state_fn: Callable[[ProxmoxNodeData], bool | None]
    permission: ProxmoxPermission = ProxmoxPermission.SYSAUDIT
    permission_target: str = "nodes"


@dataclass(frozen=True, kw_only=True)
class ProxmoxNodeButtonEntityDescription(ButtonEntityDescription):
    """Class to hold Proxmox node button description."""

    press_action: Callable[[ProxmoxCoordinator, str], None]
    permission: ProxmoxPermission = ProxmoxPermission.SYSPOWER
    permission_target: str = "nodes"


NODE_SENSORS: tuple[ProxmoxNodeSensorEntityDescription, ...] = (
    ProxmoxNodeSensorEntityDescription(
        key="node_cpu",
        translation_key="node_cpu",
        value_fn=lambda data: data.node["cpu"] * 100,
        native_unit_of_measurement=PERCENTAGE,
        entity_category=EntityCategory.DIAGNOSTIC,
        suggested_display_precision=2,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    ProxmoxNodeSensorEntityDescription(
        key="node_max_cpu",
        translation_key="node_max_cpu",
        value_fn=lambda data: data.node["maxcpu"],
        entity_category=EntityCategory.DIAGNOSTIC,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    ),
    ProxmoxNodeSensorEntityDescription(
        key="node_disk",
        translation_key="node_disk",
        value_fn=lambda data: data.node["disk"],
        device_class=SensorDeviceClass.DATA_SIZE,
        native_unit_of_measurement=UnitOfInformation.BYTES,
        suggested_unit_of_measurement=UnitOfInformation.GIBIBYTES,
        suggested_display_precision=1,
        entity_category=EntityCategory.DIAGNOSTIC,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    ),
    ProxmoxNodeSensorEntityDescription(
        key="node_max_disk",
        translation_key="node_max_disk",
        value_fn=lambda data: data.node["maxdisk"],
        device_class=SensorDeviceClass.DATA_SIZE,
        native_unit_of_measurement=UnitOfInformation.BYTES,
        suggested_unit_of_measurement=UnitOfInformation.GIBIBYTES,
        suggested_display_precision=1,
        entity_category=EntityCategory.DIAGNOSTIC,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    ),
    ProxmoxNodeSensorEntityDescription(
        key="node_memory",
        translation_key="node_memory",
        value_fn=lambda data: data.node["mem"],
        device_class=SensorDeviceClass.DATA_SIZE,
        native_unit_of_measurement=UnitOfInformation.BYTES,
        suggested_unit_of_measurement=UnitOfInformation.GIBIBYTES,
        suggested_display_precision=1,
        entity_category=EntityCategory.DIAGNOSTIC,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    ),
    ProxmoxNodeSensorEntityDescription(
        key="node_max_memory",
        translation_key="node_max_memory",
        value_fn=lambda data: data.node["maxmem"],
        device_class=SensorDeviceClass.DATA_SIZE,
        native_unit_of_measurement=UnitOfInformation.BYTES,
        suggested_unit_of_measurement=UnitOfInformation.GIBIBYTES,
        suggested_display_precision=1,
        entity_category=EntityCategory.DIAGNOSTIC,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    ProxmoxNodeSensorEntityDescription(
        key="node_memory_percentage",
        translation_key="node_memory_percentage",
        value_fn=lambda data: int(data.node["mem"]) / int(data.node["maxmem"]) * 100,
        native_unit_of_measurement=PERCENTAGE,
        entity_category=EntityCategory.DIAGNOSTIC,
        suggested_display_precision=2,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    ProxmoxNodeSensorEntityDescription(
        key="node_uptime",
        translation_key="node_uptime",
        value_fn=lambda data: data.node["uptime"],
        device_class=SensorDeviceClass.DURATION,
        native_unit_of_measurement=UnitOfTime.SECONDS,
        suggested_unit_of_measurement=UnitOfTime.HOURS,
        entity_category=EntityCategory.DIAGNOSTIC,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    ProxmoxNodeSensorEntityDescription(
        key="node_status",
        translation_key="node_status",
        value_fn=lambda data: data.node["status"],
        device_class=SensorDeviceClass.ENUM,
        options=["online", "offline"],
        permission=ProxmoxPermission.VMAUDIT,
        permission_target="vms",
    ),
    ProxmoxNodeSensorEntityDescription(
        key="node_backup_last_backup",
        translation_key="node_backup_last_backup",
        value_fn=lambda data: (
            dt_util.utc_from_timestamp(data.backups[0]["endtime"])
            if data.backups
            else None
        ),
        device_class=SensorDeviceClass.TIMESTAMP,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
    ),
    ProxmoxNodeSensorEntityDescription(
        key="node_backup_duration",
        translation_key="node_backup_duration",
        value_fn=lambda data: (
            data.backups[0]["endtime"] - data.backups[0]["starttime"]
            if data.backups
            else None
        ),
        device_class=SensorDeviceClass.DURATION,
        native_unit_of_measurement=UnitOfTime.SECONDS,
        suggested_unit_of_measurement=UnitOfTime.MINUTES,
        entity_category=EntityCategory.DIAGNOSTIC,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    ),
)

NODE_BINARY_SENSORS: tuple[ProxmoxNodeBinarySensorEntityDescription, ...] = (
    ProxmoxNodeBinarySensorEntityDescription(
        key="status",
        translation_key="status",
        state_fn=lambda data: data.node["status"] == NODE_ONLINE,
        device_class=BinarySensorDeviceClass.RUNNING,
        entity_category=EntityCategory.DIAGNOSTIC,
        # PVEVMUsers are allowed this node, through "/vms"
        permission=ProxmoxPermission.VMAUDIT,
        permission_target="vms",
    ),
    ProxmoxNodeBinarySensorEntityDescription(
        key="node_backup_status",
        translation_key="node_backup_status",
        state_fn=lambda data: bool(
            data.backups and data.backups[0]["status"] != STATUS_OK
        ),
        device_class=BinarySensorDeviceClass.PROBLEM,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
    ),
)

NODE_BUTTONS: tuple[ProxmoxNodeButtonEntityDescription, ...] = (
    ProxmoxNodeButtonEntityDescription(
        key="reboot",
        press_action=lambda coordinator, node: coordinator.client.reboot_node(node),
        entity_category=EntityCategory.CONFIG,
        device_class=ButtonDeviceClass.RESTART,
    ),
    ProxmoxNodeButtonEntityDescription(
        key="shutdown",
        translation_key="shutdown",
        press_action=lambda coordinator, node: coordinator.client.shutdown_node(node),
        entity_category=EntityCategory.CONFIG,
    ),
    ProxmoxNodeButtonEntityDescription(
        key="start_all",
        translation_key="start_all",
        permission=ProxmoxPermission.POWER,
        permission_target="vms",
        press_action=lambda coordinator, node: coordinator.client.start_all_vms(node),
        entity_category=EntityCategory.CONFIG,
    ),
    ProxmoxNodeButtonEntityDescription(
        key="stop_all",
        translation_key="stop_all",
        permission=ProxmoxPermission.POWER,
        permission_target="vms",
        press_action=lambda coordinator, node: coordinator.client.stop_all_vms(node),
        entity_category=EntityCategory.CONFIG,
    ),
    ProxmoxNodeButtonEntityDescription(
        key="suspend_all",
        translation_key="suspend_all",
        permission=ProxmoxPermission.POWER,
        permission_target="vms",
        press_action=lambda coordinator, node: coordinator.client.suspend_all_vms(node),
        entity_category=EntityCategory.CONFIG,
    ),
)


class ProxmoxNodeSensor(ProxmoxNodeEntity, SensorEntity):
    """Representation of a Proxmox VE node sensor."""

    entity_description: ProxmoxNodeSensorEntityDescription

    @property
    @override
    def native_value(self) -> StateType | datetime:
        """Return the native value of the sensor."""
        return self.entity_description.value_fn(self.coordinator.data[self.device_name])


class ProxmoxNodeBinarySensor(ProxmoxNodeEntity, BinarySensorEntity):
    """A binary sensor for reading Proxmox VE node data."""

    entity_description: ProxmoxNodeBinarySensorEntityDescription

    @property
    @override
    def is_on(self) -> bool | None:
        """Return true if the binary sensor is on."""
        return self.entity_description.state_fn(self.coordinator.data[self.device_name])


class ProxmoxNodeButtonEntity(ProxmoxNodeEntity, ButtonEntity):
    """Represents a Proxmox Node button entity."""

    entity_description: ProxmoxNodeButtonEntityDescription

    @override
    async def async_press(self) -> None:
        """Execute the node button action via executor."""
        await self.hass.async_add_executor_job(
            self.entity_description.press_action,
            self.coordinator,
            self._node_data.node["node"],
        )
