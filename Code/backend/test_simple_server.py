#!/usr/bin/env python3
"""
Standalone test server to verify HTTP response works correctly.
"""

import socket
import gc

def send_response(conn, status, content_type, body):
    try:
        if isinstance(body, str):
            body_bytes = body.encode('utf-8')
        else:
            body_bytes = body
        
        response = 'HTTP/1.1 {}\r\n'.format(status)
        response += 'Content-Type: {}\r\n'.format(content_type)
        response += 'Connection: close\r\n'
        response += 'Content-Length: {}\r\n'.format(len(body_bytes))
        response += '\r\n'
        
        full_response = response.encode('utf-8') + body_bytes
        conn.sendall(full_response)
        print('Sent {} bytes'.format(len(full_response)))
    except Exception as e:
        print('Error:', e)

def main():
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('0.0.0.0', 5000))
    s.listen(5)
    print('Server running on port 5000')
    
    while True:
        try:
            conn, addr = s.accept()
            print(f'Connection from {addr}')
            
            request = conn.recv(1024)
            print(f'Request: {request[:100]}')
            
            send_response(conn, '200 OK', 'application/json', '{"status": "ok"}')
            conn.close()
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f'Error: {e}')
    
    s.close()

if __name__ == '__main__':
    main()
