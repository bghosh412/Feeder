# Test script for DS3231 RTC
# Run this to test RTC functionality
import sys
sys.path.append('../Code/backend')

from lib.rtc_handler import DS3231
import time

# RTC pins
RTC_SDA_PIN = 4   # D2
RTC_SCL_PIN = 5   # D1

def test_rtc():
    """Test DS3231 RTC functionality"""
    print("Initializing RTC...")
    rtc = DS3231(RTC_SDA_PIN, RTC_SCL_PIN)
    
    try:
        # Test 1: Read current time
        print("\nTest 1: Reading current time")
        current_time = rtc.get_time()
        year, month, day, hour, minute, second, weekday = current_time
        print(f"Current time: {year}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:{second:02d}")
        print(f"Weekday: {weekday}")
        
        # Test 2: Read temperature
        print("\nTest 2: Reading temperature")
        temp = rtc.get_temperature()
        print(f"Temperature: {temp}°C")
        
        # Test 3: Set time (optional - uncomment if needed)
        # print("\nTest 3: Setting time to 2025-11-08 12:00:00")
        # rtc.set_time(2025, 11, 8, 12, 0, 0, 5)  # Friday
        # time.sleep(1)
        # current_time = rtc.get_time()
        # year, month, day, hour, minute, second, weekday = current_time
        # print(f"New time: {year}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:{second:02d}")
        
        # Test 4: Monitor time for 5 seconds
        print("\nTest 4: Monitoring time updates")
        for i in range(5):
            current_time = rtc.get_time()
            year, month, day, hour, minute, second, weekday = current_time
            print(f"{hour:02d}:{minute:02d}:{second:02d}")
            time.sleep(1)
        
        print("\nAll RTC tests completed successfully!")
        
    except Exception as e:
        print(f"Error during test: {e}")

if __name__ == "__main__":
    test_rtc()
