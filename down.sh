#!/bin/bash

# This script runs docker compose down from the docker directory.
# Change to the docker directory
cd docker || exit

# Check if there are any arguments
if [ $# -eq 0 ]; then
    # If no arguments, run docker compose down
    docker compose down
else
    # If arguments are provided, set them as environment variables and run docker compose down
    env "$@" docker compose down
fi

echo "Docker containers have been stopped and removed."