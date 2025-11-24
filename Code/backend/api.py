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
    """Improved JSON parser for nested structures"""
    s = s.strip()
    if not s:
        return {}
    
    # Try to use ujson if available (MicroPython)
    try:
        import ujson
        return ujson.loads(s)
    except:
        pass
    
    # Try standard json (Python)
    try:
        import json
        return json.loads(s)
    except:
        pass
    
    # Fallback: basic parser for simple key:value pairs only
    if s.startswith('{') and s.endswith('}'):
        result = {}
        content = s[1:-1].strip()
        if content:
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
    response += 'Access-Control-Allow-Methods: GET, POST, DELETE, OPTIONS\r\n'
    response += 'Access-Control-Allow-Headers: Content-Type\r\n'
    response += 'Connection: close\r\n'
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
        
        # Extract path without query parameters
        if '?' in path:
            path = path.split('?')[0]
        
        print('Request: {} {}'.format(method, path))
        
        # Parse body if POST
        body_data = {}
        if method == 'POST':
            body_start = request.find(b'\r\n\r\n')
            if body_start != -1:
                body = request[body_start+4:].decode()
                if body:
                    print('Raw body:', body)
                    body_data = parse_simple_json(body)
                    print('Parsed body_data:', body_data)
                    print('Type of body_data:', type(body_data))
        
        # OPTIONS handling
        if method == 'OPTIONS':
            send_response(conn, '200 OK', 'text/plain', '')
            return
        
        # Route handling
        # Support both /api/feed and /api/feednow for compatibility
        if path == '/api/feednow' or path == '/api/feed':
            import time
            import lib.notification
            import calibration_service
            
            # Disburse food using calibrated servo settings
            food_dispensed = calibration_service.disburseFood()
            
            if food_dispensed:
                # Update quantity and last fed timestamp
                quantity = quantity_service.read_quantity()
                if quantity > 0:
                    quantity -= 1
                quantity_service.write_quantity(quantity)
                last_fed_service.write_last_fed_now()
                
                # Send notification
                now = time.localtime()
                msg = "Feeding done at {:02d}:{:02d}:{:02d}. Feed remaining: {}".format(now[3], now[4], now[5], quantity)
                lib.notification.send_ntfy_notification(msg)
                
                result = json_encode({'status': 'ok', 'quantity': quantity})
                send_response(conn, '200 OK', 'application/json', result)
            else:
                # Food dispensing failed
                result = json_encode({'status': 'error', 'message': 'Failed to dispense food'})
                send_response(conn, '500 Internal Server Error', 'application/json', result)
            
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
            
        elif path == '/api/ping' or path == '/api/status':
            send_response(conn, '200 OK', 'application/json', json_encode({'status': 'ok', 'message': 'Server is running'}))
            
        elif path == '/api/schedule' or path == '/api/schedules' or path.startswith('/api/schedule/'):
            if method == 'GET':
                data = services.read_schedule()
                result = json_encode(data) if data else json_encode({'error': 'Could not read schedule'})
                send_response(conn, '200 OK', 'application/json', result)
            elif method == 'DELETE':
                # For now, just return success - implement delete logic as needed
                send_response(conn, '200 OK', 'application/json', json_encode({'status': 'ok', 'message': 'Schedule deleted'}))
            else:
                # write_schedule already calculates and saves next feed time
                print('Received schedule data:', body_data)
                result = services.write_schedule(body_data)
                if result:
                    send_response(conn, '200 OK', 'application/json', json_encode({'status': 'ok'}))
                else:
                    print('Failed to write schedule')
                    send_response(conn, '500 Internal Server Error', 'application/json', json_encode({'error': 'Failed to save schedule'}))
        
        elif path == '/api/calibration/get':
            if method == 'GET':
                try:
                    import calibration_service
                    data = calibration_service.get_current_calibration()
                    send_response(conn, '200 OK', 'application/json', json_encode(data))
                except Exception as e:
                    print('Error reading calibration:', e)
                    send_response(conn, '500 Internal Server Error', 'application/json', json_encode({'error': str(e)}))
            else:
                send_response(conn, '405 Method Not Allowed', 'application/json', json_encode({'error': 'Only GET allowed'}))
        
        elif path == '/api/calibration/save':
            if method == 'POST':
                try:
                    import calibration_service
                    duty_cycle = body_data.get('duty_cycle')
                    pulse_duration = body_data.get('pulse_duration')
                    
                    if duty_cycle is not None and pulse_duration is not None:
                        success = calibration_service.save_calibration(duty_cycle, pulse_duration)
                        if success:
                            send_response(conn, '200 OK', 'application/json', json_encode({'status': 'ok', 'duty_cycle': duty_cycle, 'pulse_duration': pulse_duration}))
                        else:
                            send_response(conn, '500 Internal Server Error', 'application/json', json_encode({'error': 'Failed to save'}))
                    else:
                        send_response(conn, '400 Bad Request', 'application/json', json_encode({'error': 'Missing parameters'}))
                except Exception as e:
                    print('Error saving calibration:', e)
                    send_response(conn, '500 Internal Server Error', 'application/json', json_encode({'error': str(e)}))
            else:
                send_response(conn, '405 Method Not Allowed', 'application/json', json_encode({'error': 'Only POST allowed'}))
        
        elif path == '/api/calibration/adjust_duty':
            if method == 'POST':
                try:
                    import calibration_service
                    increment = body_data.get('increment', 1)
                    duty_cycle, pulse_duration = calibration_service.adjust_duty_cycle(increment)
                    send_response(conn, '200 OK', 'application/json', json_encode({'status': 'ok', 'duty_cycle': duty_cycle, 'pulse_duration': pulse_duration}))
                except Exception as e:
                    print('Error adjusting duty cycle:', e)
                    send_response(conn, '500 Internal Server Error', 'application/json', json_encode({'error': str(e)}))
            else:
                send_response(conn, '405 Method Not Allowed', 'application/json', json_encode({'error': 'Only POST allowed'}))
        
        elif path == '/api/calibration/adjust_duration':
            if method == 'POST':
                try:
                    import calibration_service
                    increment = body_data.get('increment', 5)
                    duty_cycle, pulse_duration = calibration_service.adjust_pulse_duration(increment)
                    send_response(conn, '200 OK', 'application/json', json_encode({'status': 'ok', 'duty_cycle': duty_cycle, 'pulse_duration': pulse_duration}))
                except Exception as e:
                    print('Error adjusting pulse duration:', e)
                    send_response(conn, '500 Internal Server Error', 'application/json', json_encode({'error': str(e)}))
            else:
                send_response(conn, '405 Method Not Allowed', 'application/json', json_encode({'error': 'Only POST allowed'}))
        
        elif path == '/api/calibration/test':
            if method == 'POST':
                try:
                    import calibration_service
                    result = calibration_service.test_calibration()
                    send_response(conn, '200 OK', 'application/json', json_encode(result))
                except Exception as e:
                    print('Error testing calibration:', e)
                    send_response(conn, '500 Internal Server Error', 'application/json', json_encode({'error': str(e)}))
            else:
                send_response(conn, '405 Method Not Allowed', 'application/json', json_encode({'error': 'Only POST allowed'}))
        
        elif path == '/api/calibrate/left' or path == '/api/calibrate/right':
            if method == 'POST':
                try:
                    # Check if running on actual hardware (ESP8266/ESP32)
                    try:
                        from machine import Pin
                        on_hardware = True
                    except ImportError:
                        on_hardware = False
                        print('Warning: Not running on ESP hardware, motor control disabled')
                    
                    if on_hardware:
                        import config
                        from lib.stepper import StepperMotor
                        
                        # Get speed from request
                        speed = body_data.get('speed', 'medium')
                        
                        # Map speed to delay_ms (lower delay = faster)
                        speed_map = {
                            'very_slow': 10,
                            'slow': 5,
                            'medium': 2,
                            'fast': 1,
                            'very_fast': 0
                        }
                        delay_ms = speed_map.get(speed, 2)
                        
                        # Initialize motor
                        motor = StepperMotor(
                            config.MOTOR_PIN_1,
                            config.MOTOR_PIN_2,
                            config.MOTOR_PIN_3,
                            config.MOTOR_PIN_4
                        )
                        
                        # Determine direction and steps
                        # 512 steps = 1/8 rotation (about 45 degrees)
                        steps = 512
                        if path == '/api/calibrate/left':
                            steps = -steps  # Negative for counter-clockwise
                        
                        print('Calibrating motor: {} steps at {} ms delay'.format(steps, delay_ms))
                        motor.step(steps, delay_ms)
                        motor.off()  # Turn off motor to save power
                        
                        direction = 'left' if path == '/api/calibrate/left' else 'right'
                        result = json_encode({'status': 'ok', 'message': 'Motor moved {}'.format(direction)})
                    else:
                        # Simulation mode - just return success without moving motor
                        direction = 'left' if path == '/api/calibrate/left' else 'right'
                        speed = body_data.get('speed', 'medium')
                        print('Simulation: Would move motor {} at {} speed'.format(direction, speed))
                        result = json_encode({'status': 'ok', 'message': 'Motor moved {} (simulation mode)'.format(direction)})
                    
                    send_response(conn, '200 OK', 'application/json', result)
                    
                except Exception as e:
                    print('Error in calibration:', e)
                    error_msg = 'Calibration error: {}'.format(str(e))
                    send_response(conn, '500 Internal Server Error', 'application/json', json_encode({'status': 'error', 'message': error_msg}))
            else:
                send_response(conn, '405 Method Not Allowed', 'application/json', json_encode({'error': 'Only POST allowed'}))
                
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
                # Stream file in chunks to avoid memory issues
                with open('UI/index.html', 'rb') as f:
                    # Get file size
                    import os
                    file_size = os.stat('UI/index.html')[6]
                    
                    # Send headers
                    response = 'HTTP/1.1 200 OK\r\n'
                    response += 'Content-Type: text/html\r\n'
                    response += 'Access-Control-Allow-Origin: *\r\n'
                    response += 'Connection: close\r\n'
                    response += 'Content-Length: {}\r\n'.format(file_size)
                    response += '\r\n'
                    conn.send(response.encode())
                    
                    # Stream file in 512 byte chunks
                    while True:
                        chunk = f.read(512)
                        if not chunk:
                            break
                        conn.send(chunk)
                        gc.collect()
            except Exception as e:
                print('Error serving index.html:', e)
                error_msg = 'Error: {}'.format(str(e))
                send_response(conn, '500 Internal Server Error', 'text/html', '<html><body><h1>Error</h1><p>{}</p></body></html>'.format(error_msg))
                
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
                
                print('Serving file:', file_path)
                
                # Stream file in chunks to avoid memory issues
                import os
                file_size = os.stat(file_path)[6]
                
                # Send headers
                response = 'HTTP/1.1 200 OK\r\n'
                response += 'Content-Type: {}\r\n'.format(content_type)
                response += 'Access-Control-Allow-Origin: *\r\n'
                response += 'Connection: close\r\n'
                response += 'Content-Length: {}\r\n'.format(file_size)
                response += '\r\n'
                conn.send(response.encode())
                
                # Stream file in 512 byte chunks
                with open(file_path, 'rb') as f:
                    while True:
                        chunk = f.read(512)
                        if not chunk:
                            break
                        conn.send(chunk)
                        gc.collect()
                        
            except Exception as e:
                print('Error serving file {}: {}'.format(file_path, e))
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
        # Get actual IP address if host is 0.0.0.0
        if host == '0.0.0.0':
            try:
                import network
                sta = network.WLAN(network.STA_IF)
                if sta.isconnected():
                    actual_ip = sta.ifconfig()[0]
                    print('Server will run on {}:{}'.format(actual_ip, port))
                else:
                    actual_ip = '0.0.0.0'
                    print('Not connected to WiFi, using 0.0.0.0')
            except:
                actual_ip = '0.0.0.0'
                print('Could not determine IP, using 0.0.0.0')
        else:
            actual_ip = host
        
        addr = socket.getaddrinfo(host, port)[0][-1]
        self.socket = socket.socket()
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # SO_KEEPALIVE not supported on ESP8266 MicroPython
        self.socket.bind(addr)
        self.socket.listen(5)
        print('Server running on {}:{}'.format(actual_ip, port))
        
        # Send notification with server URL
        try:
            import lib.notification
            url = 'http://{}:{}'.format(actual_ip, port)
            import time
            now = time.localtime()
            time_str = "{:02d}:{:02d}:{:02d}".format(now[3], now[4], now[5])
            msg = 'Feeder started at {} and can be accessed at {}'.format(time_str, url)
            lib.notification.send_ntfy_notification(msg)
            print('Startup notification sent:', msg)
        except Exception as e:
            print('Could not send startup notification:', e)
        
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
                
                # Close connection (shutdown not always available on ESP8266)
                try:
                    conn.close()
                except:
                    pass
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
