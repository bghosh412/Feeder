# Automatic Feeding Scheduler

## Overview
The feeding scheduler is an asyncio-based background task that automatically triggers feeding at scheduled times. It runs continuously alongside the API server without blocking web access.

## How It Works

### Architecture
- **Asyncio-based**: Uses `uasyncio` for cooperative multitasking
- **Non-blocking**: Web server remains responsive while scheduler sleeps
- **Efficient**: Sleeps for exact duration until next feed (max 5 minutes)
- **Automatic**: Triggers `disburseFood()` at scheduled times

### Workflow
1. **Startup**: Scheduler starts when `main.py` runs
2. **Check Schedule**: Reads `next_feed.txt` for next scheduled feeding time
3. **Calculate Wait**: Computes seconds until next feed
4. **Smart Sleep**: Sleeps for exact time or max 5 minutes (whichever is less)
5. **Feed**: When time arrives, calls `disburseFood()`
6. **Update**: Records last feed time, calculates next feed time
7. **Repeat**: Returns to step 2

### Special Cases
- **Empty Schedule**: If `next_feed.txt` is empty, feeds immediately and calculates next time
- **Past Due**: If scheduled time has passed, feeds immediately
- **No Schedule**: If no schedule is configured, writes "Not scheduled"

## Files Involved

### scheduler_service.py
Main scheduler implementation with these functions:
- `parse_iso_time()`: Convert ISO timestamp to time tuple
- `seconds_until_next_feed()`: Calculate wait time
- `calculate_and_update_next_feed()`: Find next feed time from schedule
- `feeding_scheduler()`: Main async loop (runs continuously)
- `start_scheduler()`: Initialize scheduler task

### main.py
Entry point that:
1. Imports scheduler_service
2. Starts the scheduler task
3. Starts the API server (which runs the asyncio event loop)

### api.py
Modified to support asyncio:
- `_run_async()`: Async server mode
- `_run_blocking()`: Fallback for non-asyncio environments
- Non-blocking socket operations

## Schedule Updates

When the user updates the schedule via the web interface:
1. Frontend sends POST to `/api/schedule`
2. `services.write_schedule()` saves schedule
3. Automatically calculates and writes `next_feed.txt`
4. Scheduler picks up new time on next check (within 5 minutes)

## Configuration

### Maximum Sleep Time
```python
MAX_SLEEP_SECONDS = 300  # 5 minutes
```
This prevents the scheduler from sleeping too long, allowing it to:
- Pick up schedule changes relatively quickly
- Handle edge cases where exact timing matters
- Provide regular status updates in logs

### Timing Tolerance
The scheduler triggers feeding when:
```python
if seconds <= 0:  # Time has arrived or passed
    disburseFood()
```

## Testing

Use `test_scheduler.py` to verify:
```bash
micropython test_scheduler.py
```

Tests include:
- ISO time parsing
- Next feed calculation
- Seconds calculation
- Empty schedule handling

## Deployment

The scheduler is included in the standard build:
```bash
cd Code/backend
./build_backend.sh api
```

Files deployed:
- `scheduler_service.py` → Core scheduler logic
- `main.py` → Starts scheduler and API server
- `api.py` → Async-capable web server

## Monitoring

Check logs for scheduler activity:
- "Feeding scheduler started" → Initialization
- "Scheduler sleeping for X seconds" → Wait state
- "Feed time reached - dispensing food" → Feeding triggered
- "Next feed scheduled for: YYYY-MM-DDTHH:MM:SS" → Next time calculated

## Power Considerations

Since the device is now adapter-powered:
- No deep sleep mode
- WiFi always on
- Web interface always accessible
- Scheduler runs continuously
- Minimal power consumption in sleep state

## Error Handling

The scheduler includes robust error handling:
- Catches all exceptions in main loop
- Prints errors to console
- Continues running after errors
- 60-second retry delay after errors

## Integration with Existing Features

### Manual Feeding
- Web interface "Feed Now" button still works
- Does NOT affect scheduled feeding
- Updates `last_fed.txt` independently

### Calibration
- Scheduler uses current calibration settings
- Changes to duty cycle/pulse duration apply immediately
- Test calibration does not affect schedule

### Schedule Management
- Changes via web interface picked up automatically
- No restart required
- Next feed recalculated on every schedule save
