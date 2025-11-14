# ESP8266 Deployment Guide - Memory Optimized Version

## Prerequisites
- ESP8266 flashed with MicroPython 1.26.1
- USB connection to Raspberry Pi (/dev/ttyUSB0)
- Build completed: `bash build_backend.sh`

## Option 1: Deploy Using rshell (Recommended)

### Step 1: Connect to ESP8266
```bash
rshell -p /dev/ttyUSB0 --buffer-size=512
```

### Step 2: Upload Core Files
```bash
# From rshell prompt
cp /home/pi/Desktop/Feeder/Code/backend/dist/boot.py /pyboard/boot.py
cp /home/pi/Desktop/Feeder/Code/backend/dist/main.py /pyboard/main.py
cp /home/pi/Desktop/Feeder/Code/backend/dist/api.py /pyboard/api.py
cp /home/pi/Desktop/Feeder/Code/backend/dist/config.py /pyboard/config.py
cp /home/pi/Desktop/Feeder/Code/backend/dist/wifi_manager.py /pyboard/wifi_manager.py
```

### Step 3: Upload Service Modules
```bash
cp /home/pi/Desktop/Feeder/Code/backend/dist/services.py /pyboard/services.py
cp /home/pi/Desktop/Feeder/Code/backend/dist/last_fed_service.py /pyboard/last_fed_service.py
cp /home/pi/Desktop/Feeder/Code/backend/dist/next_feed_service.py /pyboard/next_feed_service.py
cp /home/pi/Desktop/Feeder/Code/backend/dist/quantity_service.py /pyboard/quantity_service.py
```

### Step 4: Create and Upload lib Directory
```bash
mkdir /pyboard/lib
cp /home/pi/Desktop/Feeder/Code/backend/dist/lib/stepper.py /pyboard/lib/stepper.py
cp /home/pi/Desktop/Feeder/Code/backend/dist/lib/rtc_handler.py /pyboard/lib/rtc_handler.py
cp /home/pi/Desktop/Feeder/Code/backend/dist/lib/notification.py /pyboard/lib/notification.py
```

### Step 5: Create and Upload data Directory
```bash
mkdir /pyboard/data
cp /home/pi/Desktop/Feeder/Code/backend/dist/data/quantity.txt /pyboard/data/quantity.txt
cp /home/pi/Desktop/Feeder/Code/backend/dist/data/last_fed.txt /pyboard/data/last_fed.txt
cp /home/pi/Desktop/Feeder/Code/backend/dist/data/next_feed.txt /pyboard/data/next_feed.txt
cp /home/pi/Desktop/Feeder/Code/backend/dist/data/schedule.txt /pyboard/data/schedule.txt
```

### Step 6: Upload UI Directory
```bash
mkdir /pyboard/UI
mkdir /pyboard/UI/css
mkdir /pyboard/UI/assets
mkdir /pyboard/UI/assets/images

# HTML files
cp /home/pi/Desktop/Feeder/Code/backend/dist/UI/index.html /pyboard/UI/index.html
cp /home/pi/Desktop/Feeder/Code/backend/dist/UI/feednow.html /pyboard/UI/feednow.html
cp /home/pi/Desktop/Feeder/Code/backend/dist/UI/setquantity.html /pyboard/UI/setquantity.html
cp /home/pi/Desktop/Feeder/Code/backend/dist/UI/setschedule.html /pyboard/UI/setschedule.html

# CSS
cp /home/pi/Desktop/Feeder/Code/backend/dist/UI/css/styles.css /pyboard/UI/css/styles.css

# Assets
cp /home/pi/Desktop/Feeder/Code/backend/dist/UI/assets/images/Header.png /pyboard/UI/assets/images/Header.png
```

### Step 7: Reboot ESP8266
```bash
repl
# Press Ctrl+D to soft reboot
```

## Option 2: Deploy Using ampy

### Install ampy
```bash
pip3 install adafruit-ampy
```

### Upload Files
```bash
cd /home/pi/Desktop/Feeder/Code/backend/dist

# Core files
ampy -p /dev/ttyUSB0 -b 115200 put boot.py
ampy -p /dev/ttyUSB0 -b 115200 put main.py
ampy -p /dev/ttyUSB0 -b 115200 put api.py
ampy -p /dev/ttyUSB0 -b 115200 put config.py
ampy -p /dev/ttyUSB0 -b 115200 put wifi_manager.py

# Service modules
ampy -p /dev/ttyUSB0 -b 115200 put services.py
ampy -p /dev/ttyUSB0 -b 115200 put last_fed_service.py
ampy -p /dev/ttyUSB0 -b 115200 put next_feed_service.py
ampy -p /dev/ttyUSB0 -b 115200 put quantity_service.py

# lib directory
ampy -p /dev/ttyUSB0 -b 115200 mkdir lib
ampy -p /dev/ttyUSB0 -b 115200 put lib/stepper.py lib/stepper.py
ampy -p /dev/ttyUSB0 -b 115200 put lib/rtc_handler.py lib/rtc_handler.py
ampy -p /dev/ttyUSB0 -b 115200 put lib/notification.py lib/notification.py

# data directory
ampy -p /dev/ttyUSB0 -b 115200 mkdir data
ampy -p /dev/ttyUSB0 -b 115200 put data/quantity.txt data/quantity.txt
ampy -p /dev/ttyUSB0 -b 115200 put data/last_fed.txt data/last_fed.txt
ampy -p /dev/ttyUSB0 -b 115200 put data/next_feed.txt data/next_feed.txt
ampy -p /dev/ttyUSB0 -b 115200 put data/schedule.txt data/schedule.txt

# UI directory (this will take time)
ampy -p /dev/ttyUSB0 -b 115200 mkdir UI
ampy -p /dev/ttyUSB0 -b 115200 mkdir UI/css
ampy -p /dev/ttyUSB0 -b 115200 mkdir UI/assets
ampy -p /dev/ttyUSB0 -b 115200 mkdir UI/assets/images
ampy -p /dev/ttyUSB0 -b 115200 put UI/index.html UI/index.html
ampy -p /dev/ttyUSB0 -b 115200 put UI/feednow.html UI/feednow.html
ampy -p /dev/ttyUSB0 -b 115200 put UI/setquantity.html UI/setquantity.html
ampy -p /dev/ttyUSB0 -b 115200 put UI/setschedule.html UI/setschedule.html
ampy -p /dev/ttyUSB0 -b 115200 put UI/css/styles.css UI/css/styles.css
ampy -p /dev/ttyUSB0 -b 115200 put UI/assets/images/Header.png UI/assets/images/Header.png
```

## Verification

### Check Memory Usage
```bash
rshell -p /dev/ttyUSB0
repl
```

```python
>>> import gc
>>> gc.collect()
>>> gc.mem_free()
# Should show >15KB free after imports
```

### Test API Server
```bash
# Connect to ESP8266's WiFi network (if using WiFiManager)
# Or check your router for ESP8266 IP address

# Test endpoint
curl http://<ESP8266_IP>:5000/api/ping
# Should return: {"status": "ok"}
```

### Monitor Serial Output
```bash
screen /dev/ttyUSB0 115200
# Or use rshell repl
```

Expected output:
```
WiFi connected
IP address: 192.168.x.x
Server running on 0.0.0.0:5000
```

## Troubleshooting

### MemoryError Still Occurs
1. Remove UI directory to save flash space
2. Simplify notification.py (remove non-essential code)
3. Check if firmware is correct (should be ESP8266_GENERIC-20250911-v1.26.1.bin)

### ImportError
- Verify all files uploaded successfully
- Check directory structure matches exactly
- Ensure lib/ and data/ directories exist

### WiFi Connection Issues
- Check config.py WiFi credentials
- ESP8266 only supports 2.4GHz networks
- WiFiManager will create AP "ESP-Feeder" if connection fails

### Server Won't Start
1. Check boot.py and main.py uploaded correctly
2. Verify api.py syntax: `python3 -m py_compile api.py`
3. Monitor serial output for error messages

## File Structure on ESP8266
```
/
├── boot.py
├── main.py
├── api.py
├── config.py
├── wifi_manager.py
├── services.py
├── last_fed_service.py
├── next_feed_service.py
├── quantity_service.py
├── lib/
│   ├── stepper.py
│   ├── rtc_handler.py
│   └── notification.py
├── data/
│   ├── quantity.txt
│   ├── last_fed.txt
│   ├── next_feed.txt
│   └── schedule.txt
└── UI/
    ├── index.html
    ├── feednow.html
    ├── setquantity.html
    ├── setschedule.html
    ├── css/
    │   └── styles.css
    └── assets/
        └── images/
            └── Header.png
```

## Memory Footprint
- **api.py**: 11KB (vs Microdot's 57KB)
- **Total code**: ~30KB
- **UI files**: ~30KB
- **Free RAM after boot**: ~15-20KB
- **No ujson dependency**: Saves 5-10KB
- **Plain text data**: No JSON parsing overhead

## API Endpoints Available
- `GET /` - Serve index.html
- `GET /api/ping` - Health check
- `GET /api/home` - Dashboard data
- `POST /api/feednow` - Manual feeding
- `GET /api/quantity` - Get remaining feed
- `POST /api/quantity` - Update quantity
- `GET /api/schedule` - Get schedule
- `POST /api/schedule` - Update schedule
- `GET /api/lastfed` - Get last feed time
- `POST /api/lastfed` - Update last feed time
- Static files from `/UI/*`
