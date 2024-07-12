#!/bin/bash

# Exit on any error
set -e

# Navigate to the BotUI directory
cd "$(dirname "$0")"

# Install dependencies (if needed)
npm install

# Build the production version of BotUI
npm run build

# Create the destination directory if it doesn't exist
mkdir -p ../../web/www/botui

# Copy the built files to the web folder
cp -R dist/* ../../web/www/botui/

# Change permissions to make all files publicly readable
chmod -R a+r ../../web/www/botui/

echo "BotUI has been built and deployed to ../../web/www/botui/"
echo "All files have been set to be publicly readable."