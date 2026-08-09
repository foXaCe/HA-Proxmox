"""Tests for pure helpers."""

from __future__ import annotations

from custom_components.proxmoxve.const import ProxmoxPermission
from custom_components.proxmoxve.helpers import is_granted, sanitize_config_entry


def test_sanitize_config_entry_pam_realm() -> None:
    """Username with @ realm is split and rebuilt with realm."""
    data = {
        "auth_method": "pam",
        "username": "root@pam",
        "realm": "pam",
        "token": False,
    }
    result = sanitize_config_entry(data)
    assert result["username"] == "root@pam"
    assert result["realm"] == "pam"


def test_sanitize_config_entry_other_realm() -> None:
    """Custom realm is preserved."""
    data = {
        "auth_method": "other",
        "username": "user@ldap",
        "realm": "ldap",
        "token": False,
    }
    result = sanitize_config_entry(data)
    assert result["username"] == "user@ldap"
    assert result["realm"] == "ldap"


def test_sanitize_config_entry_pve_realm() -> None:
    """pve auth method maps to pve realm."""
    data = {
        "auth_method": "pve",
        "username": "user",
        "realm": "pam",
        "token": False,
    }
    result = sanitize_config_entry(data)
    assert result["username"] == "user@pve"
    assert result["realm"] == "pve"


def test_sanitize_config_entry_token_id_with_bang() -> None:
    """Token ID with user@realm!name is stripped to the bare name."""
    data = {
        "auth_method": "pam",
        "username": "root@pam",
        "realm": "pam",
        "token": True,
        "token_id": "root@pam!myapp",
    }
    result = sanitize_config_entry(data)
    assert result["token_id"] == "myapp"


def test_sanitize_config_entry_token_id_without_bang() -> None:
    """Token ID without bang is left untouched."""
    data = {
        "auth_method": "pam",
        "username": "root@pam",
        "realm": "pam",
        "token": True,
        "token_id": "myapp",
    }
    result = sanitize_config_entry(data)
    assert result["token_id"] == "myapp"


def test_sanitize_config_entry_no_token() -> None:
    """No token means no token_id transformation."""
    data = {
        "auth_method": "pam",
        "username": "root@pam",
        "realm": "pam",
        "token": False,
        "token_id": "root@pam!myapp",
    }
    result = sanitize_config_entry(data)
    assert result["token_id"] == "root@pam!myapp"


def test_sanitize_config_entry_does_not_mutate_input() -> None:
    """The input mapping is not modified."""
    data = {
        "auth_method": "pam",
        "username": "root",
        "realm": "pam",
        "token": False,
    }
    sanitize_config_entry(data)
    assert data["username"] == "root"


def test_is_granted_permission_on_specific_path() -> None:
    """Permission granted on the specific path."""
    permissions = {"/vms/100": {"VM.PowerMgmt": 1}}
    assert is_granted(permissions, "vms", 100, ProxmoxPermission.POWER)


def test_is_granted_permission_denied_on_specific_path() -> None:
    """Permission explicitly denied on the specific path."""
    permissions = {"/vms/100": {"VM.PowerMgmt": 0}}
    assert not is_granted(permissions, "vms", 100, ProxmoxPermission.POWER)


def test_is_granted_permission_on_parent_path() -> None:
    """Permission granted on the collection path."""
    permissions = {"/vms": {"VM.PowerMgmt": 1}}
    assert is_granted(permissions, "vms", 100, ProxmoxPermission.POWER)


def test_is_granted_permission_on_root() -> None:
    """Permission granted on root path."""
    permissions = {"/": {"VM.PowerMgmt": 1}}
    assert is_granted(permissions, "vms", 100, ProxmoxPermission.POWER)


def test_is_granted_no_permission_anywhere() -> None:
    """No permission found returns False."""
    permissions: dict[str, dict[str, int]] = {}
    assert not is_granted(permissions, "vms", 100, ProxmoxPermission.POWER)


def test_is_granted_prefers_most_specific_path() -> None:
    """The most specific path wins even if parent grants."""
    permissions = {
        "/": {"VM.PowerMgmt": 1},
        "/vms/100": {"VM.PowerMgmt": 0},
    }
    assert not is_granted(permissions, "vms", 100, ProxmoxPermission.POWER)
