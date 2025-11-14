#!/bin/bash
# Quick deployment script for ESP8266 Fish Feeder (API Mode)
# Usage: ./deploy_to_esp8266.sh [port]

PORT=${1:-/dev/ttyUSB0}
DIST_DIR="/home/pi/Desktop/Feeder/Code/backend/dist"

echo "========================================"
echo "ESP8266 Fish Feeder Deployment (API Mode)"
echo "========================================"
echo "Port: $PORT"
echo "Source: $DIST_DIR"
echo ""

# Check if port exists
if [ ! -e "$PORT" ]; then
    echo "❌ Error: Port $PORT not found!"
    echo "Available ports:"
    ls -la /dev/ttyUSB* 2>/dev/null || echo "No USB devices found"
    exit 1
fi

# Check if ampy is installed
if ! command -v ampy &> /dev/null; then
    echo "❌ Error: ampy not installed!"
    echo "Install with: pip3 install adafruit-ampy"
    exit 1
fi

cd "$DIST_DIR" || exit 1

echo "📦 Step 1: Uploading core files..."
ampy -p "$PORT" -b 115200 put boot.py && echo "  ✓ boot.py"
ampy -p "$PORT" -b 115200 put main.py && echo "  ✓ main.py"
ampy -p "$PORT" -b 115200 put api.py && echo "  ✓ api.py"
ampy -p "$PORT" -b 115200 put config.py && echo "  ✓ config.py"
ampy -p "$PORT" -b 115200 put wifi_manager.py && echo "  ✓ wifi_manager.py"
ampy -p "$PORT" -b 115200 put wifi.dat && echo "  ✓ wifi.dat"
ampy -p "$PORT" -b 115200 put urequests.py && echo "  ✓ urequests.py"

echo ""
echo "📦 Step 2: Uploading service modules..."
ampy -p "$PORT" -b 115200 put services.py && echo "  ✓ services.py"
ampy -p "$PORT" -b 115200 put last_fed_service.py && echo "  ✓ last_fed_service.py"
ampy -p "$PORT" -b 115200 put next_feed_service.py && echo "  ✓ next_feed_service.py"
ampy -p "$PORT" -b 115200 put quantity_service.py && echo "  ✓ quantity_service.py"

echo ""
echo "📦 Step 3: Creating and uploading lib/ directory..."
ampy -p "$PORT" -b 115200 rmdir lib 2>/dev/null || true
ampy -p "$PORT" -b 115200 mkdir lib
ampy -p "$PORT" -b 115200 put lib/stepper.py lib/stepper.py && echo "  ✓ lib/stepper.py"
ampy -p "$PORT" -b 115200 put lib/rtc_handler.py lib/rtc_handler.py && echo "  ✓ lib/rtc_handler.py"
ampy -p "$PORT" -b 115200 put lib/notification.py lib/notification.py && echo "  ✓ lib/notification.py"

echo ""
echo "📦 Step 4: Creating and uploading data/ directory..."
ampy -p "$PORT" -b 115200 rmdir data 2>/dev/null || true
ampy -p "$PORT" -b 115200 mkdir data
ampy -p "$PORT" -b 115200 put data/quantity.txt data/quantity.txt && echo "  ✓ data/quantity.txt"
ampy -p "$PORT" -b 115200 put data/last_fed.txt data/last_fed.txt && echo "  ✓ data/last_fed.txt"
ampy -p "$PORT" -b 115200 put data/next_feed.txt data/next_feed.txt && echo "  ✓ data/next_feed.txt"
ampy -p "$PORT" -b 115200 put data/schedule.txt data/schedule.txt && echo "  ✓ data/schedule.txt"

echo ""
echo "📦 Step 5: Creating and uploading UI/ directory (this will take time)..."
ampy -p "$PORT" -b 115200 rmdir UI 2>/dev/null || true
ampy -p "$PORT" -b 115200 mkdir UI
ampy -p "$PORT" -b 115200 mkdir UI/css
ampy -p "$PORT" -b 115200 mkdir UI/assets
ampy -p "$PORT" -b 115200 mkdir UI/assets/images

ampy -p "$PORT" -b 115200 put UI/index.html UI/index.html && echo "  ✓ UI/index.html"
ampy -p "$PORT" -b 115200 put UI/feednow.html UI/feednow.html && echo "  ✓ UI/feednow.html"
ampy -p "$PORT" -b 115200 put UI/setquantity.html UI/setquantity.html && echo "  ✓ UI/setquantity.html"
ampy -p "$PORT" -b 115200 put UI/setschedule.html UI/setschedule.html && echo "  ✓ UI/setschedule.html"
ampy -p "$PORT" -b 115200 put UI/css/styles.css UI/css/styles.css && echo "  ✓ UI/css/styles.css"
ampy -p "$PORT" -b 115200 put UI/assets/images/Header.png UI/assets/images/Header.png && echo "  ✓ UI/assets/images/Header.png"

echo ""
echo "✅ Deployment complete!"
echo ""
echo "Next steps:"
echo "1. Connect to serial monitor: screen $PORT 115200"
echo "2. Press Ctrl+D to soft reset the ESP8266"
echo "3. Watch for WiFi connection and server startup messages"
echo "4. Note the IP address displayed"
echo "5. Access the web interface at http://<ESP8266_IP>:5000"
echo ""
echo "To exit screen: Press Ctrl+A then K, then Y to confirm"
