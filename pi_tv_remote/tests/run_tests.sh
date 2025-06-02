#!/bin/bash
# Script to run CEC adapter tests with different options

# Set colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color
BOLD='\033[1m'
NORMAL='\033[0m'

# Default settings
SKIP_STANDBY=0
NO_TV=0
DEBUG=0
VERBOSE=0
TESTS_DIR="$(dirname "$(readlink -f "$0")")"
PROJECT_DIR="$(dirname "$TESTS_DIR")"

# Function to print usage
print_usage() {
    echo -e "\n${BOLD}Usage:${NORMAL} $0 [options]"
    echo
    echo "Options:"
    echo "  --skip-standby    Skip tests that put the TV in standby mode"
    echo "  --no-tv           Skip all real TV tests (when no TV is connected)"
    echo "  --debug           Run with debug output enabled"
    echo "  --verbose, -v     Run with verbose output"
    echo "  --help, -h        Show this help message"
    echo
    echo "Examples:"
    echo "  $0                           Run all tests"
    echo "  $0 --skip-standby            Skip standby tests"
    echo "  $0 --no-tv                   Skip all real TV tests"
    echo "  $0 --debug                   Run with debug output"
    echo "  $0 --verbose                 Run with verbose output"
    echo
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
    --skip-standby)
        SKIP_STANDBY=1
        shift
        ;;
    --no-tv)
        NO_TV=1
        shift
        ;;
    --debug)
        DEBUG=1
        shift
        ;;
    --verbose | -v)
        VERBOSE=1
        shift
        ;;
    --help | -h)
        print_usage
        exit 0
        ;;
    *)
        echo -e "${RED}ERROR: Unknown option: $1${NC}"
        print_usage
        exit 1
        ;;
    esac
done

# Build command with options
COMMAND="python -m pytest"

if [ $VERBOSE -eq 1 ]; then
    COMMAND="$COMMAND -v"
fi

if [ $DEBUG -eq 1 ]; then
    COMMAND="$COMMAND -vxs"
fi

if [ $SKIP_STANDBY -eq 1 ]; then
    COMMAND="$COMMAND --skip-standby"
fi

# Add the test directory
COMMAND="$COMMAND $TESTS_DIR"

# Print header
echo -e "\n${GREEN}${BOLD}===================================================${NC}"
echo -e "${GREEN}${BOLD}             Pi TV Remote - Test Runner            ${NC}"
echo -e "${GREEN}${BOLD}===================================================${NC}\n"

# Show settings
echo -e "${BOLD}Test Settings:${NORMAL}"
echo -e "  Test Directory: ${YELLOW}$TESTS_DIR${NC}"
echo -e "  Skip Standby Tests: ${YELLOW}$([ $SKIP_STANDBY -eq 1 ] && echo "Yes" || echo "No")${NC}"
echo -e "  Skip Real TV Tests: ${YELLOW}$([ $NO_TV -eq 1 ] && echo "Yes" || echo "No")${NC}"
echo -e "  Debug Mode: ${YELLOW}$([ $DEBUG -eq 1 ] && echo "Yes" || echo "No")${NC}"
echo -e "  Verbose Output: ${YELLOW}$([ $VERBOSE -eq 1 ] && echo "Yes" || echo "No")${NC}"
echo

# Run tests
echo -e "${BOLD}Running Command:${NORMAL} ${YELLOW}$COMMAND${NC}\n"

if [ $NO_TV -eq 1 ]; then
    export NO_TV=1
    echo -e "${YELLOW}Note: All real TV tests will be skipped.${NC}\n"
fi

# Execute the command
eval $COMMAND

# Print summary
echo -e "\n${GREEN}${BOLD}===================================================${NC}"
echo -e "${GREEN}${BOLD}                    Test Complete                  ${NC}"
echo -e "${GREEN}${BOLD}===================================================${NC}\n"
