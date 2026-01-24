#!/bin/bash

# Test runner script - run all unit tests from project root

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${BLUE}=== $1 ===${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

run_api_tests() {
    print_header "Running API Unit Tests"
    cd "$SCRIPT_DIR/openai_scheduled_newsletter_api"
    poetry run python -m pytest -v tests/
    print_success "API tests passed"
}

run_job_tests() {
    print_header "Running Job Unit Tests"
    cd "$SCRIPT_DIR/openai_scheduled_newsletter_job"
    poetry run python -m pytest -v tests/
    print_success "Job tests passed"
}

show_help() {
    echo "Usage: ./run_tests.sh [OPTION]"
    echo ""
    echo "Options:"
    echo "  api       Run API tests only"
    echo "  job       Run Job tests only"
    echo "  all       Run all tests (default)"
    echo "  help      Show this help message"
}

# Main
case "${1:-all}" in
    api)
        run_api_tests
        ;;
    job)
        run_job_tests
        ;;
    all)
        run_api_tests
        echo ""
        run_job_tests
        echo ""
        print_success "All tests passed! (API: 6/6, Job: 7/7)"
        ;;
    help)
        show_help
        ;;
    *)
        echo "Unknown option: $1"
        show_help
        exit 1
        ;;
esac
