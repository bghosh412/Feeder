QUANTITY_FILE = 'data/quantity.txt'

def read_quantity():
    try:
        with open(QUANTITY_FILE, 'r') as f:
            return int(f.read().strip())
    except:
        return 0

def write_quantity(value):
    try:
        value = max(0, min(15, int(value)))
        with open(QUANTITY_FILE, 'w') as f:
            f.write(str(value))
        return True
    except:
        return False
