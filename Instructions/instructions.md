# Automatic Fish Feeder - Copilot Instructions

## Project Overview
This is an automatic fish feeder project deployed to ESP8266, powered by 4 Alkaline AA batteries. Power efficiency is critical.

## Hardware Components
1. **ESP8266** - Main microcontroller
2. **Power Supply** - 4 Alkaline AA batteries
3. **28BYJ-48** - 5V stepper motor for dispensing food
4. **ULN2003** - Stepper motor driver
5. **DS3231 RTC** - Real-time clock module to wake ESP8266 during feeding times

## Software Architecture

### Frontend (Web Interface)

#### Location
- `/Code/frontend`

#### Purpose
- Provides a simple web interface for configuring feeding schedule, portion size, and viewing system status.
- Designed to be extremely lightweight for ESP8266 static hosting.

#### Features
- Set feeding schedule (time)
- Set feed quantity
- View feed remaining, last fed time, battery status, and system info
- **Calibrate feeder** - Fine-tune servo motor duty cycle and pulse duration
- Quick links for navigation

#### Technology
- Pure HTML and CSS with minimal JavaScript for calibration
- Minimal CSS for layout and readability
- No build tools, no dependencies
- Can be served as static files from ESP8266 SPIFFS or LittleFS

#### File Structure
```
Code/frontend/
├── index.html           # Main web page
├── feednow.html        # Feed now page
├── setschedule.html    # Schedule configuration
├── setquantity.html    # Quantity settings
├── calibration.html    # Servo calibration page
├── css/
│   └── styles.css      # Minimal stylesheet
├── js/
│   └── calibration.js  # Calibration page logic
├── assets/
│   └── images/
│       └── Header.png  # Header logo
```

#### Usage
- Open `index.html` in a browser to access the feeder controls.
- Hyperlinks in the sidebar allow quick navigation to schedule, feed, and quantity sections.
- All status and configuration is displayed on a single page for simplicity.

#### Customization
- To change logo, replace `Header.png` in `assets/images/`.
- To adjust colors or layout, edit `css/styles.css`.
- For ESP8266, keep HTML and CSS as small as possible for fast loading and low memory usage.

#### Example UI Layout
- Header: Logo and title side-by-side (black background, white text)
- Sidebar: Quick links (gray background, black text)
- Main: Feed Remaining, Last Fed, Battery Status, System Information (cards with borders)


#### Deployment to Local/Server (Backend always on port 5000)
- Upload `index.html`, `css/styles.css`, and `assets/images/Header.png` to ESP8266 SPIFFS/LittleFS or serve locally.
- Start backend server using:
  ```bash
  cd /home/pi/Desktop/Feeder/Code/backend
  python3 api.py
  ```
- The backend API will always be available at `http://localhost:5000`.
- Frontend API calls must use `http://localhost:5000` for all endpoints (e.g., `/api/ping`, `/api/schedule`).
- If deploying to a remote server, replace `localhost` with the server IP.

---

### Backend - MicroPython
- **Location**: `/Code/backend`
- **Platform**: MicroPython for ESP8266
- **Key Requirements**:
  - Extremely frugal power consumption
  - Deep sleep mode between feedings
  - Wake-up via DS3231 RTC timer
  - Stepper motor control via ULN2003 driver
  - Post-feeding notifications via ntfy

#### Backend File Structure
```
/Code/backend/
├── main.py                    # Main entry point with feeding logic
├── api.py                     # API server for web interface (always-on mode)
├── config.py                  # Configuration settings (WiFi, schedule, pins)
├── services.py                # Schedule data operations
├── last_fed_service.py        # Last feed timestamp tracking
├── next_feed_service.py       # Next scheduled feed calculation
├── quantity_service.py        # Feed quantity/remaining tracking
├── calibration_service.py     # Servo calibration and disburseFood()
├── urequests.py              # HTTP client library (MicroPython)
├── data/                     # JSON persistence layer (API mode only)
│   ├── schedule.txt          # Feeding schedule with times/days
│   ├── last_fed.txt          # Last feeding timestamp
│   ├── next_feed.txt         # Calculated next feed time
│   ├── quantity.txt          # Remaining feed quantity
│   └── calibration.txt       # Servo duty cycle and pulse duration
├── UI/                       # Static files served by api.py
│   ├── index.html
│   ├── feednow.html
│   ├── setquantity.html
│   ├── setschedule.html
│   ├── calibration.html
│   ├── css/styles.css
│   └── js/calibration.js
├── lib/                      # Hardware driver modules
│   ├── stepper.py           # 28BYJ-48 stepper motor driver
│   ├── rtc_handler.py       # DS3231 RTC interface
│   └── notification.py      # ntfy.sh notification service
├── wokwi/                   # Wokwi online simulator configuration
│   ├── diagram.json         # Circuit diagram
│   └── wokwi.toml           # Simulator settings
└── README.md                # Testing and deployment guide

/Tests/
├── test_motor.py            # Standalone motor testing
├── test_rtc.py              # Standalone RTC testing
├── test_servo.py            # Servo calibration test script
└── test_simulation.py       # Simple simulation without hardware
```

#### Key Backend Components

**main.py** - Main program flow:
- Initializes RTC and checks current time
- Compares against feeding schedule
- Executes feeding routine if needed
- Sends notification via WiFi
- Enters deep sleep (30 min default)

**config.py** - All configurable parameters:
- WiFi credentials (SSID, password)
- Feeding schedule (list of (hour, minute) tuples)
- Motor settings (steps per feeding, speed)
- GPIO pin assignments
- Deep sleep duration
- ntfy notification settings

**lib/stepper.py** - Stepper motor control:
- Half-step sequence for smooth operation
- Step-by-step control with configurable delay
- Degree-based rotation
- Power-off method for energy saving

**lib/rtc_handler.py** - RTC communication:
- I2C interface to DS3231
- Get/set time functions
- Temperature reading
- Alarm configuration for wake-up

**lib/notification.py** - Push notifications:
- HTTP POST to ntfy.sh service
- Success and error notification methods
- Configurable priority levels

**calibration_service.py** - Servo calibration:
- `read_calibration()` - Read duty cycle and pulse duration from file
- `save_calibration(duty_cycle, pulse_duration)` - Save calibration settings
- `adjust_duty_cycle(increment)` - Adjust duty cycle by ±1 or ±10
- `adjust_pulse_duration(increment)` - Adjust pulse duration by ±5ms
- `disburseFood()` - Main feeding method: reads calibration, runs servo, deinits
- `test_calibration()` - Test current settings and return feedback
- Calibration stored in `data/calibration.txt` as `duty_cycle,pulse_duration`

## Development Guidelines

### Power Optimization
- **Deep Sleep**: Device sleeps for 30 minutes between schedule checks
- **WiFi**: Only connects for notifications, disconnects immediately after
- **Motor**: Powered off via `motor.off()` immediately after feeding
- **RTC**: Uses separate coin battery, maintains time during deep sleep
- **Debug Output**: Disabled in production (`esp.osdebug(None)`)

### GPIO Pin Configuration
**Continuous Rotation Servo:**
- Signal → GPIO18 (D18 on ESP32)
- Power: 5V (not 3.3V!)
- PWM frequency: 50Hz

**Stepper Motor (ULN2003) - Legacy/Alternative:**
- IN1 → GPIO12 (D6)
- IN2 → GPIO13 (D7)
- IN3 → GPIO14 (D5)
- IN4 → GPIO15 (D8)

**DS3231 RTC (I2C):**
- SDA → GPIO4 (D2)
- SCL → GPIO5 (D1)

### Code Structure
- Keep backend code modular for easy deployment to ESP8266
- Separate hardware control (lib/), timing (main.py), and configuration (config.py)
- All hardware drivers are in lib/ folder for clean organization
- Frontend should be lightweight and static-deployable

### API Endpoints (api.py)
The backend provides the following REST API endpoints:

**Feeding:**
- `POST /api/feednow` - Trigger manual feeding, update quantity and last_fed
- `GET /api/home` - Get system status (connection, quantity, last_fed, next_feed, battery)

**Schedule:**
- `GET /api/schedule` - Get feeding schedule
- `POST /api/schedule` - Save feeding schedule (calculates next_feed automatically)

**Quantity:**
- `GET /api/quantity` - Get remaining feed quantity
- `POST /api/quantity` - Update feed quantity

**Calibration:**
- `GET /api/calibration/get` - Get current duty cycle and pulse duration
- `POST /api/calibration/save` - Save calibration (body: `{duty_cycle, pulse_duration}`)
- `POST /api/calibration/adjust_duty` - Adjust duty cycle (body: `{increment}`)
- `POST /api/calibration/adjust_duration` - Adjust pulse duration (body: `{increment}`)
- `POST /api/calibration/test` - Test current calibration settings

**Health:**
- `GET /api/ping` - Health check endpoint
- `GET /api/status` - Server status

### Notifications
- Use ntfy service for push notifications to phone
- Send notification after each successful feeding
- Include timestamp and feeding status
- Error notifications sent if feeding fails
- Configure topic in config.py: `NTFY_TOPIC = "your_fish_feeder_topic"`
- Subscribe to topic on phone: https://ntfy.sh/your_fish_feeder_topic

## Servo Calibration Workflow

### Purpose
The calibration system allows fine-tuning of the servo motor to dispense the exact amount of food needed.

### Calibration Parameters
- **Duty Cycle** (0-1023): PWM duty cycle for servo rotation speed/direction
- **Pulse Duration** (1-1000ms): How long to run the servo motor

### Calibration Page Controls
| Button | Action |
|--------|--------|
| `>>` (duty) | Decrease duty cycle by 10 (more food) |
| `>` (duty) | Decrease duty cycle by 1 |
| `<` (duty) | Increase duty cycle by 1 (less food) |
| `<<` (duty) | Increase duty cycle by 10 |
| `>` (duration) | Increase pulse duration by 5ms |
| `<` (duration) | Decrease pulse duration by 5ms |
| Test | Run servo with current settings |
| Save | Save calibration to file |

### Calibration Steps
1. Open `http://<device-ip>/calibration.html` in browser
2. Current values displayed: Duty Cycle (default: 80), Pulse Duration (default: 10ms)
3. Press **Test** button to observe current behavior
4. **If disk doesn't disperse complete food**: Press `<` or `<<` buttons (increases duty)
5. **If disk disperses too much food**: Press `>` or `>>` buttons (decreases duty)
6. Adjust pulse duration with `<` or `>` buttons if needed
7. Press **Test** repeatedly to verify calibration
8. Once satisfied, press **Save** to persist settings
9. Settings stored in `data/calibration.txt` (format: `duty_cycle,pulse_duration`)

### Using Calibration in Code
The `disburseFood()` function automatically uses the saved calibration:
```python
import calibration_service

# Dispense food using saved calibration
calibration_service.disburseFood()
# This will:
# 1. Read duty_cycle and pulse_duration from data/calibration.txt
# 2. Initialize servo PWM
# 3. Apply duty cycle for specified duration
# 4. Deinitialize servo (stops motor and saves power)
```

### Test Script for Manual Calibration
Use `test_servo.py` for hardware testing:
```bash
# Activate virtual environment
source venv/bin/activate

# Run continuous microstepping test
micropython Tests/test_servo.py
# - Pulses duty 80 for 10ms
# - Deinits servo between pulses
# - Press Ctrl+C to stop
```

## Testing & Development

### Local Testing (No Hardware)
```bash
# Activate virtual environment
source venv/bin/activate

# Test syntax and basic logic
micropython Tests/test_simulation.py

# Check for syntax errors
micropython -m py_compile Code/backend/main.py
micropython -m py_compile Code/backend/calibration_service.py
```

### Wokwi Online Simulation
1. Visit https://wokwi.com
2. Create new ESP8266 MicroPython project
3. Upload circuit from `/Code/backend/wokwi/diagram.json`
4. Copy code files (main.py, config.py, lib/)
5. Run simulation to test hardware interactions

### Hardware Testing
```bash
# Test motor independently
micropython Tests/test_motor.py

# Test RTC independently  
micropython Tests/test_rtc.py
```

### Deployment to ESP8266
```bash
# Flash MicroPython firmware (first time)
esptool.py --port /dev/ttyUSB0 erase_flash
esptool.py --port /dev/ttyUSB0 --baud 460800 write_flash --flash_size=detect 0 firmware.bin

# Upload code files
ampy --port /dev/ttyUSB0 put main.py
ampy --port /dev/ttyUSB0 put config.py
ampy --port /dev/ttyUSB0 mkdir lib
ampy --port /dev/ttyUSB0 put lib/stepper.py lib/stepper.py
ampy --port /dev/ttyUSB0 put lib/rtc_handler.py lib/rtc_handler.py
ampy --port /dev/ttyUSB0 put lib/notification.py lib/notification.py
```

## Development Tools Installed
- **esptool** - Flash ESP8266 firmware
- **mpremote** - Interact with MicroPython devices
- **adafruit-ampy** - Upload files to MicroPython boards
- **micropython** - Local MicroPython interpreter for testing

## File Locations
- **Instructions**: `/Instructions/`
- **Backend Code**: `/Code/backend`
- **Frontend Code**: `/Code/frontend`
- **Test Files**: `/Tests`
- **Python Virtual Environment**: `/venv`
