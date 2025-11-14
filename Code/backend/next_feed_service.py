NEXT_FEED_FILE = "data/next_feed.txt"

def read_next_feed():
    try:
        with open(NEXT_FEED_FILE, "r") as f:
            raw_time = f.read().strip()
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
    except:
        return "Not scheduled"

def write_next_feed(iso_time):
    try:
        with open(NEXT_FEED_FILE, "w") as f:
            f.write(iso_time)
        return True
    except:
        return False
