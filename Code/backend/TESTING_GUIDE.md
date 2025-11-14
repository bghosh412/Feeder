# Connection Issues Fixed - Testing Guide

## Problem Solved
The "connection unexpectedly closed" error was caused by:
1. Incorrect socket send methods (sendall vs send for MicroPython)
2. Missing Connection: close header
3. Response not being sent as single packet
4. stdout buffering hiding server logs

## Changes Made
1. **Added platform detection**: Detect MicroPython vs CPython
2. **Fixed send_response()**: Send headers + body as single packet
3. **Added proper error handling**: Better error messages and logging
4. **Added stdout flush**: Server startup message now visible
5. **Improved request parsing**: Better handling of malformed requests

## Testing on Raspberry Pi (Required Before ESP8266 Deployment)

### Step 1: Activate Virtual Environment
```bash
cd /home/pi/Desktop/Feeder
source venv/bin/activate
```

### Step 2: Start Server
```bash
cd Code/backend
python api.py
```

You should see:
```
Server running on 0.0.0.0:5000
```

### Step 3: Test Endpoints (in another terminal)

**Test API:**
```bash
# Ping
curl http://localhost:5000/api/ping
# Expected: {"status": "ok"}

# Home
curl http://localhost:5000/api/home
# Expected: JSON with connectionStatus, feedRemaining, lastFed, batteryStatus, nextFeed

# Quantity
curl http://localhost:5000/api/quantity
# Expected: {"quantity": 13}

# Schedule
curl http://localhost:5000/api/schedule
# Expected: JSON with feeding times and days
```

**Test Static Files:**
```bash
# Index page
curl -I http://localhost:5000/
# Expected: HTTP/1.1 200 OK, Content-Type: text/html

# CSS
curl -I http://localhost:5000/css/styles.css
# Expected: HTTP/1.1 200 OK, Content-Type: text/css

# Image
curl -I http://localhost:5000/assets/images/Header.png
# Expected: HTTP/1.1 200 OK, Content-Type: image/png
```

**Test in Browser:**
```bash
# Open browser (if GUI available)
firefox http://localhost:5000
# Or from another machine on network:
firefox http://<raspberry-pi-ip>:5000
```

### Step 4: Monitor Server Logs
While testing, you should see in the terminal:
```
Connection from ('127.0.0.1', 12345)
Request: GET /api/ping
Connection from ('127.0.0.1', 12346)
Request: GET /
Serving file: UI/index.html
```

## Deploying to ESP8266

### Prerequisites
```bash
# Ensure ESP8266 is connected
ls /dev/ttyUSB0

# Check if port responds
screen /dev/ttyUSB0 115200
# Press Ctrl+A then K to exit
```

### Option 1: Using rshell (Recommended)

```bash
# Activate venv first
cd /home/pi/Desktop/Feeder
source venv/bin/activate

# Connect to ESP8266
rshell -p /dev/ttyUSB0 --buffer-size=512

# From rshell prompt:
# Upload core files
cp /home/pi/Desktop/Feeder/Code/backend/dist/boot.py /pyboard/boot.py
cp /home/pi/Desktop/Feeder/Code/backend/dist/main.py /pyboard/main.py
cp /home/pi/Desktop/Feeder/Code/backend/dist/api.py /pyboard/api.py
cp /home/pi/Desktop/Feeder/Code/backend/dist/config.py /pyboard/config.py
cp /home/pi/Desktop/Feeder/Code/backend/dist/wifi_manager.py /pyboard/wifi_manager.py

# Upload services
cp /home/pi/Desktop/Feeder/Code/backend/dist/services.py /pyboard/services.py
cp /home/pi/Desktop/Feeder/Code/backend/dist/last_fed_service.py /pyboard/last_fed_service.py
cp /home/pi/Desktop/Feeder/Code/backend/dist/next_feed_service.py /pyboard/next_feed_service.py
cp /home/pi/Desktop/Feeder/Code/backend/dist/quantity_service.py /pyboard/quantity_service.py

# Create and upload lib
mkdir /pyboard/lib
cp /home/pi/Desktop/Feeder/Code/backend/dist/lib/stepper.py /pyboard/lib/stepper.py
cp /home/pi/Desktop/Feeder/Code/backend/dist/lib/rtc_handler.py /pyboard/lib/rtc_handler.py
cp /home/pi/Desktop/Feeder/Code/backend/dist/lib/notification.py /pyboard/lib/notification.py

# Create and upload data
mkdir /pyboard/data
cp /home/pi/Desktop/Feeder/Code/backend/dist/data/quantity.txt /pyboard/data/quantity.txt
cp /home/pi/Desktop/Feeder/Code/backend/dist/data/last_fed.txt /pyboard/data/last_fed.txt
cp /home/pi/Desktop/Feeder/Code/backend/dist/data/next_feed.txt /pyboard/data/next_feed.txt
cp /home/pi/Desktop/Feeder/Code/backend/dist/data/schedule.txt /pyboard/data/schedule.txt

# Create and upload UI
mkdir /pyboard/UI
mkdir /pyboard/UI/css
mkdir /pyboard/UI/assets
mkdir /pyboard/UI/assets/images

cp /home/pi/Desktop/Feeder/Code/backend/dist/UI/index.html /pyboard/UI/index.html
cp /home/pi/Desktop/Feeder/Code/backend/dist/UI/feednow.html /pyboard/UI/feednow.html
cp /home/pi/Desktop/Feeder/Code/backend/dist/UI/setquantity.html /pyboard/UI/setquantity.html
cp /home/pi/Desktop/Feeder/Code/backend/dist/UI/setschedule.html /pyboard/UI/setschedule.html
cp /home/pi/Desktop/Feeder/Code/backend/dist/UI/css/styles.css /pyboard/UI/css/styles.css
cp /home/pi/Desktop/Feeder/Code/backend/dist/UI/assets/images/Header.png /pyboard/UI/assets/images/Header.png

# Enter REPL and soft reboot
repl
# Press Ctrl+D to reboot ESP8266
```

### Verification on ESP8266

After reboot, you should see:
```
WiFi connected
IP address: 192.168.x.x
Server running on 0.0.0.0:5000
```

### Test ESP8266 Server

From Raspberry Pi or another device on the same network:
```bash
# Replace with your ESP8266's IP
ESP_IP=192.168.1.100

# Test ping
curl http://$ESP_IP:5000/api/ping

# Test home
curl http://$ESP_IP:5000/api/home

# Open in browser
firefox http://$ESP_IP:5000
```

## Troubleshooting

### "Connection unexpectedly closed" in browser
- **Cause**: Response not sent correctly
- **Fix**: Already fixed in updated api.py with proper packet sending

### Server shows connection but browser gets no response
- **Cause**: Body not sent or wrong Content-Length
- **Fix**: Updated send_response() to send as single packet

### "OSError: [Errno 98] Address already in use"
```bash
# Kill existing server
pkill -f "python api.py"
# Or find and kill specific PID
lsof -i :5000
kill <PID>
```

### ESP8266 shows MemoryError
- **Status**: Already fixed with previous optimizations
- **Verify**: Check `gc.mem_free()` after import
```python
>>> import gc
>>> gc.collect()
>>> gc.mem_free()
# Should show >15KB
```

### No output from server
- **Cause**: stdout buffering
- **Fix**: Already added sys.stdout.flush()

### Static files return 404
- **Check**: UI directory structure on ESP8266
```python
# In rshell REPL
>>> import os
>>> os.listdir('UI')
['index.html', 'feednow.html', ...]
>>> os.listdir('UI/css')
['styles.css']
```

## Performance Tips

1. **Memory**: Monitor with `gc.mem_free()` in ESP8266 REPL
2. **Speed**: Reduce image sizes if serving slowly
3. **Connections**: Server handles one connection at a time (sequential)
4. **Timeout**: Connections timeout after 3 seconds
5. **Buffer**: Reads 512 bytes at a time to conserve memory

## Success Indicators

✅ Server starts without errors  
✅ curl commands return JSON responses  
✅ Browser loads index.html  
✅ CSS and images load correctly  
✅ API endpoints respond within 1 second  
✅ No MemoryError on ESP8266  
✅ gc.mem_free() shows >15KB after startup  

## API Endpoints Summary

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | / | Serve index.html |
| GET | /api/ping | Health check |
| GET | /api/home | Dashboard data |
| GET | /api/quantity | Get feed quantity |
| POST | /api/quantity | Update quantity |
| POST | /api/feednow | Manual feed |
| GET | /api/schedule | Get schedule |
| POST | /api/schedule | Update schedule |
| GET | /api/lastfed | Get last feed time |
| POST | /api/lastfed | Update last feed |
| GET | /UI/* | Static files |

All endpoints support CORS (Access-Control-Allow-Origin: *)
