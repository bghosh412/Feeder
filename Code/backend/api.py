import gc
import services
import last_fed_service
import quantity_service
import next_feed_service
from microdot import Microdot, Response, send_file

app = Microdot()

# Collect garbage at startup
gc.collect()

# Manual JSON encoding helpers (no ujson dependency)
def json_encode(obj):
    """Simple JSON encoder for dict/list/str/int/bool/None"""
    if obj is None:
        return 'null'
    elif isinstance(obj, bool):
        return 'true' if obj else 'false'
    elif isinstance(obj, (int, float)):
        return str(obj)
    elif isinstance(obj, str):
        # Escape special characters
        escaped = obj.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')
        return '"{}"'.format(escaped)
    elif isinstance(obj, dict):
        items = []
        for k, v in obj.items():
            items.append('"{}": {}'.format(k, json_encode(v)))
        return '{' + ', '.join(items) + '}'
    elif isinstance(obj, list):
        items = [json_encode(item) for item in obj]
        return '[' + ', '.join(items) + ']'
    return 'null'

# Feed Now API endpoint
@app.route('/api/feednow', methods=['POST'])
def feed_now(request):
    gc.collect()
    import time
    import lib.notification
    try:
        quantity = quantity_service.read_quantity()
        if quantity > 0:
            quantity -= 1
        quantity_service.write_quantity(quantity)
        last_fed_service.write_last_fed_now()
        now = time.localtime()
        msg = "Feeding done at {:02d}:{:02d}:{:02d}. Feed remaining: {}".format(now[3], now[4], now[5], quantity)
        lib.notification.send_ntfy_notification(msg)
        gc.collect()
        return json_encode({'status': 'ok', 'quantity': quantity})
    except Exception as e:
        gc.collect()
        return Response(json_encode({'error': str(e)}), status=400)

@app.route('/api/feednow', methods=['OPTIONS'])
def feednow_options(request):
    return ''

# Quantity API endpoints
@app.route('/api/quantity', methods=['GET'])
def get_quantity(request):
    gc.collect()
    quantity = quantity_service.read_quantity()
    return json_encode({'quantity': quantity})

@app.route('/api/quantity', methods=['POST'])
def set_quantity(request):
    gc.collect()
    import lib.notification
    try:
        data = request.json
        value = data.get('quantity')
        if value is not None:
            success = quantity_service.write_quantity(value)
            if success:
                msg = "Remaining food quantity updated to {}".format(value)
                lib.notification.send_ntfy_notification(msg)
                gc.collect()
                return json_encode({'status': 'ok'})
            else:
                gc.collect()
                return Response(json_encode({'error': 'Write failed'}), status=500)
        else:
            gc.collect()
            return Response(json_encode({'error': 'Missing quantity'}), status=400)
    except Exception as e:
        gc.collect()
        return Response(json_encode({'error': str(e)}), status=400)

@app.route('/api/quantity', methods=['OPTIONS'])
def quantity_options(request):
    return ''

@app.route('/api/home', methods=['GET'])
def get_home_data(request):
    gc.collect()
    connection_status = 'Online'
    quantity = quantity_service.read_quantity()
    feed_remaining = '{} more feed remaining'.format(quantity)
    last_fed = last_fed_service.read_last_fed()
    battery_status = '40% of the Battery remaining'
    next_feed = next_feed_service.read_next_feed()
    gc.collect()
    return json_encode({
        'connectionStatus': connection_status,
        'feedRemaining': feed_remaining,
        'lastFed': last_fed,
        'batteryStatus': battery_status,
        'nextFeed': next_feed
    })

@app.route('/api/home', methods=['OPTIONS'])
def home_options(request):
    return ''

@app.route('/api/lastfed', methods=['GET'])
def get_last_fed(request):
    gc.collect()
    last_fed = last_fed_service.read_last_fed()
    if last_fed:
        return json_encode({'last_fed_time': last_fed})
    return Response(json_encode({'error': 'Could not read last fed time'}), status=500)

@app.route('/api/lastfed', methods=['POST'])
def set_last_fed(request):
    gc.collect()
    try:
        data = request.json
        last_fed_time = data.get('last_fed_time')
        if last_fed_time:
            with open(last_fed_service.data_file, 'w') as f:
                f.write(last_fed_time)
            gc.collect()
            return json_encode({'status': 'ok'})
        else:
            gc.collect()
            return Response(json_encode({'error': 'Missing last_fed_time'}), status=400)
    except Exception as e:
        gc.collect()
        return Response(json_encode({'error': str(e)}), status=400)

@app.route('/api/lastfed', methods=['OPTIONS'])
def last_fed_options(request):
    return ''

@app.after_request
def enable_cors(request, response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    # Collect garbage after each request to free memory
    gc.collect()
    return response

@app.route('/api/ping', methods=['GET'])
def ping(request):
    gc.collect()
    return json_encode({'status': 'ok'})

@app.route('/api/ping', methods=['OPTIONS'])
def ping_options(request):
    return ''

@app.route('/api/schedule', methods=['GET'])
def get_schedule(request):
    gc.collect()
    data = services.read_schedule()
    if data:
        return json_encode(data)
    return Response(json_encode({'error': 'Could not read schedule'}), status=500)

@app.route('/api/schedule', methods=['POST'])
def set_schedule(request):
    gc.collect()
    try:
        schedule_data = request.json
        success = services.write_schedule(schedule_data)
        if success:
            gc.collect()
            return json_encode({'status': 'ok'})
        else:
            gc.collect()
            return Response(json_encode({'error': 'Write failed'}), status=500)
    except Exception as e:
        gc.collect()
        return Response(json_encode({'error': str(e)}), status=400)

@app.route('/api/schedule', methods=['OPTIONS'])
def schedule_options(request):
    return ''

@app.route('/', methods=['GET'])
def index(request):
    gc.collect()
    return send_file('UI/index.html')

@app.route('/<path:path>', methods=['GET'])
def static_files(request, path):
    gc.collect()
    try:
        return send_file('UI/{}'.format(path))
    except:
        return Response('Not found', status=404)

if __name__ == '__main__':
    app.run(port=5000)
