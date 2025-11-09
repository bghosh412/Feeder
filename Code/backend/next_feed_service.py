import ujson
import time

NEXT_FEED_FILE = "data/next_feed.json"

# Read next feed time and return formatted string
def read_next_feed():
    try:
        # Try to open file, if it doesn't exist, return default
        try:
            f = open(NEXT_FEED_FILE, "r")
            f.close()
        except:
            return "Not scheduled"
        with open(NEXT_FEED_FILE, "r") as f:
            data = ujson.load(f)
        raw_time = data.get("next_feed_time")
        if not raw_time or raw_time == "Not scheduled":
            return "Not scheduled"
        # Parse and format manually from ISO string: YYYY-MM-DDTHH:MM:SS
        try:
            date_part, time_part = raw_time.split('T')
            year, month, day = date_part.split('-')
            hour, minute, second = time_part.split(':')
            # Format as "Nov 9th, 10:00 PM"
            months = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
            h = int(hour)
            m = int(minute)
            ampm = "AM" if h < 12 else "PM"
            if h == 0:
                h = 12
            elif h > 12:
                h -= 12
            formatted = "{} {}th, {:02d}:{:02d} {}".format(months[int(month)], day, h, m, ampm)
            return formatted
        except:
            return raw_time
    except Exception as e:
        print("Error reading next feed:", e)
        return "Not scheduled"

# Write next feed time (expects ISO string)
def write_next_feed(iso_time):
    try:
        with open(NEXT_FEED_FILE, "w") as f:
            ujson.dump({"next_feed_time": iso_time}, f)
        return True
    except Exception as e:
        print("Error writing next feed:", e)
        return False
