#!/bin/bash

# This script runs docker compose up from the docker directory.
# It accepts space-separated environment variables as arguments.
#
# Usage examples:
# ./up.sh
# ./up.sh SYSTEM_SOURCE_PATH=/path/to/source ENABLE_HOT_RELOAD=true
# ./up.sh ENABLE_HOT_RELOAD=false

# Change to the docker directory
cd docker || exit

# Check if there are any arguments
if [ $# -eq 0 ]; then
    # If no arguments, run docker compose up
    docker compose up
else
    # If arguments are provided, set them as environment variables and run docker compose up
    env "$@" docker compose up
fi