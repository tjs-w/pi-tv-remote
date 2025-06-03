#!/usr/bin/env python3
"""
PiTVRemote - CEC Adapter for Raspberry Pi
Requires Raspberry Pi hardware with HDMI-CEC support and the python-cec package.
"""
import os
import platform
import subprocess
import sys

from setuptools import Command, find_packages, setup
from setuptools.command.develop import develop
from setuptools.command.install import install

# Check if we're on Raspberry Pi
is_raspberry_pi = (
    platform.system() == "Linux"
    and os.path.exists("/proc/device-tree/model")
    and "raspberry pi" in open("/proc/device-tree/model").read().lower()
    if os.path.exists("/proc/device-tree/model")
    else False
)

# Define package requirements for Raspberry Pi
requirements = ["pydantic>=2.0.0"]
package_name = "pi_tv_remote"


def install_libcec_dependencies():
    """Install the libcec dependencies for Raspberry Pi."""
    # Only run on actual Raspberry Pi hardware
    if not is_raspberry_pi:
        print("Not on Raspberry Pi - skipping system dependency installation")
        return

    try:
        print("\nInstalling libcec dependencies for Raspberry Pi...")
        subprocess.check_call(["sudo", "apt-get", "update"])
        subprocess.check_call(
            [
                "sudo",
                "apt-get",
                "install",
                "-y",
                "libcec6",
                "libcec-dev",
                "python3-cec",
                "build-essential",
                "python3-dev",
                "python3-pip",
            ]
        )
    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies: {e}")
        sys.exit(1)


def install_cec_module():
    """Install the Python CEC module using pip."""
    # Only run on actual Raspberry Pi hardware
    if not is_raspberry_pi:
        print("Not on Raspberry Pi - skipping CEC module installation")
        return

    try:
        # For Raspberry Pi, use system-provided python3-cec instead of pip package
        print("\nUsing system-provided python3-cec for Raspberry Pi")
        # No need to install the cec module since we installed python3-cec via apt
    except subprocess.CalledProcessError as e:
        print(f"Error installing CEC module: {e}")
        sys.exit(1)


class PreInstallCommand(Command):
    """Pre-install command to install libcec and cec module."""

    description = "Install libcec and cec module dependencies"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        install_libcec_dependencies()
        install_cec_module()


class CustomInstall(install):
    """Custom install command to install dependencies first."""

    def run(self):
        self.run_command("preinstall")
        install.run(self)


class CustomDevelop(develop):
    """Custom develop command to install dependencies first."""

    def run(self):
        self.run_command("preinstall")
        develop.run(self)


# Create the setup configuration
setup(
    name=package_name,
    version="0.1.0",
    description="CEC Adapter for Raspberry Pi - Requires HDMI-CEC hardware",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/pi_tv_remote",
    packages=find_packages(),
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest",
            "mypy",
            "black",
            "isort",
        ],
    },
    cmdclass={
        "preinstall": PreInstallCommand,
        "install": CustomInstall,
        "develop": CustomDevelop,
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries",
        "Topic :: Home Automation",
        "Environment :: Console",
        "Operating System :: POSIX :: Linux",
        "Intended Audience :: End Users/Desktop",
    ],
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "pi_tv_remote=pi_tv_remote:main",
        ],
    },
)
