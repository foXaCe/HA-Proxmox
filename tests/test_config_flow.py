"""Tests for the Proxmox config flow."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from custom_components.proxmoxve.api.exceptions import (
    ProxmoxAuthError,
    ProxmoxConnectionError,
    ProxmoxServerError,
    ProxmoxSSLError,
    ProxmoxTimeoutError,
)
from custom_components.proxmoxve.const import (
    CONF_AUTH_METHOD,
    CONF_NODE,
    CONF_NODES,
    CONF_SCAN_INTERVAL,
    DOMAIN,
)

from .conftest import (
    MOCK_HOST,
    MOCK_NODE_NAME,
    MOCK_PASSWORD,
    MOCK_PORT,
    MOCK_USERNAME,
    NODE,
)


async def test_config_flow_user_step_shows_form(hass: HomeAssistant) -> None:
    """The initial step shows the user form."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"


async def test_config_flow_full_flow_password(
    hass: HomeAssistant, mock_client: MagicMock
) -> None:
    """The full flow with password creates an entry."""
    mock_client.connect.return_value = None
    mock_client.get_nodes.return_value = [NODE]
    mock_client.get_vms.return_value = []
    mock_client.get_containers.return_value = []

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == FlowResultType.FORM

    with patch(
        "custom_components.proxmoxve.config_flow.ProxmoxClient",
        return_value=mock_client,
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_AUTH_METHOD: "pam",
                "host": MOCK_HOST,
                "username": MOCK_USERNAME,
                "port": MOCK_PORT,
                "token": False,
                "verify_ssl": False,
            },
        )
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user_auth"

    with patch(
        "custom_components.proxmoxve.config_flow.ProxmoxClient",
        return_value=mock_client,
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], {"password": MOCK_PASSWORD}
        )
    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["title"] == MOCK_HOST
    assert CONF_NODES in result["data"]
    assert result["data"][CONF_NODES][0][CONF_NODE] == MOCK_NODE_NAME


async def test_config_flow_invalid_auth(
    hass: HomeAssistant, mock_client: MagicMock
) -> None:
    """Invalid credentials show invalid_auth error."""
    mock_client.connect.side_effect = ProxmoxAuthError

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    with patch(
        "custom_components.proxmoxve.config_flow.ProxmoxClient",
        return_value=mock_client,
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_AUTH_METHOD: "pam",
                "host": MOCK_HOST,
                "username": MOCK_USERNAME,
                "port": MOCK_PORT,
                "token": False,
                "verify_ssl": False,
            },
        )
    with patch(
        "custom_components.proxmoxve.config_flow.ProxmoxClient",
        return_value=mock_client,
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], {"password": "wrong"}
        )
    assert result["type"] == FlowResultType.FORM
    assert result["errors"] == {"base": "invalid_auth"}


async def test_config_flow_cannot_connect(
    hass: HomeAssistant, mock_client: MagicMock
) -> None:
    """Connection error shows cannot_connect error."""
    mock_client.connect.side_effect = ProxmoxConnectionError

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    with patch(
        "custom_components.proxmoxve.config_flow.ProxmoxClient",
        return_value=mock_client,
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_AUTH_METHOD: "pam",
                "host": MOCK_HOST,
                "username": MOCK_USERNAME,
                "port": MOCK_PORT,
                "token": False,
                "verify_ssl": False,
            },
        )
    with patch(
        "custom_components.proxmoxve.config_flow.ProxmoxClient",
        return_value=mock_client,
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], {"password": "wrong"}
        )
    assert result["type"] == FlowResultType.FORM
    assert result["errors"] == {"base": "cannot_connect"}


async def test_config_flow_ssl_error(
    hass: HomeAssistant, mock_client: MagicMock
) -> None:
    """SSL error shows ssl_error."""
    mock_client.connect.side_effect = ProxmoxSSLError

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    with patch(
        "custom_components.proxmoxve.config_flow.ProxmoxClient",
        return_value=mock_client,
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_AUTH_METHOD: "pam",
                "host": MOCK_HOST,
                "username": MOCK_USERNAME,
                "port": MOCK_PORT,
                "token": False,
                "verify_ssl": False,
            },
        )
    with patch(
        "custom_components.proxmoxve.config_flow.ProxmoxClient",
        return_value=mock_client,
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], {"password": "wrong"}
        )
    assert result["type"] == FlowResultType.FORM
    assert result["errors"] == {"base": "ssl_error"}


async def test_config_flow_already_configured(
    hass: HomeAssistant, config_entry, mock_client: MagicMock
) -> None:
    """A duplicate host aborts with already_configured."""
    config_entry.add_to_hass(hass)
    mock_client.connect.return_value = None
    mock_client.get_nodes.return_value = [NODE]
    mock_client.get_vms.return_value = []
    mock_client.get_containers.return_value = []

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    with patch(
        "custom_components.proxmoxve.config_flow.ProxmoxClient",
        return_value=mock_client,
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_AUTH_METHOD: "pam",
                "host": MOCK_HOST,
                "username": MOCK_USERNAME,
                "port": MOCK_PORT,
                "token": False,
                "verify_ssl": False,
            },
        )
    with patch(
        "custom_components.proxmoxve.config_flow.ProxmoxClient",
        return_value=mock_client,
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], {"password": MOCK_PASSWORD}
        )
    assert result["type"] == FlowResultType.ABORT
    assert result["reason"] == "already_configured"


async def test_options_flow_scan_interval(hass: HomeAssistant, config_entry) -> None:
    """The options flow updates the scan interval."""
    config_entry.add_to_hass(hass)
    result = await hass.config_entries.options.async_init(config_entry.entry_id)
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "init"

    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {CONF_SCAN_INTERVAL: 30}
    )
    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["data"] == {CONF_SCAN_INTERVAL: 30}


async def test_options_flow_invalid_scan_interval(
    hass: HomeAssistant, config_entry
) -> None:
    """A too-small scan interval shows an error."""
    config_entry.add_to_hass(hass)
    result = await hass.config_entries.options.async_init(config_entry.entry_id)

    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {CONF_SCAN_INTERVAL: 1}
    )
    assert result["type"] == FlowResultType.FORM
    assert result["errors"] == {"base": "invalid_scan_interval"}


async def test_reauth_flow(
    hass: HomeAssistant, config_entry, mock_client: MagicMock
) -> None:
    """Reauth updates credentials and reloads the entry."""
    config_entry.add_to_hass(hass)
    mock_client.connect.return_value = None
    mock_client.get_nodes.return_value = [NODE]

    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={
            "source": config_entries.SOURCE_REAUTH,
            "entry_id": config_entry.entry_id,
        },
    )
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "reauth_confirm"

    with patch(
        "custom_components.proxmoxve.config_flow.ProxmoxClient",
        return_value=mock_client,
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], {"password": "new-password"}
        )
    assert result["type"] == FlowResultType.ABORT
    assert result["reason"] == "reauth_successful"
    await hass.async_block_till_done()


async def test_reconfigure_flow(
    hass: HomeAssistant, config_entry, mock_client: MagicMock
) -> None:
    """Reconfigure updates the connection settings."""
    config_entry.add_to_hass(hass)
    mock_client.connect.return_value = None
    mock_client.get_nodes.return_value = [NODE]
    mock_client.get_vms.return_value = []
    mock_client.get_containers.return_value = []

    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={
            "source": config_entries.SOURCE_RECONFIGURE,
            "entry_id": config_entry.entry_id,
        },
    )
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "reconfigure"

    with patch(
        "custom_components.proxmoxve.config_flow.ProxmoxClient",
        return_value=mock_client,
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_AUTH_METHOD: "pam",
                "host": MOCK_HOST,
                "username": MOCK_USERNAME,
                "port": MOCK_PORT,
                "token": False,
                "verify_ssl": False,
            },
        )
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "reconfigure_auth"

    with patch(
        "custom_components.proxmoxve.config_flow.ProxmoxClient",
        return_value=mock_client,
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], {"password": "new-password"}
        )
    assert result["type"] == FlowResultType.ABORT
    assert result["reason"] == "reconfigure_successful"
    await hass.async_block_till_done()


async def test_config_flow_no_nodes(
    hass: HomeAssistant, mock_client: MagicMock
) -> None:
    """No nodes found shows no_nodes_found."""
    mock_client.connect.return_value = None
    mock_client.get_nodes.return_value = []

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    with patch(
        "custom_components.proxmoxve.config_flow.ProxmoxClient",
        return_value=mock_client,
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_AUTH_METHOD: "pam",
                "host": MOCK_HOST,
                "username": MOCK_USERNAME,
                "port": MOCK_PORT,
                "token": False,
                "verify_ssl": False,
            },
        )
    with patch(
        "custom_components.proxmoxve.config_flow.ProxmoxClient",
        return_value=mock_client,
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], {"password": "wrong"}
        )
    assert result["type"] == FlowResultType.FORM
    assert result["errors"] == {"base": "no_nodes_found"}


async def test_config_flow_no_vmlxc(
    hass: HomeAssistant, mock_client: MagicMock
) -> None:
    """No VMs/LXC found shows no_vmlxc_found."""

    mock_client.connect.return_value = None
    mock_client.get_nodes.return_value = [NODE]
    mock_client.get_vms.side_effect = ProxmoxServerError

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    with patch(
        "custom_components.proxmoxve.config_flow.ProxmoxClient",
        return_value=mock_client,
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_AUTH_METHOD: "pam",
                "host": MOCK_HOST,
                "username": MOCK_USERNAME,
                "port": MOCK_PORT,
                "token": False,
                "verify_ssl": False,
            },
        )
    with patch(
        "custom_components.proxmoxve.config_flow.ProxmoxClient",
        return_value=mock_client,
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], {"password": "wrong"}
        )
    assert result["type"] == FlowResultType.FORM
    assert result["errors"] == {"base": "no_vmlxc_found"}


async def test_config_flow_timeout(hass: HomeAssistant, mock_client: MagicMock) -> None:
    """Timeout shows connect_timeout."""

    mock_client.connect.side_effect = ProxmoxTimeoutError

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    with patch(
        "custom_components.proxmoxve.config_flow.ProxmoxClient",
        return_value=mock_client,
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_AUTH_METHOD: "pam",
                "host": MOCK_HOST,
                "username": MOCK_USERNAME,
                "port": MOCK_PORT,
                "token": False,
                "verify_ssl": False,
            },
        )
    with patch(
        "custom_components.proxmoxve.config_flow.ProxmoxClient",
        return_value=mock_client,
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], {"password": "wrong"}
        )
    assert result["type"] == FlowResultType.FORM
    assert result["errors"] == {"base": "connect_timeout"}
