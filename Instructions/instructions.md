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
├── main.py                 # Main entry point with feeding logic
├── config.py              # Configuration settings (WiFi, schedule, pins)
├── lib/                   # Hardware driver modules
│   ├── stepper.py        # 28BYJ-48 stepper motor driver
│   ├── rtc_handler.py    # DS3231 RTC interface
│   └── notification.py   # ntfy.sh notification service
├── wokwi/                # Wokwi online simulator configuration
│   ├── diagram.json      # Circuit diagram
│   └── wokwi.toml        # Simulator settings
└── README.md             # Testing and deployment guide

/Tests/
├── test_motor.py         # Standalone motor testing
├── test_rtc.py           # Standalone RTC testing
└── test_simulation.py    # Simple simulation without hardware
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

### Frontend - React (No Node)
- **Location**: `/Code/frontend`
- **Framework**: React (standalone, no Node.js server)
- **UI Design**: Minimal interface for settings only
- **Features**:
  - Configure feeding times
  - Adjust portion sizes
  - Set notification preferences

## Development Guidelines

### Power Optimization
- **Deep Sleep**: Device sleeps for 30 minutes between schedule checks
- **WiFi**: Only connects for notifications, disconnects immediately after
- **Motor**: Powered off via `motor.off()` immediately after feeding
- **RTC**: Uses separate coin battery, maintains time during deep sleep
- **Debug Output**: Disabled in production (`esp.osdebug(None)`)

### GPIO Pin Configuration
**Stepper Motor (ULN2003):**
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

### Notifications
- Use ntfy service for push notifications to phone
- Send notification after each successful feeding
- Include timestamp and feeding status
- Error notifications sent if feeding fails
- Configure topic in config.py: `NTFY_TOPIC = "your_fish_feeder_topic"`
- Subscribe to topic on phone: https://ntfy.sh/your_fish_feeder_topic

## Testing & Development

### Local Testing (No Hardware)
```bash
# Activate virtual environment
source venv/bin/activate

# Test syntax and basic logic
micropython Tests/test_simulation.py

# Check for syntax errors
micropython -m py_compile Code/backend/main.py
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
