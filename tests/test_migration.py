"""Tests for config entry migration."""

from __future__ import annotations

from homeassistant.const import CONF_TOKEN
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.proxmoxve.__init__ import async_migrate_entry
from custom_components.proxmoxve.const import (
    CONF_AUTH_METHOD,
    CONF_REALM,
    DOMAIN,
)


async def test_migrate_v1_to_v3(hass: HomeAssistant) -> None:
    """A v1 entry migrates to v3 with realm and auth_method."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="old",
        data={
            "host": "192.168.1.60",
            "port": 8006,
            "username": "root@pam",
            "password": "secret",
        },
        entry_id="migrate_v1",
        version=1,
    )
    entry.add_to_hass(hass)

    assert await async_migrate_entry(hass, entry)
    assert entry.version == 3
    assert entry.data[CONF_REALM] == "pam"
    assert entry.data[CONF_AUTH_METHOD] == "pam"
    assert entry.data[CONF_TOKEN] is False


async def test_migrate_v2_to_v3(hass: HomeAssistant) -> None:
    """A v2 entry gains auth_method and token flag."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="old",
        data={
            "host": "192.168.1.60",
            "port": 8006,
            "username": "root",
            "password": "secret",
            "realm": "pve",
        },
        entry_id="migrate_v2",
        version=2,
    )
    entry.add_to_hass(hass)

    assert await async_migrate_entry(hass, entry)
    assert entry.version == 3
    assert entry.data[CONF_REALM] == "pve"
    assert entry.data[CONF_AUTH_METHOD] == "pve"
    assert entry.data[CONF_TOKEN] is False


async def test_migrate_v3_noop(hass: HomeAssistant) -> None:
    """A v3 entry is left untouched."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="current",
        data={
            "host": "192.168.1.60",
            "port": 8006,
            "username": "root@pam",
            "password": "secret",
            "realm": "pam",
            "auth_method": "pam",
            "token": False,
        },
        entry_id="migrate_v3",
        version=3,
    )
    entry.add_to_hass(hass)

    assert await async_migrate_entry(hass, entry)
    assert entry.version == 3
