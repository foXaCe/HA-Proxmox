"""Constants for ProxmoxVE."""

from __future__ import annotations

from enum import StrEnum
from typing import Final

DOMAIN: Final = "proxmoxve"
CONF_AUTH_METHOD: Final = "auth_method"
CONF_REALM: Final = "realm"
CONF_NODE: Final = "node"
CONF_NODES: Final = "nodes"
CONF_TOKEN_ID: Final = "token_id"
CONF_TOKEN_SECRET: Final = "token_value"
CONF_VMS: Final = "vms"
CONF_CONTAINERS: Final = "containers"

CONF_USER: Final = "user"
CONF_SCAN_INTERVAL: Final = "scan_interval"

NODE_ONLINE: Final = "online"
VM_CONTAINER_RUNNING: Final = "running"

STORAGE_ACTIVE: Final = 1
STORAGE_SHARED: Final = 1
STORAGE_ENABLED: Final = 1
STATUS_OK: Final = "OK"

AUTH_PAM: Final = "pam"
AUTH_PVE: Final = "pve"
AUTH_OTHER: Final = "other"
AUTH_METHODS: Final = [AUTH_PAM, AUTH_PVE, AUTH_OTHER]

DEFAULT_PORT: Final = 8006
DEFAULT_REALM: Final = AUTH_PAM
DEFAULT_TIMEOUT: Final = 30
DEFAULT_VERIFY_SSL: Final = True
DEFAULT_SCAN_INTERVAL: Final = 60
MIN_SCAN_INTERVAL: Final = 5
TYPE_VM: Final = 0
TYPE_CONTAINER: Final = 1
UPDATE_INTERVAL: Final = 60


class ProxmoxPermission(StrEnum):
    """Proxmox permissions."""

    POWER = "VM.PowerMgmt"
    SNAPSHOT = "VM.Snapshot"
    SYSAUDIT = "Sys.Audit"
    SYSPOWER = "Sys.PowerMgmt"
    VMAUDIT = "VM.Audit"
