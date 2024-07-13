#!/bin/bash

# This script runs docker compose up --build from the docker directory.
# It accepts space-separated environment variables as arguments.
#
# Usage examples:
# ./buildAndUp.sh
# ./buildAndUp.sh SYSTEM_SOURCE_PATH=/path/to/source ENABLE_HOT_RELOAD=true
# ./buildAndUp.sh ENABLE_HOT_RELOAD=false

# Change to the docker directory
cd docker || exit

# Check if there are any arguments
if [ $# -eq 0 ]; then
    # If no arguments, run docker compose up --build
    docker compose up --build
else
    # If arguments are provided, set them as environment variables and run docker compose up --build
    env "$@" docker compose up --build
fi