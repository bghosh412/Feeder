import ujson

QUANTITY_FILE = 'data/quantity.json'

def read_quantity():
    try:
        with open(QUANTITY_FILE, 'r') as f:
            data = ujson.load(f)
        return data.get('quantity', 0)
    except Exception as e:
        print('Error reading quantity:', e)
        return 0

def write_quantity(value):
    try:
        value = max(0, min(15, int(value)))
        with open(QUANTITY_FILE, 'w') as f:
            ujson.dump({'quantity': value}, f)
        return True
    except Exception as e:
        print('Error writing quantity:', e)
        return False
