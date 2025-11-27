"""
Asyncio-based feeding scheduler service.
Monitors next_feed.txt and automatically triggers feeding at scheduled times.
"""

import uasyncio as asyncio
import time
import next_feed_service
import calibration_service

# Maximum sleep time (5 minutes in seconds)
MAX_SLEEP_SECONDS = 300

def parse_iso_time(iso_str):
    """Parse ISO format time string to time tuple.
    Format: YYYY-MM-DDTHH:MM:SS
    Returns: time tuple or None if invalid
    """
    try:
        if not iso_str or iso_str == "Not scheduled":
            return None
        
        date_part, time_part = iso_str.split('T')
        year, month, day = date_part.split('-')
        hour, minute, second = time_part.split(':')
        
        # Create time tuple (year, month, day, hour, minute, second, weekday, yearday)
        # weekday and yearday will be calculated by mktime
        return (int(year), int(month), int(day), int(hour), int(minute), int(second), 0, 0)
    except Exception as e:
        print(f"Error parsing ISO time '{iso_str}': {e}")
        return None

def seconds_until_next_feed():
    """Calculate seconds until next scheduled feed.
    Returns: seconds until next feed, or None if not scheduled
    """
    try:
        # Read next feed time from file
        with open(next_feed_service.NEXT_FEED_FILE, 'r') as f:
            iso_time = f.read().strip()
        
        if not iso_time or iso_time == "Not scheduled":
            return None
        
        # Parse the ISO time
        next_feed_tuple = parse_iso_time(iso_time)
        if not next_feed_tuple:
            return None
        
        # Convert to seconds since epoch
        next_feed_secs = time.mktime(next_feed_tuple)
        now_secs = time.time()
        
        # Calculate difference
        diff = next_feed_secs - now_secs
        
        print(f"Next feed in {diff:.0f} seconds ({diff/60:.1f} minutes)")
        
        return max(0, diff)  # Return 0 if time has passed
        
    except Exception as e:
        print(f"Error calculating next feed time: {e}")
        return None

def calculate_and_update_next_feed():
    """Calculate the next feed time based on schedule and update next_feed.txt.
    This is called after each feeding to prepare for the next one.
    """
    try:
        import services
        
        # Read current schedule
        schedule = services.read_schedule()
        if not schedule or not schedule.get('feeding_times'):
            print("No schedule configured")
            next_feed_service.write_next_feed("Not scheduled")
            return
        
        # Get enabled feeding times and days
        feeding_times = [t for t in schedule.get('feeding_times', []) if t.get('enabled')]
        enabled_days = [day for day, enabled in schedule.get('days', {}).items() if enabled]
        
        if not feeding_times or not enabled_days:
            print("No enabled feeding times or days")
            next_feed_service.write_next_feed("Not scheduled")
            return
        
        # Find next feed time
        now = time.localtime()
        now_secs = time.mktime(now)
        next_feed_secs = None
        next_feed_tuple = None
        
        weekday_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        
        # Search up to 7 days ahead
        for day_offset in range(8):
            check_secs = now_secs + (86400 * day_offset)
            check_date = time.localtime(check_secs)
            weekday = weekday_names[check_date[6]]
            
            if weekday in enabled_days:
                for feed_time in feeding_times:
                    hour = feed_time.get('hour', 0)
                    minute = feed_time.get('minute', 0)
                    ampm = feed_time.get('ampm', 'AM')
                    
                    # Convert to 24-hour format
                    if ampm == 'PM' and hour < 12:
                        hour += 12
                    if ampm == 'AM' and hour == 12:
                        hour = 0
                    
                    feed_tuple = (check_date[0], check_date[1], check_date[2], hour, minute, 0, check_date[6], check_date[7])
                    feed_secs = time.mktime(feed_tuple)
                    
                    if feed_secs > now_secs:
                        if next_feed_secs is None or feed_secs < next_feed_secs:
                            next_feed_secs = feed_secs
                            next_feed_tuple = feed_tuple
                
                if next_feed_tuple:
                    break
        
        # Write next feed time
        if next_feed_tuple:
            iso_str = "{:04d}-{:02d}-{:02d}T{:02d}:{:02d}:{:02d}".format(
                next_feed_tuple[0], next_feed_tuple[1], next_feed_tuple[2],
                next_feed_tuple[3], next_feed_tuple[4], next_feed_tuple[5]
            )
            next_feed_service.write_next_feed(iso_str)
            print(f"Next feed scheduled for: {iso_str}")
        else:
            next_feed_service.write_next_feed("Not scheduled")
            print("No upcoming feed times found")
            
    except Exception as e:
        print(f"Error calculating next feed: {e}")
        import sys
        sys.print_exception(e)

async def feeding_scheduler():
    """Main scheduler loop that monitors and triggers feeding."""
    import gc
    
    print("Feeding scheduler started")
    
    while True:
        try:
            # Free memory at start of each cycle
            gc.collect()
            
            # Calculate seconds until next feed
            seconds = seconds_until_next_feed()
            
            # If next_feed.txt is empty or not scheduled, feed immediately and recalculate
            if seconds is None:
                print("No scheduled feed time found - feeding now and calculating schedule")
                
                # Log event
                import event_log_service
                event_log_service.log_event(event_log_service.EVENT_FEED_IMMEDIATE, 'No schedule found')
                
                calibration_service.disburseFood()
                
                # Update quantity
                import quantity_service
                quantity = quantity_service.read_quantity()
                if quantity > 0:
                    quantity -= 1
                    quantity_service.write_quantity(quantity)
                
                # Update last fed time
                import last_fed_service
                now = time.localtime()
                iso_time = "{:04d}-{:02d}-{:02d}T{:02d}:{:02d}:{:02d}".format(
                    now[0], now[1], now[2], now[3], now[4], now[5]
                )
                last_fed_service.write_last_fed(iso_time)
                
                # Send notification
                try:
                    import lib.notification
                    time_str = "{:02d}:{:02d}:{:02d}".format(now[3], now[4], now[5])
                    msg = "Food disbursed at {}. Feed remaining: {}".format(time_str, quantity)
                    lib.notification.send_ntfy_notification(msg)
                except Exception as e:
                    print(f"Could not send notification: {e}")
                
                # Calculate and update next feed time
                calculate_and_update_next_feed()
                
                # Clean up after feeding cycle
                gc.collect()
                
                # Sleep for a bit before checking again
                await asyncio.sleep(60)
                continue
            
            # If feed time is now or past, feed immediately
            if seconds <= 0:
                print("Feed time reached - dispensing food")
                
                # Log event
                import event_log_service
                event_log_service.log_event(event_log_service.EVENT_FEED_SCHEDULED, 'Scheduled feeding')
                
                calibration_service.disburseFood()
                
                # Update quantity
                import quantity_service
                quantity = quantity_service.read_quantity()
                if quantity > 0:
                    quantity -= 1
                    quantity_service.write_quantity(quantity)
                
                # Update last fed time
                import last_fed_service
                now = time.localtime()
                iso_time = "{:04d}-{:02d}-{:02d}T{:02d}:{:02d}:{:02d}".format(
                    now[0], now[1], now[2], now[3], now[4], now[5]
                )
                last_fed_service.write_last_fed(iso_time)
                
                # Send notification
                try:
                    import lib.notification
                    time_str = "{:02d}:{:02d}:{:02d}".format(now[3], now[4], now[5])
                    msg = "Food disbursed at {}. Feed remaining: {}".format(time_str, quantity)
                    lib.notification.send_ntfy_notification(msg)
                except Exception as e:
                    print(f"Could not send notification: {e}")
                
                # Calculate and update next feed time
                calculate_and_update_next_feed()
                
                # Clean up after feeding cycle
                gc.collect()
                
                # Sleep for a bit to avoid immediate re-trigger
                await asyncio.sleep(60)
                continue
            
            # Sleep until next feed or max 5 minutes
            sleep_time = min(seconds, MAX_SLEEP_SECONDS)
            print(f"Scheduler sleeping for {sleep_time:.0f} seconds ({sleep_time/60:.1f} minutes)")
            await asyncio.sleep(sleep_time)
            
        except Exception as e:
            print(f"Error in feeding scheduler: {e}")
            
            # Log error
            try:
                import event_log_service
                event_log_service.log_event(event_log_service.EVENT_ERROR, 'Scheduler: {}'.format(str(e)))
            except:
                pass
            
            import sys
            sys.print_exception(e)
            # Sleep a bit before retrying
            await asyncio.sleep(60)

def start_scheduler():
    """Start the feeding scheduler as an asyncio task."""
    loop = asyncio.get_event_loop()
    loop.create_task(feeding_scheduler())
    print("Feeding scheduler task created")
