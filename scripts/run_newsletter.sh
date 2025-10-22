#!/usr/bin/env bash

# Find the correct python executable
PYTHON=$(which python3 || which python)

# Run main.py with --run-now option
exec "$PYTHON" -m deepseek_daily_newsletter.main --run-now
