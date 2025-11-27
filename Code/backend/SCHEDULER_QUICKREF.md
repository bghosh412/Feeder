# Feeding Scheduler - Quick Reference

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                      ESP32/ESP8266                       │
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │              main.py (Entry Point)              │    │
│  │  1. Start scheduler_service                     │    │
│  │  2. Start api.py server (asyncio event loop)    │    │
│  └────────────────────────────────────────────────┘    │
│                          │                               │
│         ┌────────────────┴───────────────┐              │
│         │                                │              │
│         ▼                                ▼              │
│  ┌─────────────┐                  ┌──────────────┐     │
│  │  Scheduler  │                  │  Web Server  │     │
│  │   (Async)   │                  │   (Async)    │     │
│  │             │                  │              │     │
│  │  • Check    │                  │  • /api/*    │     │
│  │    time     │                  │  • /UI/*     │     │
│  │  • Sleep    │                  │  • Handle    │     │
│  │  • Feed     │                  │    requests  │     │
│  │  • Update   │                  │              │     │
│  └─────────────┘                  └──────────────┘     │
│         │                                               │
│         ▼                                               │
│  ┌─────────────────────────────────────┐               │
│  │   calibration_service.disburseFood() │               │
│  │        (Servo Control)               │               │
│  └─────────────────────────────────────┘               │
│         │                                               │
│         ▼                                               │
│  ┌─────────────────────────────────────┐               │
│  │         Data Files (data/)           │               │
│  │  • next_feed.txt   - Next feed time  │               │
│  │  • last_fed.txt    - Last feed time  │               │
│  │  • schedule.txt    - Weekly schedule │               │
│  │  • calibration.txt - Servo settings  │               │
│  └─────────────────────────────────────┘               │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
                   ┌─────────────┐
                   │   Servo     │
                   │   Motor     │
                   └─────────────┘
```

## Scheduler Flow

```
START
  │
  ▼
┌─────────────────────────┐
│ Read next_feed.txt      │
└─────────────────────────┘
  │
  ▼
┌─────────────────────────┐
│ Is schedule empty?      │
└─────────────────────────┘
  │           │
  │ Yes       │ No
  ▼           ▼
┌───────┐   ┌─────────────────────────┐
│ Feed  │   │ Calculate seconds until │
│ Now   │   │ next feed time          │
└───────┘   └─────────────────────────┘
  │           │
  │           ▼
  │         ┌─────────────────────────┐
  │         │ Sleep for MIN(seconds,  │
  │         │ MAX_SLEEP_SECONDS=300)  │
  │         └─────────────────────────┘
  │           │
  │           ▼
  │         ┌─────────────────────────┐
  │         │ Time arrived?           │
  │         └─────────────────────────┘
  │           │
  │           │ Yes
  ▼           ▼
┌─────────────────────────┐
│ disburseFood()          │
└─────────────────────────┘
  │
  ▼
┌─────────────────────────┐
│ Update last_fed.txt     │
└─────────────────────────┘
  │
  ▼
┌─────────────────────────┐
│ Calculate & update      │
│ next_feed.txt           │
└─────────────────────────┘
  │
  ▼
┌─────────────────────────┐
│ LOOP (go to START)      │
└─────────────────────────┘
```

## Data Flow: Schedule Update

```
User                 Frontend              Backend              Scheduler
  │                     │                     │                     │
  │  Edit Schedule      │                     │                     │
  ├────────────────────▶│                     │                     │
  │                     │                     │                     │
  │                     │  POST /api/schedule │                     │
  │                     ├────────────────────▶│                     │
  │                     │                     │                     │
  │                     │                     │ write_schedule()    │
  │                     │                     │ ──────────┐         │
  │                     │                     │           │         │
  │                     │                     │ ◀─────────┘         │
  │                     │                     │                     │
  │                     │                     │ Write schedule.txt  │
  │                     │                     │ ──────────┐         │
  │                     │                     │           │         │
  │                     │                     │ ◀─────────┘         │
  │                     │                     │                     │
  │                     │                     │ Calculate next feed │
  │                     │                     │ ──────────┐         │
  │                     │                     │           │         │
  │                     │                     │ ◀─────────┘         │
  │                     │                     │                     │
  │                     │                     │ Write next_feed.txt │
  │                     │                     │ ──────────┐         │
  │                     │                     │           │         │
  │                     │                     │ ◀─────────┘         │
  │                     │                     │                     │
  │                     │  {status: ok}       │                     │
  │                     │◀────────────────────┤                     │
  │                     │                     │                     │
  │  Success!           │                     │                     │
  │◀────────────────────┤                     │                     │
  │                     │                     │                     │
  │                     │                     │ (Within 5 minutes)  │
  │                     │                     │                     │
  │                     │                     │      Wake up        │
  │                     │                     │ ◀───────────────────┤
  │                     │                     │                     │
  │                     │                     │ Read next_feed.txt  │
  │                     │                     │ ◀───────────────────┤
  │                     │                     │                     │
  │                     │                     │ Use new time!       │
  │                     │                     │ ◀───────────────────┤
```

## Key Functions

### scheduler_service.py
```python
parse_iso_time(iso_str)                    # Convert ISO time to tuple
seconds_until_next_feed()                   # Calculate wait time
calculate_and_update_next_feed()            # Find next feed from schedule
async feeding_scheduler()                   # Main scheduler loop
start_scheduler()                           # Initialize scheduler task
```

### Integration Points
```python
# Feeding
calibration_service.disburseFood()          # Dispense food

# Time tracking
last_fed_service.write_last_fed(iso_time)   # Record feeding
next_feed_service.write_next_feed(iso_time) # Update next time

# Schedule management
services.write_schedule(data)               # Save schedule (auto-calculates next_feed)
services.read_schedule()                    # Read schedule
```

## Configuration

### scheduler_service.py
```python
MAX_SLEEP_SECONDS = 300  # 5 minutes max between checks
```

### Time Format
```python
ISO_FORMAT = "YYYY-MM-DDTHH:MM:SS"
EXAMPLE = "2025-11-27T14:30:00"  # Nov 27, 2025 at 2:30 PM
```

## Monitoring Commands

### View Logs (Serial Monitor)
```bash
screen /dev/ttyUSB0 115200
# or
minicom -D /dev/ttyUSB0 -b 115200
```

### Check Next Feed Time
```bash
# On ESP32
cat data/next_feed.txt
# Output: 2025-11-27T14:30:00
```

### Check Last Fed
```bash
cat data/last_fed.txt
# Output: 2025-11-27T08:00:00
```

### Check Schedule
```bash
cat data/schedule.txt
# Output:
# times=08:00:AM,20:00:PM
# days=Monday,Tuesday,Wednesday,Thursday,Friday,Saturday,Sunday
```

## Testing Checklist

- [ ] Build backend: `./build_backend.sh api`
- [ ] Test scheduler logic: `micropython test_scheduler.py`
- [ ] Verify asyncio support: `import uasyncio` in REPL
- [ ] Check schedule file format
- [ ] Verify calibration values
- [ ] Test manual feeding via web interface
- [ ] Test schedule updates via web interface
- [ ] Monitor logs for scheduler messages
- [ ] Verify feeding happens at scheduled times

## Troubleshooting

### Scheduler not starting
- Check logs for "Feeding scheduler started"
- Verify uasyncio is available: `import uasyncio`
- Check main.py imports scheduler_service

### Feeding not happening
- Check next_feed.txt is not empty
- Verify schedule.txt has valid times
- Check logs for "Feed time reached"
- Ensure servo is connected (GPIO 18)

### Schedule changes not picked up
- Wait up to 5 minutes for scheduler to wake
- Check logs for "Next feed scheduled for:"
- Verify next_feed.txt was updated after schedule change

### Web server not responding
- Check asyncio mode: logs should show "Using asyncio mode"
- Verify WiFi connection
- Check port 5000 is accessible
- Look for server errors in logs

## Quick Commands

```bash
# Build
cd Code/backend && ./build_backend.sh api

# Test
micropython test_scheduler.py

# View files
ls -la dist/
cat dist/data/next_feed.txt

# Monitor (when deployed)
screen /dev/ttyUSB0 115200
```
