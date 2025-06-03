#!/bin/bash
# Deploy and test CEC adapter code on a Raspberry Pi
# Usage: ./deploy_and_test_on_pi.sh [pi_hostname] [options]

# Default Raspberry Pi hostname/IP
PI_HOST=${1:-"pi.local"}
shift # Remove the first argument (hostname)

# Default SSH user
PI_USER="raspy"

# Default remote directory
REMOTE_DIR="/home/$PI_USER/Apps/"

# Virtual environment path
VENV_DIR="$REMOTE_DIR/venv"

# Print usage
function print_usage {
    echo "Usage: $0 [pi_hostname] [options]"
    echo "Options:"
    echo "  --skip-standby   Skip tests that put the TV in standby mode"
    echo "  --debug          Run with more verbose output"
    echo "  --install-deps   Install required dependencies on the Pi first"
    echo "  --no-individual  Disable individual test mode"
    echo "  --max-duration=  Set the maximum duration for tests"
    echo "  -h, --help       Show this help message"
    echo ""
    echo "Example:"
    echo "  $0 pi.local --install-deps"
    echo "  $0 192.168.1.100 --skip-standby"
}

# Parse options
SKIP_STANDBY=""
DEBUG=""
INSTALL_DEPS=""
INDIVIDUAL="--individual" # Use individual test mode by default for reliability
MAX_DURATION=10

for arg in "$@"; do
    case $arg in
    --skip-standby)
        SKIP_STANDBY="--skip-standby"
        ;;
    --debug)
        DEBUG="--debug"
        ;;
    --install-deps)
        INSTALL_DEPS="yes"
        ;;
    --no-individual)
        INDIVIDUAL=""
        ;;
    --max-duration=*)
        MAX_DURATION="${arg#*=}"
        ;;
    -h | --help)
        print_usage
        exit 0
        ;;
    esac
done

echo "=== Deploying to Raspberry Pi ($PI_HOST) ==="

# Check if Pi is reachable
echo "Checking if Raspberry Pi is reachable..."
if ! ping -c 1 $PI_HOST &>/dev/null; then
    echo "Error: Cannot reach $PI_HOST"
    echo "Please check your network connection and hostname/IP."
    exit 1
fi

# Handle existing installation
echo "Setting up remote directory..."
ssh $PI_USER@$PI_HOST "if [ -d \"$REMOTE_DIR\" ]; then \
    echo 'Removing existing directory...' && \
    rm -rf $REMOTE_DIR; \
fi && \
mkdir -p $REMOTE_DIR"

# Install system dependencies if requested
if [ -n "$INSTALL_DEPS" ]; then
    echo "Installing system dependencies on Raspberry Pi..."
    ssh $PI_USER@$PI_HOST "sudo apt-get update && \
                           sudo apt-get install -y python3-pip python3-dev libcec-dev build-essential python3-venv"
fi

# Set up virtual environment
echo "Setting up virtual environment..."
ssh $PI_USER@$PI_HOST "cd $REMOTE_DIR && \
                        python3 -m venv $VENV_DIR && \
                        source $VENV_DIR/bin/activate && \
                        pip install --upgrade pip && \
                        pip install pytest cec"

# Copy files to Raspberry Pi
echo "Copying files to Raspberry Pi..."
# Create directory structure
ssh $PI_USER@$PI_HOST "mkdir -p $REMOTE_DIR/pi_tv_remote $REMOTE_DIR/tests/test_tools"

# Copy main package files
rsync -avz --exclude="__pycache__" ./pi_tv_remote/ $PI_USER@$PI_HOST:$REMOTE_DIR/pi_tv_remote/

# Copy test files
rsync -avz --exclude="__pycache__" ./tests/ $PI_USER@$PI_HOST:$REMOTE_DIR/tests/

# Copy setup.py
echo "Copying setup.py file..."
rsync -avz setup.py $PI_USER@$PI_HOST:$REMOTE_DIR/

# Copy README.md for setup.py
echo "Copying README.md file..."
rsync -avz README.md $PI_USER@$PI_HOST:$REMOTE_DIR/

# Make scripts executable
ssh $PI_USER@$PI_HOST "chmod +x $REMOTE_DIR/tests/test_tools/run_tests.sh $REMOTE_DIR/tests/test_tools/deploy_and_test_on_pi.sh"

# Install package in development mode within the virtual environment
echo "Installing pi_tv_remote package on Raspberry Pi..."
ssh $PI_USER@$PI_HOST "cd $REMOTE_DIR && \
                       source $VENV_DIR/bin/activate && \
                       pip install -e ."

# Create a launcher script for easy activation
echo "Creating launcher scripts..."
LAUNCHER_SCRIPT="/home/$PI_USER/activate_pitvremote.sh"
ssh $PI_USER@$PI_HOST "echo '#!/bin/bash' > $LAUNCHER_SCRIPT && \
    echo 'cd $REMOTE_DIR' >> $LAUNCHER_SCRIPT && \
    echo 'source $VENV_DIR/bin/activate' >> $LAUNCHER_SCRIPT && \
    echo 'echo \"PiTVRemote environment activated. Run pi_tv_remote to start the application.\"' >> $LAUNCHER_SCRIPT && \
    chmod +x $LAUNCHER_SCRIPT"

# Create a test script launcher
TEST_SCRIPT="/home/$PI_USER/test_pitvremote.sh"
ssh $PI_USER@$PI_HOST "echo '#!/bin/bash' > $TEST_SCRIPT && \
    echo 'cd $REMOTE_DIR/tests/test_tools' >> $TEST_SCRIPT && \
    echo 'source $VENV_DIR/bin/activate' >> $TEST_SCRIPT && \
    echo './run_tests.sh \"\$@\"' >> $TEST_SCRIPT && \
    echo 'deactivate' >> $TEST_SCRIPT && \
    chmod +x $TEST_SCRIPT"

# Run tests using the virtual environment
echo "Running tests on Raspberry Pi in virtual environment..."
TEST_CMD="cd $REMOTE_DIR && source $VENV_DIR/bin/activate && export PYTHONPATH=$REMOTE_DIR/pi_tv_remote && ./tests/test_tools/run_tests.sh"
if [ -n "$SKIP_STANDBY" ]; then
    TEST_CMD="$TEST_CMD --skip-standby"
fi
if [ -n "$DEBUG" ]; then
    TEST_CMD="$TEST_CMD --debug"
fi
if [ -n "$INDIVIDUAL" ]; then
    TEST_CMD="$TEST_CMD $INDIVIDUAL"
fi
if [ -n "$MAX_DURATION" ]; then
    TEST_CMD="$TEST_CMD --max-duration=$MAX_DURATION"
fi

ssh $PI_USER@$PI_HOST "$TEST_CMD"

echo "=== Test Execution Complete ==="
