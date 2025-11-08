# Fish Feeder Test Suite

This directory contains all test files for the fish feeder project.

## Test Files

### test_motor.py
Tests the 28BYJ-48 stepper motor functionality:
- Forward and backward rotation
- Degree-based rotation
- Step control

**Usage:**
```bash
# From project root
micropython Tests/test_motor.py

# Or from Tests directory
cd Tests
micropython test_motor.py
```

### test_rtc.py
Tests the DS3231 RTC module:
- Reading current time
- Temperature sensor
- Time monitoring

**Usage:**
```bash
# From project root
micropython Tests/test_rtc.py

# Or from Tests directory
cd Tests
micropython test_rtc.py
```

### test_simulation.py
Simple simulation test without hardware dependencies:
- Simulates complete feeding cycle
- Tests all system components logic
- Safe to run without ESP8266 or hardware

**Usage:**
```bash
# From project root
micropython Tests/test_simulation.py

# Or from Tests directory
cd Tests
micropython test_simulation.py
```

## Running Tests

### Prerequisites
- MicroPython installed (for local testing)
- Virtual environment activated (optional)

### Local Testing (Without Hardware)
```bash
# Activate venv
source venv/bin/activate

# Run simulation test
micropython Tests/test_simulation.py
```

### Hardware Testing (With ESP8266)
```bash
# Upload test file to ESP8266
ampy --port /dev/ttyUSB0 put Tests/test_motor.py test_motor.py

# Run via serial console
screen /dev/ttyUSB0 115200
>>> import test_motor
```

### Syntax Validation
```bash
# Check for syntax errors
micropython -m py_compile Tests/test_motor.py
micropython -m py_compile Tests/test_rtc.py
micropython -m py_compile Tests/test_simulation.py
```

## Notes

- Import errors in IDE are expected - these files use MicroPython libraries
- Tests use `sys.path.append('../Code/backend')` to import project modules
- For hardware tests, ensure proper GPIO connections as per `/Instructions/instructions.md`
