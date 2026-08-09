"""Exceptions for Proxmox VE API."""

from __future__ import annotations

from homeassistant.exceptions import HomeAssistantError


class ProxmoxApiError(HomeAssistantError):
    """Base class for Proxmox VE API errors."""


class ProxmoxAuthError(ProxmoxApiError):
    """Raised when authentication fails."""


class ProxmoxConnectionError(ProxmoxApiError):
    """Raised when a connection to the Proxmox VE server fails."""


class ProxmoxTimeoutError(ProxmoxApiError):
    """Raised when a connection to the Proxmox VE server times out."""


class ProxmoxSSLError(ProxmoxApiError):
    """Raised on SSL errors when connecting to the Proxmox VE server."""


class ProxmoxPermissionsError(ProxmoxApiError):
    """Raised when failing to retrieve permissions."""


class ProxmoxNodesNotFoundError(ProxmoxApiError):
    """Raised when the API works but no nodes are visible."""


class ProxmoxServerError(ProxmoxApiError):
    """Raised when the Proxmox VE server returns an error."""


class ProxmoxNoVMLXCFoundError(ProxmoxApiError):
    """Raised when no LXC or VM are found on a node."""
