SCHEDULE_FILE = "data/schedule.txt"

def read_schedule():
    """
    Read schedule from plain text file.
    Format: times=08:00:AM,20:00:PM
            days=Monday,Tuesday,Wednesday
    Returns: dict with feeding_times and days for API compatibility
    """
    try:
        with open(SCHEDULE_FILE, "r") as f:
            lines = f.readlines()
        
        feeding_times = []
        days = {}
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                key, value = line.split('=', 1)
                if key == 'times':
                    # Parse times: 08:00:AM,20:00:PM
                    for time_str in value.split(','):
                        if time_str:
                            parts = time_str.split(':')
                            if len(parts) >= 2:
                                hour = int(parts[0])
                                min_ampm = parts[1]
                                if 'AM' in min_ampm or 'PM' in min_ampm:
                                    minute = int(min_ampm[:2])
                                    ampm = min_ampm[2:]
                                else:
                                    minute = int(min_ampm)
                                    ampm = parts[2] if len(parts) > 2 else 'AM'
                                feeding_times.append({
                                    'hour': hour,
                                    'minute': minute,
                                    'ampm': ampm,
                                    'enabled': True
                                })
                elif key == 'days':
                    # Parse days: Monday,Tuesday,Wednesday
                    all_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
                    enabled_days = [d.strip() for d in value.split(',') if d.strip()]
                    for day in all_days:
                        days[day] = day in enabled_days
        
        return {'feeding_times': feeding_times, 'days': days}
    except:
        return None


def write_schedule(schedule_data):
    """
    Write schedule to plain text file.
    Args:
        schedule_data: dict with feeding_times and days
    Returns: True if successful, False otherwise
    """
    try:
        # Build times string
        feeding_times = [t for t in schedule_data.get("feeding_times", []) if t.get("enabled")]
        times_list = []
        for t in feeding_times:
            hour = t.get("hour", 0)
            minute = t.get("minute", 0)
            ampm = t.get("ampm", "AM")
            times_list.append("{:02d}:{:02d}:{}".format(hour, minute, ampm))
        times_str = ','.join(times_list)
        
        # Build days string
        enabled_days = [day for day, enabled in schedule_data.get("days", {}).items() if enabled]
        days_str = ','.join(enabled_days)
        
        # Write to file
        with open(SCHEDULE_FILE, "w") as f:
            f.write("times={}\n".format(times_str))
            f.write("days={}\n".format(days_str))
        
        # Calculate next feed time
        import time
        import next_feed_service
        
        now = time.localtime()
        now_secs = time.mktime(now)
        next_feed_secs = None
        next_feed_tuple = None
        
        weekday_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        
        for day_offset in range(8):
            check_secs = now_secs + (86400 * day_offset)
            check_date = time.localtime(check_secs)
            weekday = weekday_names[check_date[6]]
            
            if weekday in enabled_days:
                for feed_time in feeding_times:
                    hour = feed_time.get("hour", 0)
                    minute = feed_time.get("minute", 0)
                    ampm = feed_time.get("ampm", "AM")
                    
                    # Convert to 24-hour format
                    if ampm == "PM" and hour < 12:
                        hour += 12
                    if ampm == "AM" and hour == 12:
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
        else:
            next_feed_service.write_next_feed("Not scheduled")
        
        return True
    except:
        return False
