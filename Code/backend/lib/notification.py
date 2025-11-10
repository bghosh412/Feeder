# Notification handler using ntfy
import json

ntfy_topic = 'FF0x98854'

# MicroPython-compatible notification sender
# Try urequests (MicroPython) first, fall back to requests (standard Python)
try:
    import urequests
except ImportError:
    try:
        import requests as urequests
    except ImportError:
        urequests = None

def send_ntfy_notification(message):
    if urequests is None:
        print('urequests not available, cannot send notification')
        return
    url = 'https://ntfy.sh/' + ntfy_topic
    headers = {'Title': 'Auto Feeder'}
    try:
        r = urequests.post(url, data=message, headers=headers)
        r.close()
    except Exception as e:
        print('ntfy notification error:', e)

class NotificationService:
    """Send push notifications via ntfy.sh"""
    
    def __init__(self, server, topic=ntfy_topic):
        """
        Initialize notification service
        server: ntfy server URL (e.g., "https://ntfy.sh")
        topic: unique topic name for your device
        """
        self.server = server.rstrip('/')
        self.topic = topic
        self.url = f"{self.server}/{self.topic}"
    
    def send(self, message, title="Fish Feeder", priority=3):
        """
        Send notification
        priority: 1=min, 3=default, 5=max
        """
        try:
            headers = {
                'Title': title,
                'Priority': str(priority),
                'Tags': 'fish,food'
            }
            
            response = urequests.post(
                self.url,
                data=message.encode('utf-8'),
                headers=headers
            )
            
            success = response.status_code == 200
            response.close()
            return success
            
        except Exception as e:
            print(f"Notification failed: {e}")
            return False
    
    def send_feeding_notification(self, time_str):
        """Send notification after successful feeding"""
        message = f"Fish fed successfully at {time_str}"
        return self.send(message, title="🐟 Feeding Complete")
    
    def send_error_notification(self, error):
        """Send notification on error"""
        message = f"Feeding error: {error}"
        return self.send(message, title="⚠️ Feeder Error", priority=4)
