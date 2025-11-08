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
- Minimize WiFi usage (connect only for notifications)
- Use deep sleep mode extensively
- Optimize stepper motor operation duration
- Disable unused peripherals

### Code Structure
- Keep backend code modular for easy deployment to ESP8266
- Separate hardware control, timing, and networking concerns
- Frontend should be lightweight and static-deployable

### Notifications
- Use ntfy service for push notifications to phone
- Send notification after each successful feeding
- Include timestamp and feeding status

## File Locations
- **Instructions**: `/Instructions/`
- **Backend Code**: `/Code/backend`
- **Frontend Code**: `/Code/frontend`
