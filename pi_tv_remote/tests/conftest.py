"""
pytest configuration for CEC adapter tests.
"""

import pytest


def pytest_configure(config):
    """Configure pytest."""
    # Register custom markers
    config.addinivalue_line(
        "markers", "standby: marks tests that put the TV in standby mode"
    )


def pytest_addoption(parser):
    """Add custom command line options."""
    parser.addoption(
        "--skip-standby",
        action="store_true",
        default=False,
        help="Skip tests that put the TV in standby mode",
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection based on options."""
    if config.getoption("--skip-standby"):
        # Skip tests marked with 'standby'
        skip_standby = pytest.mark.skip(reason="--skip-standby option provided")
        for item in items:
            if "standby" in item.keywords:
                item.add_marker(skip_standby)
