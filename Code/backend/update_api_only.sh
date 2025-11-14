#!/bin/bash
# Quick update script - only updates api.py on ESP8266
# Usage: ./update_api_only.sh [port]

PORT=${1:-/dev/ttyUSB0}
DIST_DIR="/home/pi/Desktop/Feeder/Code/backend/dist"

echo "========================================"
echo "Updating api.py on ESP8266"
echo "========================================"
echo "Port: $PORT"
echo ""

# Check if port exists
if [ ! -e "$PORT" ]; then
    echo "❌ Error: Port $PORT not found!"
    exit 1
fi

# Check if ampy is installed
if ! command -v ampy &> /dev/null; then
    echo "❌ Error: ampy not installed!"
    echo "Install with: pip3 install adafruit-ampy"
    exit 1
fi

cd "$DIST_DIR" || exit 1

echo "📦 Uploading updated api.py..."
ampy -p "$PORT" -b 115200 put api.py && echo "  ✅ api.py updated successfully!"

echo ""
echo "✅ Update complete!"
echo ""
echo "Next steps:"
echo "1. Reset your ESP8266 (press reset button or power cycle)"
echo "2. Or connect to serial and press Ctrl+D: screen $PORT 115200"
echo ""
