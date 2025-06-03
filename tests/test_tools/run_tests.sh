#!/bin/bash
# Run pytest tests for PiTVRemote on Raspberry Pi
# Usage: ./run_tests.sh [options]

# Parse options
SKIP_STANDBY=""
DEBUG=""
# Set fixed timeout duration
TIMEOUT_DURATION=10

for arg in "$@"; do
    case $arg in
    --skip-standby)
        SKIP_STANDBY="-m 'not standby'"
        ;;
    --debug)
        DEBUG="-v"
        ;;
    -h | --help)
        echo "Usage: $0 [options]"
        echo "Options:"
        echo "  --skip-standby        Skip tests that put the TV in standby mode"
        echo "  --debug               Run with more verbose output"
        echo "  -h, --help            Show this help message"
        exit 0
        ;;
    esac
done

echo "=== Running PiTVRemote Tests ==="

# Determine current directory and test directory
CURRENT_DIR=$(pwd)
SCRIPT_DIR=$(dirname "$(readlink -f "$0")")
TEST_DIR=$(dirname "$SCRIPT_DIR")
PROJECT_ROOT=$(dirname "$TEST_DIR")

# Kill any existing test processes
pkill -f "python.*test_" || true
pkill -f "pytest" || true

# Change to test directory if not already there
if [[ "$CURRENT_DIR" != *"tests"* ]]; then
    cd "$TEST_DIR"
    echo "Changed to directory: $(pwd)"
fi

# Check if running remote listener test
if [[ "$@" == *"test_remote_listener.py"* ]] || [[ -z "$1" ]]; then
    echo "Running remote listener test with timeout..."
    echo "Running with remote hardware (will time out after ${TIMEOUT_DURATION}s)..."

    # Set up command with appropriate arguments
    CMD="python -m pytest $DEBUG test_remote_listener.py -xvs"
    echo "Command: $CMD"

    timeout --foreground ${TIMEOUT_DURATION}s $CMD

    # Force kill any hanging processes
    pkill -f "python.*test_remote_listener.py" || true
    echo "Remote listener test completed"
fi

# Run the TV adapter tests with pytest
TEST_FILE="test_cec_adapter_real_tv.py"

# Always run tests individually for better reliability
echo "Running tests individually for better reliability..."

# Define all test functions in the correct order
TEST_FUNCTIONS=(
    "test_cec_initialization"
    "test_power_on_tv"
    "test_set_active_source"
    "test_volume_control"
    "test_send_command"
    "test_remote_button_press"
)

# Add standby test if not skipped
if [ -z "$SKIP_STANDBY" ]; then
    TEST_FUNCTIONS+=("test_standby_tv")
fi

# Run each test with a timeout
for test_func in "${TEST_FUNCTIONS[@]}"; do
    echo ""
    echo "Running test: $test_func..."

    # Run with timeout to prevent hanging
    timeout --foreground ${TIMEOUT_DURATION}s python -m pytest $DEBUG "${TEST_FILE}::${test_func}" -xvs

    # Capture exit code
    result=$?
    if [ $result -eq 124 ]; then
        echo "⚠️ Test $test_func timed out after ${TIMEOUT_DURATION} seconds"
    elif [ $result -ne 0 ]; then
        echo "❌ Test $test_func failed with exit code $result"
    else
        echo "✅ Test $test_func passed"
    fi

    # Short pause between tests
    sleep 1
done

python -m pytest $DEBUG $SKIP_STANDBY test_remote_listener.py -xvs

# Print summary
echo ""
echo "=== Test Run Complete ==="
