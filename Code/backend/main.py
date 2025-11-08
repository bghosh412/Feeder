# Main entry point for ESP8266 Fish Feeder
import machine
import network
import time
import esp
from lib.stepper import StepperMotor
from lib.rtc_handler import DS3231
from lib.notification import NotificationService
import config

# Disable debug output to save power
if not config.DEBUG:
    esp.osdebug(None)

def connect_wifi():
    """Connect to WiFi network"""
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    if not wlan.isconnected():
        print('Connecting to WiFi...')
        wlan.connect(config.WIFI_SSID, config.WIFI_PASSWORD)
        
        timeout = 10
        while not wlan.isconnected() and timeout > 0:
            time.sleep(1)
            timeout -= 1
    
    if wlan.isconnected():
        print('WiFi connected:', wlan.ifconfig()[0])
        return True
    else:
        print('WiFi connection failed')
        return False

def disconnect_wifi():
    """Disconnect WiFi to save power"""
    wlan = network.WLAN(network.STA_IF)
    wlan.active(False)

def feed():
    """Execute feeding routine"""
    print("Starting feeding routine...")
    
    # Initialize motor
    motor = StepperMotor(
        config.MOTOR_PIN_1,
        config.MOTOR_PIN_2,
        config.MOTOR_PIN_3,
        config.MOTOR_PIN_4
    )
    
    try:
        # Rotate motor to dispense food
        motor.step(config.MOTOR_STEPS_PER_FEEDING, config.MOTOR_SPEED_MS)
        print("Food dispensed successfully")
        success = True
        error_msg = None
        
    except Exception as e:
        print(f"Feeding error: {e}")
        success = False
        error_msg = str(e)
    
    finally:
        # Always turn off motor to save power
        motor.off()
    
    return success, error_msg

def should_feed(current_time, rtc):
    """Check if it's time to feed based on schedule"""
    year, month, day, hour, minute, second, weekday = current_time
    
    for feed_hour, feed_minute in config.FEEDING_TIMES:
        # Check if current time matches feeding time (within 1 minute)
        if hour == feed_hour and minute == feed_minute:
            return True
    
    return False

def send_notification(message, is_error=False):
    """Send notification via ntfy"""
    if not config.SEND_NOTIFICATIONS:
        return
    
    try:
        # Connect to WiFi for notification
        if connect_wifi():
            notifier = NotificationService(config.NTFY_SERVER, config.NTFY_TOPIC)
            
            if is_error:
                notifier.send_error_notification(message)
            else:
                notifier.send_feeding_notification(message)
            
            # Small delay to ensure message is sent
            time.sleep(2)
            disconnect_wifi()
    except Exception as e:
        print(f"Notification error: {e}")

def main():
    """Main program loop"""
    print("Fish Feeder starting...")
    
    # Initialize RTC
    rtc = DS3231(config.RTC_SDA_PIN, config.RTC_SCL_PIN)
    
    # Get current time
    current_time = rtc.get_time()
    year, month, day, hour, minute, second, weekday = current_time
    time_str = f"{year}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:{second:02d}"
    print(f"Current time: {time_str}")
    
    # Check if it's feeding time
    if should_feed(current_time, rtc):
        print("Feeding time detected!")
        
        # Execute feeding
        success, error_msg = feed()
        
        # Send notification
        if success:
            send_notification(time_str, is_error=False)
        else:
            send_notification(error_msg, is_error=True)
    else:
        print("Not feeding time, going back to sleep")
    
    # Enter deep sleep to conserve battery
    print(f"Entering deep sleep for {config.DEEP_SLEEP_MINUTES} minutes...")
    
    # Deep sleep in microseconds
    machine.deepsleep(config.DEEP_SLEEP_MINUTES * 60 * 1000000)

# Run main program
if __name__ == "__main__":
    main()
