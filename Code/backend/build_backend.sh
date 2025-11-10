#!/bin/bash
# Fish Feeder Backend Build Script (Bash)
# Usage: ./build_backend.sh [api|battery]

MODE=${1:-api}

echo -e "\n=== Fish Feeder Backend Build Script ===\n"

# Step 1: Download MicroPython dependencies
echo "Step 1: Downloading MicroPython dependencies..."
npm run download:deps

# Step 2: Build dist folder for selected mode
echo -e "\nStep 2: Building dist folder for mode: $MODE..."
if [ "$MODE" = "battery" ]; then
    npm run build:battery
else
    npm run build:api
fi

# Step 3: Show dist folder contents
echo -e "\nStep 3: Listing dist folder contents..."
ls -lR ./dist

echo -e "\n=== Build Complete! ===\n"
echo "Deploy files from the dist folder to your ESP32 using ampy or mpremote."
echo "See dist/README.md for upload instructions.\n"
