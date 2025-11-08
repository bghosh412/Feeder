# Fish Feeder Testing Guide

## Local Testing with MicroPython

### 1. Test Motor Control
```bash
# Run on ESP8266 or use micropython for syntax check
micropython test_motor.py
```

### 2. Test RTC Communication
```bash
micropython test_rtc.py
```

### 3. Syntax Check Main Program
```bash
micropython -m py_compile main.py
micropython -m py_compile config.py
```

## Wokwi Online Simulation

### Steps to simulate on Wokwi:

1. Go to https://wokwi.com
2. Create new project → ESP32/ESP8266 → MicroPython
3. Upload files:
   - Copy contents of `main.py`
   - Copy contents of `config.py`
   - Copy lib folder files
   - Upload `wokwi/diagram.json` for circuit
4. Click "Start Simulation"

### Quick Test File
Use `test_simulation.py` for a simple simulation without hardware dependencies:
```bash
micropython test_simulation.py
```

## Deploying to ESP8266

### 1. Install Firmware (first time only)
```bash
# Erase flash
esptool.py --port /dev/ttyUSB0 erase_flash

# Flash MicroPython firmware
esptool.py --port /dev/ttyUSB0 --baud 460800 write_flash --flash_size=detect 0 esp8266-firmware.bin
```

### 2. Upload Code
```bash
# Upload all files
ampy --port /dev/ttyUSB0 put main.py
ampy --port /dev/ttyUSB0 put config.py
ampy --port /dev/ttyUSB0 mkdir lib
ampy --port /dev/ttyUSB0 put lib/stepper.py lib/stepper.py
ampy --port /dev/ttyUSB0 put lib/rtc_handler.py lib/rtc_handler.py
ampy --port /dev/ttyUSB0 put lib/notification.py lib/notification.py
```

### 3. Configure Settings
Edit `config.py` before uploading:
- Set WiFi credentials
- Configure feeding times
- Set ntfy topic

### 4. Test on Device
```bash
# Connect to serial console
mpremote connect /dev/ttyUSB0
# or
screen /dev/ttyUSB0 115200
```

## Hardware Connections

### Stepper Motor (28BYJ-48 + ULN2003)
- IN1 → GPIO12 (D6)
- IN2 → GPIO13 (D7)
- IN3 → GPIO14 (D5)
- IN4 → GPIO15 (D8)
- VCC → 5V
- GND → GND

### DS3231 RTC
- SDA → GPIO4 (D2)
- SCL → GPIO5 (D1)
- VCC → 3.3V
- GND → GND

## Power Consumption Tips

1. **Deep Sleep**: Device sleeps between checks (30 min default)
2. **WiFi**: Only connects for notifications
3. **Motor**: Powered off immediately after feeding
4. **RTC**: Uses coin battery, keeps time during sleep

## Troubleshooting

### Motor not moving
- Check wiring to ULN2003
- Verify 5V power supply
- Test with `test_motor.py`

### RTC not responding
- Check I2C connections (SDA/SCL)
- Verify 3.3V power
- Test with `test_rtc.py`

### WiFi connection fails
- Check credentials in `config.py`
- Ensure 2.4GHz WiFi network
- Check signal strength

### Notifications not sending
- Verify internet connection
- Check ntfy topic name
- Test at https://ntfy.sh/your_topic
