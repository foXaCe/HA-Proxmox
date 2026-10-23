"""System health support for Proxmox VE."""

from __future__ import annotations

from homeassistant.components import system_health
from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant, callback

from .const import DOMAIN
from .coordinator import ProxmoxConfigEntry


@callback
def async_register(
    hass: HomeAssistant,
    register: system_health.SystemHealthRegistration,
) -> None:
    """Register system health callbacks.

    Home Assistant calls this synchronously: declared ``async``, it returned a
    coroutine nobody awaited, nothing was registered and the system health page
    failed with an ``AssertionError``.
    """
    register.async_register_info(system_health_info, "/config/integrations")


async def system_health_info(hass: HomeAssistant) -> dict[str, object]:
    """Return system health information for the Proxmox VE integration."""
    entries: list[ProxmoxConfigEntry] = hass.config_entries.async_entries(DOMAIN)
    info: dict[str, object] = {
        "instances": len(entries),
    }
    loaded = [entry for entry in entries if entry.state is ConfigEntryState.LOADED]
    if loaded:
        coordinator = loaded[0].runtime_data
        try:
            # proxmoxer is synchronous: never call it on the event loop.
            version = await hass.async_add_executor_job(
                coordinator.client.proxmox.version.get
            )
        except Exception:  # noqa: BLE001 - reported on the page, not raised
            info["client_version"] = "unreachable"
        else:
            info["client_version"] = version.get("version", "unknown")
    return info
