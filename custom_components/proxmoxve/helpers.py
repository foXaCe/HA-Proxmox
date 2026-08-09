"""Helpers for Proxmox VE."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from homeassistant.const import CONF_TOKEN, CONF_USERNAME

from .const import (
    AUTH_OTHER,
    CONF_AUTH_METHOD,
    CONF_REALM,
    CONF_TOKEN_ID,
    ProxmoxPermission,
)


def sanitize_config_entry(input_data: Mapping[str, Any]) -> dict[str, Any]:
    """Sanitize the user ID and realm in config entry data."""
    data = dict(input_data)
    username = data[CONF_USERNAME].split("@")[0]
    provider = data[CONF_AUTH_METHOD]

    realm = provider.lower()
    if provider == AUTH_OTHER:
        realm = data[CONF_REALM]

    data[CONF_REALM] = realm
    data[CONF_USERNAME] = f"{username}@{realm}"

    if data.get(CONF_TOKEN) and data.get(CONF_TOKEN_ID) and "!" in data[CONF_TOKEN_ID]:
        data[CONF_TOKEN_ID] = data[CONF_TOKEN_ID].split("!")[1]

    return data


def is_granted(
    permissions: dict[str, dict[str, int]],
    p_type: str = "vms",
    p_id: str | int | None = None,  # can be str for nodes
    permission: ProxmoxPermission = ProxmoxPermission.POWER,
) -> bool:
    """Validate user permissions for the given type and permission."""
    paths = [f"/{p_type}/{p_id}", f"/{p_type}", "/"]
    for path in paths:
        value = permissions.get(path, {}).get(permission)
        if value is not None:
            return value == 1
    return False
