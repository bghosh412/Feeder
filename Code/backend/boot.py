# boot.py - MicroPython startup file for ESP8266
# Initiates WiFi connection using WifiManager

import gc
from wifi_manager import WifiManager

# Collect garbage at startup
gc.collect()

# You can customize SSID and password below if needed
SSID = 'WifiManager'
PASSWORD = 'wifimanager'
print('Starting WiFi connection...')
wifi = WifiManager()
wifi.connect()

# Collect garbage after WiFi connection
gc.collect()

# Optionally, print IP address if connected
if wifi.is_connected():
    print('Connected to WiFi. IP:', wifi.get_address()[0])
    
    # Set timezone to India/Kolkata (UTC+5:30)
    try:
        import ntptime
        import machine
        import time
        
        print('Syncing time with NTP server...')
        ntptime.settime()  # Sync with NTP server (gets UTC time)
        
        # India/Kolkata is UTC+5:30 (19800 seconds offset)
        # ESP32/ESP8266 stores time in UTC, so we need to add the offset
        IST_OFFSET = 19800  # 5 hours 30 minutes in seconds
        
        # Get current UTC time
        current_time = time.time()
        
        # Add IST offset
        ist_time = current_time + IST_OFFSET
        
        # Convert to struct_time
        tm = time.localtime(ist_time)
        
        # Set RTC with IST time
        rtc = machine.RTC()
        rtc.datetime((tm[0], tm[1], tm[2], tm[6], tm[3], tm[4], tm[5], 0))
        
        print('Time synced to India/Kolkata timezone')
        print('Current time:', time.localtime())
        
    except Exception as e:
        print('Failed to sync time:', e)
        print('Continuing without time sync...')
else:
    print('WiFi not connected. Configuration portal may be active.')

# Final garbage collection before main.py loads
gc.collect()
