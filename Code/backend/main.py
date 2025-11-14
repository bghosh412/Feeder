import gc
import time

# Collect garbage before starting
gc.collect()

# Add a small delay to ensure WiFi is fully ready
time.sleep(2)

print('Starting API server...')
print('Free memory:', gc.mem_free())

try:
    import api
    print('API module imported successfully')
    gc.collect()
    print('Free memory after import:', gc.mem_free())
    
    # Start the server
    api.app.run(host='0.0.0.0', port=5000)
except ImportError as e:
    print('Import error:', e)
    print('Make sure all required files are uploaded to the ESP8266')
except MemoryError as e:
    print('Memory error:', e)
    print('ESP8266 ran out of memory. Try reducing features.')
except Exception as e:
    print('Error starting API server:', e)
    import sys
    sys.print_exception(e)
