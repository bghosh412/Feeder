# Fish Feeder - AI Coding Agent Instructions

## Project Overview
ESP8266 automatic fish feeder using MicroPython. Supports **two deployment modes**:
- **Battery-powered mode**: Deep sleep cycles, minimal power usage (4 AA batteries)
- **Always-on server mode**: Microdot API server for real-time web control

## Architecture

### Two Distinct Codebases
1. **Backend** (`Code/backend/`) - MicroPython for ESP8266 microcontroller
2. **Frontend** (`Code/frontend/`) - Vanilla HTML/CSS/JS web interface

**Critical**: These are separate execution environments. Backend runs on embedded hardware (or Raspberry Pi for development), frontend is browser-based. No shared runtime or modules.

### Dual Backend Modes
The backend supports two operational modes with different entry points:

**Mode 1: Battery-Powered (Scheduled)**
- Entry: `main.py`
- Pattern: Wake → check schedule → feed if needed → deep sleep (30min)
- Power: Minimal WiFi usage (only for notifications)
- Use case: Production deployment on battery power

**Mode 2: Always-On API Server**
- Entry: `api.py` (Microdot web framework)
- Pattern: HTTP server on port 5000, real-time control via REST API
- Persistence: JSON files in `data/` directory (`schedule.json`, `last_fed.json`, `next_feed.json`, `quantity.json`)
- Use case: Development on Raspberry Pi, or mains-powered ESP8266 with web interface

### Backend Structure (MicroPython)
```
Code/backend/
├── main.py              # Entry point: schedule check → feed → deep sleep (battery mode)
├── api.py               # Microdot API server for web control (always-on mode)
├── config.py            # All hardware pins, WiFi, schedule config
├── services.py          # Schedule data operations
├── last_fed_service.py  # Last feed timestamp tracking
├── next_feed_service.py # Next scheduled feed calculation
├── quantity_service.py  # Feed quantity/remaining tracking
├── microdot.py          # Lightweight WSGI web framework for MicroPython
├── urequests.py         # HTTP client library (MicroPython)
├── data/                # JSON persistence layer (API mode only)
│   ├── schedule.json    # Feeding schedule with times/days
│   ├── last_fed.json    # Last feeding timestamp
│   ├── next_feed.json   # Calculated next feed time
│   └── quantity.json    # Remaining feed quantity
├── UI/                  # Static files served by api.py
│   ├── index.html
│   ├── feednow.html
│   ├── setquantity.html
│   ├── setschedule.html
│   ├── css/styles.css
│   └── assets/images/
└── lib/
    ├── stepper.py       # 28BYJ-48 motor control (half-step sequence)
    ├── rtc_handler.py   # DS3231 I2C RTC communication
    └── notification.py  # ntfy.sh push notifications via urequests
```

**Service Layer Pattern**:
- All data operations abstracted into service modules (`*_service.py`)
- Read/write JSON files for persistence in API server mode
- ISO 8601 timestamp format: `YYYY-MM-DDTHH:MM:SS`
- Schedule format: `{"feeding_times": [{"hour": 8, "minute": 0, "ampm": "AM", "enabled": true}], "days": {"Monday": true, ...}}`

**Power-critical patterns**:
- WiFi only enabled during notifications, immediately disconnected after
- Motor powered off via `motor.off()` after every feeding
- Deep sleep between cycles: `machine.deepsleep(DEEP_SLEEP_MINUTES * 60 * 1000000)`
- Debug output disabled in production: `esp.osdebug(None)`

### Frontend Structure
- Pure vanilla JS/HTML/CSS - no frameworks, no build tools
- Component-based with dynamic loading (`loadComponent()` in `app.js`)
- API calls to backend endpoints
- Status polling every 30 seconds for connection monitoring

**API Integration Pattern**:
Frontend (`app.js`) expects these endpoints:
- `POST /api/feed` → manual feeding trigger
- `POST /api/schedule` → create/update schedule
- `GET /api/schedules` → list all schedules
- `DELETE /api/schedule/{id}` → remove schedule
- `GET /api/status` → system health check

Backend (`api.py`) actual endpoints:
- `POST /api/feednow` → manual feeding (reduces quantity, updates last_fed)
- `POST /api/schedule` → save schedule (calculates next_feed)
- `GET /api/schedule` → read schedule
- `POST /api/quantity` → update quantity
- `GET /api/home` → combined status (connection, quantity, last_fed, battery, next_feed)
- `GET /api/ping` → health check

**Note**: There's an endpoint mismatch between frontend expectations and backend implementation. Frontend needs updating or backend needs `/api/schedules` (plural) endpoint.

## Hardware Configuration

### GPIO Pin Assignments (ESP8266)
**Stepper Motor (ULN2003 driver)**:
- IN1 → GPIO12 (D6), IN2 → GPIO13 (D7)
- IN3 → GPIO14 (D5), IN4 → GPIO15 (D8)

**DS3231 RTC (I2C)**:
- SDA → GPIO4 (D2), SCL → GPIO5 (D1)

**All pins configured in `config.py`** - modify there, not in driver files.

### Stepper Motor Specifics
- 28BYJ-48 with half-step sequence (8 steps/cycle)
- 4096 half-steps = 360° rotation
- `MOTOR_STEPS_PER_FEEDING = 512` in config (one full rotation)
- Delay between steps: `MOTOR_SPEED_MS = 2` (configurable for speed vs. power)

## Development Workflows

### Local Testing (Without Hardware)
```powershell
# Activate venv first
.\venv\Scripts\Activate.ps1

# Syntax validation
micropython -m py_compile Code\backend\main.py

# Simulation test (no hardware required)
micropython Tests\test_simulation.py
```

### Hardware Testing
```powershell
# Test individual components
micropython Tests\test_motor.py    # Motor control verification
micropython Tests\test_rtc.py      # RTC communication test
```

### Deployment to ESP8266
```powershell
# Upload files using ampy
ampy --port COM3 put Code\backend\main.py
ampy --port COM3 put Code\backend\config.py
ampy --port COM3 mkdir lib
ampy --port COM3 put Code\backend\lib\stepper.py lib\stepper.py
ampy --port COM3 put Code\backend\lib\rtc_handler.py lib\rtc_handler.py
ampy --port COM3 put Code\backend\lib\notification.py lib\notification.py
```

**Windows port detection**: Use Device Manager → Ports to find COM port number.

### Wokwi Simulation
Online circuit simulation at https://wokwi.com
- Circuit diagram: `Code/backend/wokwi/diagram.json`
- Upload all backend files to simulate hardware interactions without physical components

## Key Conventions

### Configuration Over Code
**Always modify `config.py` for**:
- Feeding schedule (`FEEDING_TIMES = [(8, 0), (20, 0)]` - 24hr format)
- WiFi credentials
- Motor parameters (steps, speed)
- GPIO pin assignments
- Deep sleep duration
- ntfy notification settings

### Feeding Logic (`main.py`)
1. Wake from deep sleep (RTC maintains time)
2. Initialize RTC, read current time
3. Compare against `FEEDING_TIMES` schedule
4. If match: execute `feed()` → send notification
5. Enter deep sleep for `DEEP_SLEEP_MINUTES`

**Timing tolerance**: Matches feeding time within 1 minute window

### Notification Pattern
Uses ntfy.sh for push notifications:
```python
notifier = NotificationService(config.NTFY_SERVER, config.NTFY_TOPIC)
notifier.send_feeding_notification(time_str)  # Success
notifier.send_error_notification(error_msg)   # Errors
```

Subscribe to notifications: `https://ntfy.sh/<NTFY_TOPIC>` on phone

## Common Tasks

### Adding New Feeding Time
Edit `config.py`:
```python
FEEDING_TIMES = [
    (8, 0),   # 8:00 AM
    (12, 0),  # 12:00 PM (NEW)
    (20, 0),  # 8:00 PM
]
```

### Adjusting Motor Rotation
Modify in `config.py`:
```python
MOTOR_STEPS_PER_FEEDING = 1024  # Double rotation
MOTOR_SPEED_MS = 5              # Slower speed (higher = slower)
```

### Changing Deep Sleep Duration
```python
DEEP_SLEEP_MINUTES = 15  # Check every 15 minutes instead of 30
```

### Frontend API Integration
Backend API endpoints expected at `/api/*`:
- `POST /api/feed` - Manual feeding trigger
- `POST /api/schedule` - Add feeding schedule
- `GET /api/schedules` - List all schedules
- `DELETE /api/schedule/{id}` - Remove schedule
- `GET /api/status` - System health check

## Running the API Server (Development Mode)

### Raspberry Pi / Linux
```bash
cd /home/pi/Desktop/Feeder/Code/backend
python3 api.py
```

### Windows (PowerShell)
```powershell
cd Code\backend
micropython api.py
```

Server always runs on port 5000. Frontend must use `http://localhost:5000` for all API calls.

## Testing Strategy

**Always test in this order**:
1. Syntax check: `micropython -m py_compile <file>`
2. Simulation: `micropython Tests\test_simulation.py`
3. Component tests: `test_motor.py`, `test_rtc.py`
4. Wokwi simulation (if modifying hardware interactions)
5. ESP8266 deployment

## Important Constraints

- **File size**: Keep code minimal - ESP8266 has limited flash/RAM
- **Import errors in IDE**: Expected - uses MicroPython libraries not available in standard Python
- **WiFi**: Only 2.4GHz networks supported by ESP8266
- **Deep sleep**: Device loses RAM state - RTC maintains time externally
- **Battery life**: Design decisions prioritize power efficiency over features

## Documentation
- Full project details: `Instructions/instructions.md`
- Backend testing guide: `Code/backend/README.md`
- Frontend setup: `Code/frontend/README.md`
- Test suite info: `Tests/README.md`
