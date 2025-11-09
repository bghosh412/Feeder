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
        return True
    except Exception as e:
        print("Error writing schedule:", e)
        return False
