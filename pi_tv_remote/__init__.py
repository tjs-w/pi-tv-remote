"""Pi TV Remote - A Raspberry Pi TV remote control module."""

__version__ = "0.1.0"

# Import essential classes and functions for public API
from pi_tv_remote.cec_adapter import CECAdapter, CECCommand, CECConfig, RemoteButton

# Import main function for CLI use
from pi_tv_remote.cli import main

__all__ = [
    "CECAdapter",
    "CECConfig",
    "RemoteButton",
    "CECCommand",
    "main",
]
