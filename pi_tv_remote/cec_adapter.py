"""
CEC Adapter for Raspberry Pi
- Handles initialization of CEC connection
- Sets up device as Playback or Recording Device
- Processes callbacks for remote control commands
"""

import datetime
import sys
import time
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from pydantic import BaseModel, Field

from .cec_utils import get_cec_module

# Import appropriate CEC module
cec = get_cec_module()
debug_mode = False


# Debug logging function with timestamps
def log_debug(message, level="INFO"):
    """Log a debug message with timestamp"""
    if debug_mode:
        timestamp = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
        print(f"[{timestamp}] [{level}] {message}")


# Define remote button mappings
class RemoteButton:
    """
    Remote button mappings, using the real CEC module's constants when available.
    We maintain our own naming convention for consistency but use the official values.
    """

    # Standard navigation buttons
    SELECT = 0x00  # Will be overridden if cec module has the constant
    UP = 0x01
    DOWN = 0x02
    LEFT = 0x03
    RIGHT = 0x04
    BACK = 0x0D  # EXIT in CEC spec

    # Volume controls
    VOLUME_UP = 0x41
    VOLUME_DOWN = 0x42
    MUTE = 0x43

    # Playback control
    STOP = 0x45
    PLAY = 0x44
    PAUSE = 0x46
    REWIND = 0x48
    FAST_FORWARD = 0x49

    # Color buttons
    BLUE = 0x71
    RED = 0x72
    GREEN = 0x73
    YELLOW = 0x74

    # Number keys
    NUMBER_0 = 0x20
    NUMBER_1 = 0x21
    NUMBER_2 = 0x22
    NUMBER_3 = 0x23
    NUMBER_4 = 0x24
    NUMBER_5 = 0x25
    NUMBER_6 = 0x26
    NUMBER_7 = 0x27
    NUMBER_8 = 0x28
    NUMBER_9 = 0x29

    # Update button codes from the real CEC module
    @classmethod
    def update_from_module(cls, cec_module):
        """Update button codes from the real CEC module."""
        # Map our button names to CEC module constant names
        button_mapping = {
            "SELECT": ["CEC_USER_CONTROL_CODE_SELECT", "CEC_USER_CONTROL_SELECT"],
            "UP": ["CEC_USER_CONTROL_CODE_UP", "CEC_USER_CONTROL_UP"],
            "DOWN": ["CEC_USER_CONTROL_CODE_DOWN", "CEC_USER_CONTROL_DOWN"],
            "LEFT": ["CEC_USER_CONTROL_CODE_LEFT", "CEC_USER_CONTROL_LEFT"],
            "RIGHT": ["CEC_USER_CONTROL_CODE_RIGHT", "CEC_USER_CONTROL_RIGHT"],
            "BACK": [
                "CEC_USER_CONTROL_CODE_EXIT",
                "CEC_USER_CONTROL_EXIT",
                "CEC_USER_CONTROL_BACK",
            ],
            "VOLUME_UP": [
                "CEC_USER_CONTROL_CODE_VOLUME_UP",
                "CEC_USER_CONTROL_VOLUME_UP",
            ],
            "VOLUME_DOWN": [
                "CEC_USER_CONTROL_CODE_VOLUME_DOWN",
                "CEC_USER_CONTROL_VOLUME_DOWN",
            ],
            "MUTE": [
                "CEC_USER_CONTROL_CODE_MUTE",
                "CEC_USER_CONTROL_MUTE",
                "CEC_USER_CONTROL_MUTE_TOGGLE",
            ],
            "PLAY": ["CEC_USER_CONTROL_CODE_PLAY", "CEC_USER_CONTROL_PLAY"],
            "STOP": ["CEC_USER_CONTROL_CODE_STOP", "CEC_USER_CONTROL_STOP"],
            "PAUSE": ["CEC_USER_CONTROL_CODE_PAUSE", "CEC_USER_CONTROL_PAUSE"],
            "REWIND": ["CEC_USER_CONTROL_CODE_REWIND", "CEC_USER_CONTROL_REWIND"],
            "FAST_FORWARD": [
                "CEC_USER_CONTROL_CODE_FAST_FORWARD",
                "CEC_USER_CONTROL_FAST_FORWARD",
            ],
            "BLUE": [
                "CEC_USER_CONTROL_CODE_F1_BLUE",
                "CEC_USER_CONTROL_F1_BLUE",
                "CEC_USER_CONTROL_BLUE",
            ],
            "RED": [
                "CEC_USER_CONTROL_CODE_F2_RED",
                "CEC_USER_CONTROL_F2_RED",
                "CEC_USER_CONTROL_RED",
            ],
            "GREEN": [
                "CEC_USER_CONTROL_CODE_F3_GREEN",
                "CEC_USER_CONTROL_F3_GREEN",
                "CEC_USER_CONTROL_GREEN",
            ],
            "YELLOW": [
                "CEC_USER_CONTROL_CODE_F4_YELLOW",
                "CEC_USER_CONTROL_F4_YELLOW",
                "CEC_USER_CONTROL_YELLOW",
            ],
            # Number keys
            "NUMBER_0": ["CEC_USER_CONTROL_CODE_NUMBER0", "CEC_USER_CONTROL_NUMBER_0"],
            "NUMBER_1": ["CEC_USER_CONTROL_CODE_NUMBER1", "CEC_USER_CONTROL_NUMBER_1"],
            "NUMBER_2": ["CEC_USER_CONTROL_CODE_NUMBER2", "CEC_USER_CONTROL_NUMBER_2"],
            "NUMBER_3": ["CEC_USER_CONTROL_CODE_NUMBER3", "CEC_USER_CONTROL_NUMBER_3"],
            "NUMBER_4": ["CEC_USER_CONTROL_CODE_NUMBER4", "CEC_USER_CONTROL_NUMBER_4"],
            "NUMBER_5": ["CEC_USER_CONTROL_CODE_NUMBER5", "CEC_USER_CONTROL_NUMBER_5"],
            "NUMBER_6": ["CEC_USER_CONTROL_CODE_NUMBER6", "CEC_USER_CONTROL_NUMBER_6"],
            "NUMBER_7": ["CEC_USER_CONTROL_CODE_NUMBER7", "CEC_USER_CONTROL_NUMBER_7"],
            "NUMBER_8": ["CEC_USER_CONTROL_CODE_NUMBER8", "CEC_USER_CONTROL_NUMBER_8"],
            "NUMBER_9": ["CEC_USER_CONTROL_CODE_NUMBER9", "CEC_USER_CONTROL_NUMBER_9"],
        }

        # Try to get each constant from the module
        for our_name, possible_names in button_mapping.items():
            for name in possible_names:
                if hasattr(cec_module, name):
                    setattr(cls, our_name, getattr(cec_module, name))
                    break


class CECCommand:
    """
    CEC command opcodes, using the real CEC module's constants when available.
    This class provides convenient access to common CEC command opcodes.
    """

    # TV power control
    IMAGE_VIEW_ON = 0x04
    STANDBY = 0x36

    # Device status
    GIVE_DEVICE_POWER_STATUS = 0x8F
    REPORT_POWER_STATUS = 0x90

    # Routing control
    ACTIVE_SOURCE = 0x82
    SET_STREAM_PATH = 0x86
    ROUTING_CHANGE = 0x80

    # Device information
    GIVE_PHYSICAL_ADDR = 0x83
    REPORT_PHYSICAL_ADDR = 0x84
    GIVE_OSD_NAME = 0x46
    SET_OSD_NAME = 0x47
    GIVE_DEVICE_VENDOR_ID = 0x8C
    DEVICE_VENDOR_ID = 0x87

    # Deck control
    GIVE_DECK_STATUS = 0x1A
    DECK_STATUS = 0x1B

    # Remote control
    USER_CONTROL_PRESSED = 0x44
    USER_CONTROL_RELEASED = 0x45

    # Vendor specific
    VENDOR_COMMAND = 0x89

    @classmethod
    def update_from_module(cls, cec_module):
        """Update command opcodes from the real CEC module."""
        # Map our command names to CEC module constant names
        command_mapping = {
            "IMAGE_VIEW_ON": ["CEC_OPCODE_IMAGE_VIEW_ON"],
            "STANDBY": ["CEC_OPCODE_STANDBY"],
            "GIVE_DEVICE_POWER_STATUS": ["CEC_OPCODE_GIVE_DEVICE_POWER_STATUS"],
            "REPORT_POWER_STATUS": ["CEC_OPCODE_REPORT_POWER_STATUS"],
            "ACTIVE_SOURCE": ["CEC_OPCODE_ACTIVE_SOURCE"],
            "SET_STREAM_PATH": ["CEC_OPCODE_SET_STREAM_PATH"],
            "ROUTING_CHANGE": ["CEC_OPCODE_ROUTING_CHANGE"],
            "GIVE_PHYSICAL_ADDR": ["CEC_OPCODE_GIVE_PHYSICAL_ADDR"],
            "REPORT_PHYSICAL_ADDR": ["CEC_OPCODE_REPORT_PHYSICAL_ADDR"],
            "GIVE_OSD_NAME": ["CEC_OPCODE_GIVE_OSD_NAME"],
            "SET_OSD_NAME": ["CEC_OPCODE_SET_OSD_NAME"],
            "GIVE_DEVICE_VENDOR_ID": ["CEC_OPCODE_GIVE_DEVICE_VENDOR_ID"],
            "DEVICE_VENDOR_ID": ["CEC_OPCODE_DEVICE_VENDOR_ID"],
            "GIVE_DECK_STATUS": ["CEC_OPCODE_GIVE_DECK_STATUS"],
            "DECK_STATUS": ["CEC_OPCODE_DECK_STATUS"],
            "USER_CONTROL_PRESSED": ["CEC_OPCODE_USER_CONTROL_PRESSED"],
            "USER_CONTROL_RELEASED": ["CEC_OPCODE_USER_CONTROL_RELEASED"],
            "VENDOR_COMMAND": ["CEC_OPCODE_VENDOR_COMMAND"],
        }

        # Try to get each constant from the module
        for our_name, possible_names in command_mapping.items():
            for name in possible_names:
                if hasattr(cec_module, name):
                    setattr(cls, our_name, getattr(cec_module, name))
                    break


class CECConfig(BaseModel):
    """Configuration for the CEC adapter."""

    device_name: str = Field(default="RaspberryPi")
    physical_address: str = Field(default="1.0.0.0")
    port: int = Field(default=1)
    auto_power_on: bool = Field(default=True)
    device_type: int = Field(default=1)  # Default to Recording Device


class CECAdapter:
    """CEC Adapter wrapper for Raspberry Pi."""

    def __init__(self, config: Optional[CECConfig] = None, debug: bool = False):
        """
        Initialize the CEC adapter.

        Args:
            config: Configuration for the CEC adapter
            debug: If True, skip actual CEC operations for testing
        """
        self.config = config or CECConfig()
        self.initialized = False
        self.callbacks: Dict[int, List[Callable]] = {}
        self.command_callbacks: Dict[int, List[Callable]] = {}

        global debug_mode
        debug_mode = debug

        log_debug("Running in DEBUG mode - CEC operations will be simulated", "WARNING")

        # Import CEC module
        global cec
        cec = get_cec_module()

        # Update RemoteButton class with constants from the real cec module
        RemoteButton.update_from_module(cec)

        # Update CECCommand class with constants from the real cec module
        CECCommand.update_from_module(cec)

    def init(self) -> bool:
        """
        Initialize the CEC connection using the simplest approach.
        Based on successful tests with python-cec.
        """
        log_debug("Starting CEC initialization", "DEBUG")
        start_time = time.time()

        try:
            # Simple initialization with default adapter - this is the key simplification
            log_debug("Initializing CEC with default adapter", "DEBUG")
            cec.init()
            log_debug("CEC initialization successful", "SUCCESS")

            # Register events if needed
            self.register_event_handlers()

            self.initialized = True
            log_debug(
                f"Total initialization time: {time.time() - start_time:.2f} seconds",
                "DEBUG",
            )
            return True

        except Exception as e:
            log_debug(f"Error initializing CEC: {e}", "ERROR")
            return False

    def cleanup(self) -> None:
        """Clean up CEC resources."""
        if not self.initialized:
            return

        log_debug("Cleaning up CEC resources", "DEBUG")

        # Unregister event handlers
        self.unregister_event_handlers()

        # Try to close the connection if that function exists
        try:
            if hasattr(cec, "close"):
                cec.close()
                log_debug("CEC connection closed via close()", "DEBUG")
            elif hasattr(cec, "shutdown"):
                cec.shutdown()
                log_debug("CEC connection closed via shutdown()", "DEBUG")
            else:
                log_debug("No cleanup function available (close/shutdown)", "WARNING")
        except Exception as e:
            log_debug(f"Error during CEC cleanup: {e}", "ERROR")

            self.initialized = False

    def add_button_callback(self, button_code: int, callback: Callable) -> None:
        """Add a callback for a specific remote button press."""
        if button_code not in self.callbacks:
            self.callbacks[button_code] = []
        self.callbacks[button_code].append(callback)

    def remove_button_callback(self, button_code: int, callback: Callable) -> None:
        """Remove a callback for a specific remote button press."""
        if button_code in self.callbacks and callback in self.callbacks[button_code]:
            self.callbacks[button_code].remove(callback)

    def add_command_callback(self, opcode: int, callback: Callable) -> None:
        """
        Add a callback for a specific CEC command.

        Args:
            opcode: The CEC command opcode
            callback: Function to call when the command is received
        """
        if opcode not in self.command_callbacks:
            self.command_callbacks[opcode] = []
        self.command_callbacks[opcode].append(callback)

    def remove_command_callback(self, opcode: int, callback: Callable) -> None:
        """
        Remove a callback for a specific CEC command.

        Args:
            opcode: The CEC command opcode
            callback: The callback function to remove
        """
        if (
            opcode in self.command_callbacks
            and callback in self.command_callbacks[opcode]
        ):
            self.command_callbacks[opcode].remove(callback)

    def handle_keypress(self, key_code: int, duration: int) -> None:
        """
        Handle a keypress event from CEC.

        Args:
            key_code: The key code that was pressed
            duration: How long the key was pressed
        """
        log_debug(
            f"Received key: {key_code} (0x{key_code:02x}) duration: {duration}", "DEBUG"
        )

        # First check for exact matches
        if key_code in self.callbacks:
            for callback in self.callbacks[key_code]:
                try:
                    callback(key_code, duration)
                except Exception as e:
                    log_debug(f"Error in button callback: {e}", "ERROR")

        # For debugging
        button_names = {
            RemoteButton.SELECT: "SELECT",
            RemoteButton.UP: "UP",
            RemoteButton.DOWN: "DOWN",
            RemoteButton.LEFT: "LEFT",
            RemoteButton.RIGHT: "RIGHT",
            RemoteButton.BACK: "BACK",
            RemoteButton.VOLUME_UP: "VOLUME_UP",
            RemoteButton.VOLUME_DOWN: "VOLUME_DOWN",
            RemoteButton.MUTE: "MUTE",
            RemoteButton.PLAY: "PLAY",
            RemoteButton.PAUSE: "PAUSE",
            RemoteButton.STOP: "STOP",
            RemoteButton.REWIND: "REWIND",
            RemoteButton.FAST_FORWARD: "FAST_FORWARD",
            RemoteButton.RED: "RED",
            RemoteButton.GREEN: "GREEN",
            RemoteButton.YELLOW: "YELLOW",
            RemoteButton.BLUE: "BLUE",
        }

        button_name = button_names.get(key_code, f"UNKNOWN (0x{key_code:02x})")
        log_debug(f"Remote button: {button_name}", "INFO")

    def handle_command(self, cmd, *args) -> None:
        """
        Handle a CEC command.

        Args:
            cmd: The command
            *args: Additional arguments for the command
        """
        log_debug(f"Received command: {cmd} args: {args}", "DEBUG")

        try:
            # Determine opcode and parameters based on command format
            opcode = None
            params = None

            if hasattr(cmd, "opcode"):
                # New format: cmd has opcode and parameters attributes
                opcode = cmd.opcode
                params = getattr(cmd, "parameters", None)
            elif len(args) >= 3:
                # Old format: args contain source, dest, opcode, params
                opcode = args[2]
                params = args[3] if len(args) > 3 else None
            else:
                log_debug(f"Unknown command format: {cmd} {args}", "WARNING")
                return

            # Call matching command callbacks
            if opcode in self.command_callbacks:
                for callback in self.command_callbacks[opcode]:
                    try:
                        callback(cmd, *args)
                    except Exception as e:
                        log_debug(f"Error in command callback: {e}", "ERROR")

        except Exception as e:
            log_debug(f"Error handling command: {e}", "ERROR")

    def register_event_handlers(self) -> None:
        """Register CEC event handlers."""
        if hasattr(cec, "add_callback"):
            # Register for key press events
            cec.add_callback(self.handle_keypress, cec.EVENT_KEYPRESS)
            # Register for command events
            cec.add_callback(self.handle_command, cec.EVENT_COMMAND)
            log_debug("CEC event handlers registered", "DEBUG")

    def unregister_event_handlers(self) -> None:
        """Unregister CEC event handlers."""
        if hasattr(cec, "remove_callback"):
            # Unregister key press events
            cec.remove_callback(self.handle_keypress, cec.EVENT_KEYPRESS)
            # Unregister command events
            cec.remove_callback(self.handle_command, cec.EVENT_COMMAND)
            log_debug("CEC event handlers unregistered", "DEBUG")

    def send_command(
        self,
        opcode: int,
        destination: int = 0,
        parameters: bytes = b"",
        timeout: float = 2.0,
    ) -> bool:
        """
        Send a CEC command with timeout protection.

        Args:
            opcode: Command opcode
            destination: Destination logical address (defaults to TV)
            parameters: Command parameters
            timeout: Timeout in seconds

        Returns:
            True if command sent successfully, False otherwise
        """
        if not self.initialized:
            log_debug("CEC not initialized, cannot send command", "ERROR")
            return False

        log_debug(
            f"Sending command {opcode} (0x{opcode:02x}) to {destination} "
            f"with params: {parameters.hex() if parameters else 'none'}",
            "DEBUG",
        )

        try:
            # Use direct transmit for simplicity and reliability
            cec.transmit(destination, opcode, parameters)
            return True
        except Exception as e:
            log_debug(f"Error sending command: {e}", "ERROR")
            return False

    def power_on_tv(self) -> bool:
        """Turn on the TV."""
        log_debug("Sending POWER ON to TV", "INFO")
        return self.send_command(CECCommand.IMAGE_VIEW_ON)

    def standby_tv(self) -> bool:
        """Put the TV in standby mode."""
        log_debug("Sending STANDBY to TV", "INFO")
        return self.send_command(CECCommand.STANDBY)

    def set_active_source(self) -> bool:
        """Set this device as the active source."""
        log_debug("Setting device as active source", "INFO")

        try:
            # Try the simple approach first
            if hasattr(cec, "set_active_source"):
                success = cec.set_active_source()
                if success:
                    return True

            # Fall back to manual implementation
            phys_addr = bytes.fromhex(self.config.physical_address.replace(".", ""))
            return self.send_command(
                CECCommand.ACTIVE_SOURCE,
                cec.CECDEVICE_BROADCAST,
                phys_addr,
            )
        except Exception as e:
            log_debug(f"Error setting active source: {e}", "ERROR")
            return False

    def send_remote_button(
        self, button_code: int, pressed: bool = True, hold_time: float = 0.2
    ) -> bool:
        """
        Send a remote control button press or release.

        Args:
            button_code: The button code to send
            pressed: True to send button press, False to send release
            hold_time: Time to hold button before sending release (if pressed is True)

        Returns:
            True if successful, False otherwise
        """
        if not self.initialized:
            log_debug("CEC not initialized, cannot send remote button", "ERROR")
            return False

        # Button press
        if pressed:
            opcode = CECCommand.USER_CONTROL_PRESSED
            log_debug(
                f"Sending BUTTON PRESS: {button_code} (0x{button_code:02x})", "INFO"
            )
            result = self.send_command(opcode, cec.CECDEVICE_TV, bytes([button_code]))

            if not result:
                return False

            # If hold time is specified, wait and then send release
            if hold_time > 0:
                time.sleep(hold_time)
                return self.send_remote_button(button_code, False)

            return True

        # Button release
        else:
            opcode = CECCommand.USER_CONTROL_RELEASED
            log_debug(
                f"Sending BUTTON RELEASE: {button_code} (0x{button_code:02x})", "INFO"
            )
            return self.send_command(opcode, cec.CECDEVICE_TV)

    def request_power_status(self) -> bool:
        """
        Request power status from the TV.

        Returns:
            True if request sent successfully, False otherwise
        """
        log_debug("Requesting power status from TV", "INFO")
        return self.send_command(CECCommand.GIVE_DEVICE_POWER_STATUS)

    def request_vendor_id(self) -> bool:
        """
        Request vendor ID from the TV.

        Returns:
            True if request sent successfully, False otherwise
        """
        log_debug("Requesting vendor ID from TV", "INFO")
        return self.send_command(CECCommand.GIVE_DEVICE_VENDOR_ID)

    def run(self, max_duration: Optional[float] = None) -> None:
        """
        Run the adapter indefinitely or for a specified duration, waiting for CEC events.
        This method will block until interrupted with KeyboardInterrupt or the duration expires.

        Args:
            max_duration: Maximum time to run in seconds, or None to run indefinitely
        """
        if not self.initialized:
            log_debug("CEC not initialized, cannot run event loop", "ERROR")
            return

        log_debug("Starting CEC event loop...", "INFO")
        start_time = time.time()

        try:
            # Loop until interrupted or duration exceeded
            while True:
                # Check if we've exceeded max duration
                if (
                    max_duration is not None
                    and time.time() - start_time >= max_duration
                ):
                    log_debug(
                        f"CEC event loop reached maximum duration of {max_duration} seconds",
                        "INFO",
                    )
                    break

                # Sleep to prevent CPU hogging
                time.sleep(0.1)
        except KeyboardInterrupt:
            log_debug("CEC event loop interrupted by user", "INFO")
        except Exception as e:
            log_debug(f"Error in CEC event loop: {e}", "ERROR")
        finally:
            log_debug("CEC event loop ended", "DEBUG")

    def __del__(self):
        """Destructor to ensure resources are cleaned up."""
        self.cleanup()
