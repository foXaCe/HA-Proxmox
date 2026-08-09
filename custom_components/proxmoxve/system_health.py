"""System health support for Proxmox VE."""

from __future__ import annotations

from homeassistant.components import system_health
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .coordinator import ProxmoxConfigEntry


async def async_register(
    hass: HomeAssistant,
    register: system_health.SystemHealthRegistration,
) -> None:
    """Register system health callbacks."""
    register.async_register_info(system_health_info, "/config/integrations")


async def system_health_info(hass: HomeAssistant) -> dict[str, object]:
    """Return system health information for the Proxmox VE integration."""
    entries: list[ProxmoxConfigEntry] = hass.config_entries.async_entries(DOMAIN)
    info: dict[str, object] = {
        "instances": len(entries),
    }
    if entries:
        coordinator = entries[0].runtime_data
        info["client_version"] = coordinator.client.proxmox.version.get().get(
            "version", "unknown"
        )
    return info
