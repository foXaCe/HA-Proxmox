"""Tests for diagnostics."""

from __future__ import annotations

from unittest.mock import MagicMock

from homeassistant.core import HomeAssistant

from custom_components.proxmoxve.diagnostics import (
    TO_REDACT,
    async_get_config_entry_diagnostics,
)

from .conftest import MOCK_HOST, NODE, MockNodeResources


async def test_diagnostics_redacts_sensitive_data(
    hass: HomeAssistant, config_entry, mock_client: MagicMock
) -> None:
    """Diagnostics redact host, credentials and tokens."""
    mock_client.fetch_all_nodes.return_value = [(NODE, MockNodeResources())]
    config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    diagnostics = await async_get_config_entry_diagnostics(hass, config_entry)

    config = diagnostics["config_entry"]
    assert config["data"]["host"] == "**REDACTED**"
    assert config["data"]["password"] == "**REDACTED**"
    assert config["data"]["username"] == "**REDACTED**"

    assert "devices" in diagnostics
    assert MOCK_HOST in [config["title"] for config in [config]]


def test_redact_list_contains_all_secrets() -> None:
    """The redact list covers every sensitive key."""
    assert "host" in TO_REDACT
    assert "password" in TO_REDACT
    assert "username" in TO_REDACT
    assert "token_value" in TO_REDACT
    assert "user" in TO_REDACT
