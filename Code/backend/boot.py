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
else:
    print('WiFi not connected. Configuration portal may be active.')

# Final garbage collection before main.py loads
gc.collect()
