# Fish Feeder Backend - Build & Deploy Guide

## Overview
This package.json and build script create a `dist/` folder containing only the files needed for ESP8266 deployment.

## Build Commands

### Install Node.js dependencies (none required currently)
```powershell
# No dependencies needed, Node.js is only used for the build script
```

### Build for Battery Mode (Scheduled Feeding)
```powershell
npm run build:battery
# or
node build.js battery
```

**Output**: `dist/` folder with:
- main.py (entry point)
- config.py
- lib/ (stepper.py, rtc_handler.py, notification.py)
- README.md (deployment instructions)

**Total size**: ~13KB

### Build for API Server Mode (Always-On)
```powershell
npm run build:api
# or
npm run build
# or
node build.js api
```

**Output**: `dist/` folder with:
- api.py (entry point)
- All service files (services.py, last_fed_service.py, etc.)
- microdot.py, urequests.py
- config.py
- lib/ (hardware drivers)
- UI/ (complete web interface with all HTML, CSS, images)
- data/ (JSON files with default values)
- README.md (deployment instructions)

**Total size**: ~116KB

### Clean Build Output
```powershell
npm run clean
```

## Deployment to ESP8266

After building, navigate to the `dist/` folder and follow the README.md instructions inside for ampy upload commands.

### Quick Deploy Example (Battery Mode)
```powershell
cd dist
$PORT = "COM3"

ampy --port $PORT put main.py
ampy --port $PORT put config.py
ampy --port $PORT mkdir lib
ampy --port $PORT put lib/stepper.py lib/stepper.py
ampy --port $PORT put lib/rtc_handler.py lib/rtc_handler.py
ampy --port $PORT put lib/notification.py lib/notification.py
```

### Quick Deploy Example (API Mode)
```powershell
cd dist
$PORT = "COM3"

# Upload main files
ampy --port $PORT put api.py
ampy --port $PORT put config.py
ampy --port $PORT put services.py
ampy --port $PORT put last_fed_service.py
ampy --port $PORT put next_feed_service.py
ampy --port $PORT put quantity_service.py
ampy --port $PORT put microdot.py
ampy --port $PORT put urequests.py

# Upload lib directory
ampy --port $PORT mkdir lib
ampy --port $PORT put lib/stepper.py lib/stepper.py
ampy --port $PORT put lib/rtc_handler.py lib/rtc_handler.py
ampy --port $PORT put lib/notification.py lib/notification.py

# Upload data directory
ampy --port $PORT mkdir data
ampy --port $PORT put data/schedule.json data/schedule.json
ampy --port $PORT put data/last_fed.json data/last_fed.json
ampy --port $PORT put data/next_feed.json data/next_feed.json
ampy --port $PORT put data/quantity.json data/quantity.json

# Upload UI directory (see dist/README.md for complete commands)
```

## What Gets Excluded?

The build script only includes necessary files. Excluded:
- `__pycache__/` directories
- Test files
- Development documentation
- Wokwi simulation files
- Any unnecessary dependencies

## Customization

Edit `build.js` to modify:
- Files included in each mode
- Data file default values
- Build output location

## Notes

- Always edit `config.py` before building to set WiFi credentials and other settings
- The UI folder is copied AS-IS in API mode (all HTML, CSS, images preserved)
- Data files are created with sensible defaults
- Each build includes a README.md with specific deployment instructions
