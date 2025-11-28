# System endpoint handlers
import gc
import utime as time

def handle_events(conn, method, query_params):
    """Handle events endpoint"""
    from json_utils import json_encode
    from http_utils import send_response
    import event_log_service
    
    if method == 'GET':
        # Get optional limit parameter
        limit = 100  # Default to all events
        if query_params and 'limit' in query_params:
            try:
                limit = int(query_params['limit'])
            except:
                pass
        
        events = event_log_service.read_events(limit)
        send_response(conn, '200 OK', 'application/json', json_encode({'events': events}))
    elif method == 'DELETE':
        # Clear event log
        event_log_service.clear_events()
        send_response(conn, '200 OK', 'application/json', json_encode({'status': 'ok', 'message': 'Events cleared'}))
    else:
        send_response(conn, '405 Method Not Allowed', 'application/json', json_encode({'error': 'Method not allowed'}))

def handle_ping(conn):
    """Handle ping/status endpoint"""
    from json_utils import json_encode
    from http_utils import send_response
    
    send_response(conn, '200 OK', 'application/json', json_encode({'status': 'ok', 'message': 'Server is running'}))

def handle_system_memory(conn, method):
    """Handle system memory status"""
    from json_utils import json_encode
    from http_utils import send_response
    
    if method == 'GET':
        try:
            gc.collect()
            free_mem = gc.mem_free()
            send_response(conn, '200 OK', 'application/json', json_encode({'free_memory': free_mem}))
        except Exception as e:
            print('Error reading memory:', e)
            send_response(conn, '500 Internal Server Error', 'application/json', json_encode({'error': str(e)}))
    else:
        send_response(conn, '405 Method Not Allowed', 'application/json', json_encode({'error': 'Only GET allowed'}))

def handle_system_uptime(conn, method, server_start_time):
    """Handle system uptime"""
    from json_utils import json_encode
    from http_utils import send_response
    
    if method == 'GET':
        try:
            uptime_seconds = int(time.time() - server_start_time)
            send_response(conn, '200 OK', 'application/json', json_encode({'uptime': uptime_seconds}))
        except Exception as e:
            print('Error reading uptime:', e)
            send_response(conn, '500 Internal Server Error', 'application/json', json_encode({'error': str(e)}))
    else:
        send_response(conn, '405 Method Not Allowed', 'application/json', json_encode({'error': 'Only GET allowed'}))

def handle_config(conn, method):
    """Handle configuration endpoint"""
    from json_utils import json_encode
    from http_utils import send_response
    
    if method == 'GET':
        try:
            import config
            result = {
                'ntfy_topic': config.NTFY_TOPIC if hasattr(config, 'NTFY_TOPIC') else 'N/A',
                'ntfy_server': config.NTFY_SERVER if hasattr(config, 'NTFY_SERVER') else 'N/A'
            }
            send_response(conn, '200 OK', 'application/json', json_encode(result))
        except Exception as e:
            print('Error reading config:', e)
            send_response(conn, '500 Internal Server Error', 'application/json', json_encode({'error': str(e)}))
    else:
        send_response(conn, '405 Method Not Allowed', 'application/json', json_encode({'error': 'Only GET allowed'}))

def handle_reboot(conn):
    """Handle reboot endpoint"""
    from json_utils import json_encode
    from http_utils import send_response
    import machine
    
    send_response(conn, '200 OK', 'application/json', json_encode({'status': 'ok', 'message': 'Rebooting...'}))
    machine.reset()
