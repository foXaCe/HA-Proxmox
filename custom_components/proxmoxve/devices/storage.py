"""Storage entities for Proxmox VE."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, override

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.components.sensor import (
    EntityCategory,
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
    StateType,
)
from homeassistant.const import PERCENTAGE, UnitOfInformation

from ..const import STORAGE_ACTIVE, STORAGE_ENABLED, STORAGE_SHARED
from ..entity import ProxmoxStorageEntity


@dataclass(frozen=True, kw_only=True)
class ProxmoxStorageSensorEntityDescription(SensorEntityDescription):
    """Class to hold Proxmox storage sensor description."""

    value_fn: Callable[[dict[str, Any]], StateType]


@dataclass(frozen=True, kw_only=True)
class ProxmoxStorageBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Class to hold Proxmox storage binary sensor description."""

    state_fn: Callable[[dict[str, Any]], bool | None]


STORAGE_SENSORS: tuple[ProxmoxStorageSensorEntityDescription, ...] = (
    ProxmoxStorageSensorEntityDescription(
        key="storage_used",
        translation_key="storage_used",
        value_fn=lambda data: data["used"],
        device_class=SensorDeviceClass.DATA_SIZE,
        native_unit_of_measurement=UnitOfInformation.BYTES,
        suggested_unit_of_measurement=UnitOfInformation.GIBIBYTES,
        suggested_display_precision=1,
        entity_category=EntityCategory.DIAGNOSTIC,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    ProxmoxStorageSensorEntityDescription(
        key="storage_total",
        translation_key="storage_total",
        value_fn=lambda data: data["total"],
        device_class=SensorDeviceClass.DATA_SIZE,
        native_unit_of_measurement=UnitOfInformation.BYTES,
        suggested_unit_of_measurement=UnitOfInformation.GIBIBYTES,
        suggested_display_precision=1,
        entity_category=EntityCategory.DIAGNOSTIC,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    ProxmoxStorageSensorEntityDescription(
        key="storage_available",
        translation_key="storage_available",
        value_fn=lambda data: data["avail"],
        device_class=SensorDeviceClass.DATA_SIZE,
        native_unit_of_measurement=UnitOfInformation.BYTES,
        suggested_unit_of_measurement=UnitOfInformation.GIBIBYTES,
        suggested_display_precision=1,
        entity_category=EntityCategory.DIAGNOSTIC,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    ProxmoxStorageSensorEntityDescription(
        key="storage_used_percentage",
        translation_key="storage_used_percentage",
        value_fn=lambda data: (
            round(value * 100, 1)
            if (value := data.get("used_fraction")) is not None
            else None
        ),
        native_unit_of_measurement=PERCENTAGE,
        entity_category=EntityCategory.DIAGNOSTIC,
        state_class=SensorStateClass.MEASUREMENT,
    ),
)

STORAGE_BINARY_SENSORS: tuple[ProxmoxStorageBinarySensorEntityDescription, ...] = (
    ProxmoxStorageBinarySensorEntityDescription(
        key="storage_active",
        translation_key="storage_active",
        state_fn=lambda data: data["active"] == STORAGE_ACTIVE,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    ProxmoxStorageBinarySensorEntityDescription(
        key="storage_enabled",
        translation_key="storage_enabled",
        state_fn=lambda data: data["enabled"] == STORAGE_ENABLED,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    ProxmoxStorageBinarySensorEntityDescription(
        key="storage_shared",
        translation_key="storage_shared",
        state_fn=lambda data: data["shared"] == STORAGE_SHARED,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
)


class ProxmoxStorageSensor(ProxmoxStorageEntity, SensorEntity):
    """Represents a Proxmox VE storage sensor."""

    entity_description: ProxmoxStorageSensorEntityDescription

    @property
    @override
    def native_value(self) -> StateType:
        """Return the native value of the sensor."""
        return self.entity_description.value_fn(self.storage_data)


class ProxmoxStorageBinarySensor(ProxmoxStorageEntity, BinarySensorEntity):
    """Representation of a Proxmox Storage binary sensor."""

    entity_description: ProxmoxStorageBinarySensorEntityDescription

    @property
    @override
    def is_on(self) -> bool | None:
        """Return true if the binary sensor is on."""
        return self.entity_description.state_fn(self.storage_data)
