"""VM (QEMU) entities for Proxmox VE."""

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
    ProxmoxVMEntity,
)


@dataclass(frozen=True, kw_only=True)
class ProxmoxVMSensorEntityDescription(SensorEntityDescription):
    """Class to hold Proxmox VM sensor description."""

    value_fn: Callable[[dict[str, Any]], StateType]


@dataclass(frozen=True, kw_only=True)
class ProxmoxVMBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Class to hold Proxmox endpoint binary sensor description."""

    state_fn: Callable[[dict[str, Any]], bool | None]


@dataclass(frozen=True, kw_only=True)
class ProxmoxVMButtonEntityDescription(ButtonEntityDescription):
    """Class to hold Proxmox VM button description."""

    press_action: Callable[[ProxmoxCoordinator, str, int], None]
    permission: ProxmoxPermission = ProxmoxPermission.POWER
    permission_target: str = "vms"


VM_SENSORS: tuple[ProxmoxVMSensorEntityDescription, ...] = (
    ProxmoxVMSensorEntityDescription(
        key="vm_max_cpu",
        translation_key="vm_max_cpu",
        value_fn=lambda data: data["cpus"],
        entity_category=EntityCategory.DIAGNOSTIC,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    ),
    ProxmoxVMSensorEntityDescription(
        key="vm_cpu",
        translation_key="vm_cpu",
        value_fn=lambda data: data["cpu"] * 100,
        native_unit_of_measurement=PERCENTAGE,
        entity_category=EntityCategory.DIAGNOSTIC,
        suggested_display_precision=2,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    ProxmoxVMSensorEntityDescription(
        key="vm_memory",
        translation_key="vm_memory",
        value_fn=lambda data: data["mem"],
        device_class=SensorDeviceClass.DATA_SIZE,
        native_unit_of_measurement=UnitOfInformation.BYTES,
        suggested_unit_of_measurement=UnitOfInformation.GIBIBYTES,
        suggested_display_precision=1,
        entity_category=EntityCategory.DIAGNOSTIC,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    ),
    ProxmoxVMSensorEntityDescription(
        key="vm_max_memory",
        translation_key="vm_max_memory",
        value_fn=lambda data: data["maxmem"],
        device_class=SensorDeviceClass.DATA_SIZE,
        native_unit_of_measurement=UnitOfInformation.BYTES,
        suggested_unit_of_measurement=UnitOfInformation.GIBIBYTES,
        suggested_display_precision=1,
        entity_category=EntityCategory.DIAGNOSTIC,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    ProxmoxVMSensorEntityDescription(
        key="vm_memory_percentage",
        translation_key="vm_memory_percentage",
        value_fn=lambda data: int(data["mem"]) / int(data["maxmem"]) * 100,
        native_unit_of_measurement=PERCENTAGE,
        entity_category=EntityCategory.DIAGNOSTIC,
        suggested_display_precision=2,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    ProxmoxVMSensorEntityDescription(
        key="vm_uptime",
        translation_key="vm_uptime",
        value_fn=lambda data: data.get("uptime"),
        device_class=SensorDeviceClass.DURATION,
        native_unit_of_measurement=UnitOfTime.SECONDS,
        suggested_unit_of_measurement=UnitOfTime.HOURS,
        entity_category=EntityCategory.DIAGNOSTIC,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    ProxmoxVMSensorEntityDescription(
        key="vm_disk",
        translation_key="vm_disk",
        value_fn=lambda data: data["disk"],
        device_class=SensorDeviceClass.DATA_SIZE,
        native_unit_of_measurement=UnitOfInformation.BYTES,
        suggested_unit_of_measurement=UnitOfInformation.GIBIBYTES,
        suggested_display_precision=1,
        entity_category=EntityCategory.DIAGNOSTIC,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    ),
    ProxmoxVMSensorEntityDescription(
        key="vm_max_disk",
        translation_key="vm_max_disk",
        value_fn=lambda data: data["maxdisk"],
        device_class=SensorDeviceClass.DATA_SIZE,
        native_unit_of_measurement=UnitOfInformation.BYTES,
        suggested_unit_of_measurement=UnitOfInformation.GIBIBYTES,
        suggested_display_precision=1,
        entity_category=EntityCategory.DIAGNOSTIC,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    ),
    ProxmoxVMSensorEntityDescription(
        key="vm_status",
        translation_key="vm_status",
        value_fn=lambda data: data["status"],
        device_class=SensorDeviceClass.ENUM,
        options=["running", "stopped", "suspended"],
    ),
    ProxmoxVMSensorEntityDescription(
        key="vm_netin",
        translation_key="vm_netin",
        value_fn=lambda data: data["netin"],
        device_class=SensorDeviceClass.DATA_SIZE,
        native_unit_of_measurement=UnitOfInformation.BYTES,
        suggested_unit_of_measurement=UnitOfInformation.GIBIBYTES,
        suggested_display_precision=1,
        entity_category=EntityCategory.DIAGNOSTIC,
        state_class=SensorStateClass.TOTAL_INCREASING,
        entity_registry_enabled_default=False,
    ),
    ProxmoxVMSensorEntityDescription(
        key="vm_netout",
        translation_key="vm_netout",
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

VM_BINARY_SENSORS: tuple[ProxmoxVMBinarySensorEntityDescription, ...] = (
    ProxmoxVMBinarySensorEntityDescription(
        key="status",
        translation_key="status",
        state_fn=lambda data: data["status"] == VM_CONTAINER_RUNNING,
        device_class=BinarySensorDeviceClass.RUNNING,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
)

VM_BUTTONS: tuple[ProxmoxVMButtonEntityDescription, ...] = (
    ProxmoxVMButtonEntityDescription(
        key="start",
        translation_key="start",
        press_action=lambda coordinator, node, vmid: coordinator.client.start_vm(
            node, vmid
        ),
        entity_category=EntityCategory.CONFIG,
    ),
    ProxmoxVMButtonEntityDescription(
        key="stop",
        translation_key="stop",
        press_action=lambda coordinator, node, vmid: coordinator.client.stop_vm(
            node, vmid
        ),
        entity_category=EntityCategory.CONFIG,
    ),
    ProxmoxVMButtonEntityDescription(
        key="restart",
        press_action=lambda coordinator, node, vmid: coordinator.client.reboot_vm(
            node, vmid
        ),
        entity_category=EntityCategory.CONFIG,
        device_class=ButtonDeviceClass.RESTART,
    ),
    ProxmoxVMButtonEntityDescription(
        key="hibernate",
        translation_key="hibernate",
        press_action=lambda coordinator, node, vmid: coordinator.client.suspend_vm(
            node, vmid
        ),
        entity_category=EntityCategory.CONFIG,
    ),
    ProxmoxVMButtonEntityDescription(
        key="resume",
        translation_key="resume",
        press_action=lambda coordinator, node, vmid: coordinator.client.resume_vm(
            node, vmid
        ),
        entity_category=EntityCategory.CONFIG,
    ),
    ProxmoxVMButtonEntityDescription(
        key="reset",
        translation_key="reset",
        press_action=lambda coordinator, node, vmid: coordinator.client.reset_vm(
            node, vmid
        ),
        entity_category=EntityCategory.CONFIG,
    ),
    ProxmoxVMButtonEntityDescription(
        key="shutdown",
        translation_key="shutdown",
        press_action=lambda coordinator, node, vmid: coordinator.client.shutdown_vm(
            node, vmid
        ),
        entity_category=EntityCategory.CONFIG,
    ),
    ProxmoxVMButtonEntityDescription(
        key="snapshot_create",
        translation_key="snapshot_create",
        press_action=lambda coordinator, node, vmid: (
            coordinator.client.create_vm_snapshot(
                node,
                vmid,
                name=(
                    "homeassistant_snapshot_"
                    f"{coordinator.data[node].vms[vmid]['name']}_"
                    f"{dt_util.utcnow().strftime('%Y%m%d%H%M%S')}"
                ),
            )
        ),
        permission=ProxmoxPermission.SNAPSHOT,
        entity_category=EntityCategory.CONFIG,
    ),
)


class ProxmoxVMSensor(ProxmoxVMEntity, SensorEntity):
    """Represents a Proxmox VE VM sensor."""

    entity_description: ProxmoxVMSensorEntityDescription

    @property
    @override
    def native_value(self) -> StateType:
        """Return the native value of the sensor."""
        return self.entity_description.value_fn(self.vm_data)


class ProxmoxVMBinarySensor(ProxmoxVMEntity, BinarySensorEntity):
    """Representation of a Proxmox VM binary sensor."""

    entity_description: ProxmoxVMBinarySensorEntityDescription

    @property
    @override
    def is_on(self) -> bool | None:
        """Return true if the binary sensor is on."""
        return self.entity_description.state_fn(self.vm_data)


class ProxmoxVMButtonEntity(ProxmoxVMEntity, ProxmoxBaseButton):
    """Represents a Proxmox VM button entity."""

    entity_description: ProxmoxVMButtonEntityDescription

    @override
    async def _async_press_call(self) -> None:
        """Execute the VM button action via executor."""
        await self.hass.async_add_executor_job(
            self.entity_description.press_action,
            self.coordinator,
            self._node_name,
            self.vm_data["vmid"],
        )
