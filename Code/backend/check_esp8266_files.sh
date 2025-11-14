#!/bin/bash
# Check what files exist on ESP8266
# Usage: ./check_esp8266_files.sh [port]

PORT=${1:-/dev/ttyUSB0}

echo "========================================"
echo "ESP8266 File System Check"
echo "========================================"
echo "Port: $PORT"
echo ""

if ! command -v ampy &> /dev/null; then
    echo "❌ Error: ampy not installed!"
    exit 1
fi

echo "📁 Listing root directory..."
ampy -p "$PORT" -b 115200 ls /

echo -e "\n📁 Checking if UI directory exists..."
ampy -p "$PORT" -b 115200 ls /UI 2>&1 || echo "❌ UI directory not found!"

echo -e "\n📁 Checking if data directory exists..."
ampy -p "$PORT" -b 115200 ls /data 2>&1 || echo "❌ data directory not found!"

echo -e "\n📁 Checking if lib directory exists..."
ampy -p "$PORT" -b 115200 ls /lib 2>&1 || echo "❌ lib directory not found!"

echo -e "\n✅ File system check complete!"
