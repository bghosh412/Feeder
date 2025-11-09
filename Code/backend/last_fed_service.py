import ujson
import time

data_file = 'data/last_fed.json'

def read_last_fed():
    try:
        with open(data_file, 'r') as f:
            data = ujson.load(f)
            return data.get('last_fed_time', None)
    except Exception:
        return None

def write_last_fed_now():
    try:
        now = time.localtime()
        iso_str = "{:04d}-{:02d}-{:02d}T{:02d}:{:02d}:{:02d}".format(
            now[0], now[1], now[2], now[3], now[4], now[5]
        )
        with open(data_file, 'w') as f:
            ujson.dump({'last_fed_time': iso_str}, f)
        return True
    except Exception:
        return False
