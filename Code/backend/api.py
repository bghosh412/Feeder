import gc
import socket
import services
import last_fed_service
import quantity_service
import next_feed_service

gc.collect()

# Manual JSON encoding
def json_encode(obj):
    if obj is None:
        return 'null'
    elif isinstance(obj, bool):
        return 'true' if obj else 'false'
    elif isinstance(obj, (int, float)):
        return str(obj)
    elif isinstance(obj, str):
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

def parse_simple_json(s):
    """Very basic JSON parser"""
    s = s.strip()
    if s.startswith('{') and s.endswith('}'):
        result = {}
        content = s[1:-1].strip()
        if content:
            # Simple parser - works for basic key:value pairs
            pairs = content.split(',')
            for pair in pairs:
                if ':' in pair:
                    k, v = pair.split(':', 1)
                    k = k.strip().strip('"')
                    v = v.strip().strip('"')
                    try:
                        v = int(v)
                    except:
                        pass
                    result[k] = v
        return result
    return {}

def send_response(conn, status, content_type, body):
    gc.collect()
    response = 'HTTP/1.1 {}\r\n'.format(status)
    response += 'Content-Type: {}\r\n'.format(content_type)
    response += 'Access-Control-Allow-Origin: *\r\n'
    response += 'Access-Control-Allow-Methods: GET, POST, OPTIONS\r\n'
    response += 'Access-Control-Allow-Headers: Content-Type\r\n'
    response += 'Content-Length: {}\r\n'.format(len(body))
    response += '\r\n'
    conn.send(response.encode())
    conn.send(body.encode() if isinstance(body, str) else body)
    gc.collect()

def handle_request(conn, request):
    gc.collect()
    try:
        lines = request.split(b'\r\n')
        if not lines:
            return
            
        request_line = lines[0].decode()
        parts = request_line.split()
        if len(parts) < 2:
            return
            
        method, path = parts[0], parts[1]
        
        # Parse body if POST
        body_data = {}
        if method == 'POST':
            body_start = request.find(b'\r\n\r\n')
            if body_start != -1:
                body = request[body_start+4:].decode()
                if body:
                    body_data = parse_simple_json(body)
        
        # OPTIONS handling
        if method == 'OPTIONS':
            send_response(conn, '200 OK', 'text/plain', '')
            return
        
        # Route handling
        if path == '/api/feednow':
            import time
            import lib.notification
            quantity = quantity_service.read_quantity()
            if quantity > 0:
                quantity -= 1
            quantity_service.write_quantity(quantity)
            last_fed_service.write_last_fed_now()
            now = time.localtime()
            msg = "Feeding done at {:02d}:{:02d}:{:02d}. Feed remaining: {}".format(now[3], now[4], now[5], quantity)
            lib.notification.send_ntfy_notification(msg)
            result = json_encode({'status': 'ok', 'quantity': quantity})
            send_response(conn, '200 OK', 'application/json', result)
            
        elif path == '/api/quantity':
            if method == 'GET':
                quantity = quantity_service.read_quantity()
                result = json_encode({'quantity': quantity})
                send_response(conn, '200 OK', 'application/json', result)
            else:
                import lib.notification
                value = body_data.get('quantity')
                if value is not None:
                    quantity_service.write_quantity(value)
                    msg = "Remaining food quantity updated to {}".format(value)
                    lib.notification.send_ntfy_notification(msg)
                    result = json_encode({'status': 'ok'})
                    send_response(conn, '200 OK', 'application/json', result)
                else:
                    send_response(conn, '400 Bad Request', 'application/json', json_encode({'error': 'Missing quantity'}))
                    
        elif path == '/api/home':
            quantity = quantity_service.read_quantity()
            last_fed = last_fed_service.read_last_fed()
            next_feed = next_feed_service.read_next_feed()
            result = json_encode({
                'connectionStatus': 'Online',
                'feedRemaining': '{} more feed remaining'.format(quantity),
                'lastFed': last_fed,
                'batteryStatus': '40% of the Battery remaining',
                'nextFeed': next_feed
            })
            send_response(conn, '200 OK', 'application/json', result)
            
        elif path == '/api/ping':
            send_response(conn, '200 OK', 'application/json', json_encode({'status': 'ok'}))
            
        elif path == '/api/schedule':
            if method == 'GET':
                data = services.read_schedule()
                result = json_encode(data) if data else json_encode({'error': 'Could not read schedule'})
                send_response(conn, '200 OK', 'application/json', result)
            else:
                services.write_schedule(body_data)
                send_response(conn, '200 OK', 'application/json', json_encode({'status': 'ok'}))
                
        elif path == '/api/lastfed':
            if method == 'GET':
                last_fed = last_fed_service.read_last_fed()
                result = json_encode({'last_fed_time': last_fed}) if last_fed else json_encode({'error': 'Could not read'})
                send_response(conn, '200 OK', 'application/json', result)
            else:
                last_fed_time = body_data.get('last_fed_time')
                if last_fed_time:
                    with open(last_fed_service.data_file, 'w') as f:
                        f.write(last_fed_time)
                    send_response(conn, '200 OK', 'application/json', json_encode({'status': 'ok'}))
                else:
                    send_response(conn, '400 Bad Request', 'application/json', json_encode({'error': 'Missing last_fed_time'}))
                    
        elif path == '/' or path == '/index.html':
            try:
                with open('UI/index.html', 'r') as f:
                    send_response(conn, '200 OK', 'text/html', f.read())
            except:
                send_response(conn, '404 Not Found', 'text/plain', 'Not Found')
                
        else:
            # Try to serve static file
            try:
                file_path = 'UI' + path
                content_type = 'text/html'
                if path.endswith('.css'):
                    content_type = 'text/css'
                elif path.endswith('.js'):
                    content_type = 'application/javascript'
                elif path.endswith('.png'):
                    content_type = 'image/png'
                elif path.endswith('.jpg') or path.endswith('.jpeg'):
                    content_type = 'image/jpeg'
                    
                with open(file_path, 'rb') as f:
                    content = f.read()
                    send_response(conn, '200 OK', content_type, content)
            except:
                send_response(conn, '404 Not Found', 'text/plain', 'Not Found')
        
        gc.collect()
    except Exception as e:
        print('Error handling request:', e)
        try:
            send_response(conn, '500 Internal Server Error', 'application/json', json_encode({'error': str(e)}))
        except:
            pass

class SimpleServer:
    def __init__(self):
        self.socket = None
        
    def run(self, host='0.0.0.0', port=5000):
        addr = socket.getaddrinfo(host, port)[0][-1]
        self.socket = socket.socket()
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(addr)
        self.socket.listen(5)
        print('Server running on {}:{}'.format(host, port))
        
        while True:
            try:
                conn, addr = self.socket.accept()
                print('Connection from', addr)
                conn.settimeout(5.0)
                
                # Read request
                request = b''
                while True:
                    try:
                        chunk = conn.recv(1024)
                        if not chunk:
                            break
                        request += chunk
                        # Check if we have full request
                        if b'\r\n\r\n' in request:
                            # Check if there's a body
                            if b'Content-Length:' in request:
                                header_end = request.find(b'\r\n\r\n')
                                headers = request[:header_end].decode()
                                for line in headers.split('\r\n'):
                                    if line.startswith('Content-Length:'):
                                        content_length = int(line.split(':')[1].strip())
                                        body_received = len(request) - header_end - 4
                                        if body_received >= content_length:
                                            break
                            else:
                                break
                    except:
                        break
                
                if request:
                    handle_request(conn, request)
                
                conn.close()
                gc.collect()
            except Exception as e:
                print('Server error:', e)
                try:
                    conn.close()
                except:
                    pass
                gc.collect()

app = SimpleServer()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
