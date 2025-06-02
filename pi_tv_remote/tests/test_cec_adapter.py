"""Tests for the CEC Adapter module."""

from unittest.mock import MagicMock, patch

import pytest

from pi_tv_remote.cec_adapter import CECAdapter, CECConfig, RemoteButton


def test_cec_config_defaults():
    """Test that CECConfig has expected defaults."""
    config = CECConfig()
    assert config.device_name == "RaspberryPi"
    assert config.physical_address == "1.0.0.0"
    assert config.port == 1
    assert config.auto_power_on is True
    assert config.device_type == 1


@patch("pi_tv_remote.cec_adapter.get_cec_module")
def test_cec_adapter_init(mock_get_cec):
    """Test CECAdapter initialization."""
    # Mock the CEC module
    mock_cec = MagicMock()
    mock_get_cec.return_value = mock_cec

    # Create adapter with custom config
    config = CECConfig(device_name="TestDevice", physical_address="2.0.0.0")
    adapter = CECAdapter(config, debug=True)

    # Assert config was stored correctly
    assert adapter.config.device_name == "TestDevice"
    assert adapter.config.physical_address == "2.0.0.0"

    # Assert callbacks dictionaries were initialized
    assert adapter.callbacks == {}
    assert adapter.command_callbacks == {}
