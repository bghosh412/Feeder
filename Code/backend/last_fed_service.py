import time

data_file = 'data/last_fed.txt'

def read_last_fed():
    try:
        with open(data_file, 'r') as f:
            return f.read().strip()
    except:
        return None

def write_last_fed_now():
    try:
        now = time.localtime()
        iso_str = "{:04d}-{:02d}-{:02d}T{:02d}:{:02d}:{:02d}".format(
            now[0], now[1], now[2], now[3], now[4], now[5]
        )
        with open(data_file, 'w') as f:
            f.write(iso_str)
        return True
    except:
        return False
