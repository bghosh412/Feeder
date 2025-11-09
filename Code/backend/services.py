import ujson

SCHEDULE_FILE = "data/schedule.json"

def read_schedule():
    """
    Read schedule data from JSON file to send to frontend.
    Returns: dict with feeding_times and days, or None if error
    """
    try:
        with open(SCHEDULE_FILE, "r") as f:
            data = ujson.load(f)
        return data
    except Exception as e:
        print("Error reading schedule:", e)
        return None


def write_schedule(schedule_data):
    """
    Write schedule data received from frontend to JSON file.
    Args:
        schedule_data: dict with feeding_times and days
    Returns: True if successful, False otherwise
    """
    try:
        with open(SCHEDULE_FILE, "w") as f:
            ujson.dump(schedule_data, f)

        # Calculate next feed time and update next_feed.json
        import time
        import next_feed_service

        # New schedule format: feeding_times is a list of dicts, days is a dict of day names to bool
        now = time.localtime()
        now_secs = time.mktime(now)
        next_feed_secs = None
        next_feed_tuple = None
        feeding_times = [t for t in schedule_data.get("feeding_times", []) if t.get("enabled")]
        days = [day for day, enabled in schedule_data.get("days", {}).items() if enabled]
        # Find next scheduled feed time
        weekday_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        for day_offset in range(8):
            check_secs = now_secs + (86400 * day_offset)
            check_date = time.localtime(check_secs)
            weekday = weekday_names[check_date[6]]
            if weekday in days:
                for feed_time in feeding_times:
                    hour = feed_time.get("hour", 0)
                    minute = feed_time.get("minute", 0)
                    ampm = feed_time.get("ampm", "AM")
                    # Convert to 24-hour format
                    if ampm == "PM" and hour < 12:
                        hour += 12
                    if ampm == "AM" and hour == 12:
                        hour = 0
                    # Create time tuple for this feed
                    feed_tuple = (check_date[0], check_date[1], check_date[2], hour, minute, 0, check_date[6], check_date[7])
                    feed_secs = time.mktime(feed_tuple)
                    if feed_secs > now_secs:
                        if next_feed_secs is None or feed_secs < next_feed_secs:
                            next_feed_secs = feed_secs
                            next_feed_tuple = feed_tuple
                if next_feed_tuple:
                    break
        # Write next feed time to next_feed.json
        if next_feed_tuple:
            iso_str = "{:04d}-{:02d}-{:02d}T{:02d}:{:02d}:{:02d}".format(
                next_feed_tuple[0], next_feed_tuple[1], next_feed_tuple[2], 
                next_feed_tuple[3], next_feed_tuple[4], next_feed_tuple[5]
            )
            next_feed_service.write_next_feed(iso_str)
        else:
            next_feed_service.write_next_feed("Not scheduled")
        return True
    except Exception as e:
        print("Error writing schedule:", e)
        return False
