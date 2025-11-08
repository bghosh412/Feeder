# Wokwi Simulation Test
# Simplified version for online simulator

import time

print("=== Fish Feeder Simulation ===")
print("Starting system test...")

# Simulate motor operation
print("\n1. Testing motor...")
print("   Motor: Rotating forward...")
time.sleep(1)
print("   Motor: Food dispensed!")
print("   Motor: Powered off")

# Simulate RTC
print("\n2. Testing RTC...")
print("   RTC: 2025-11-08 08:00:00")
print("   RTC: Temperature: 23.5°C")

# Simulate feeding check
print("\n3. Checking feeding schedule...")
print("   Feeding times: 08:00, 20:00")
print("   Current time: 08:00")
print("   ✓ Feeding time detected!")

# Simulate notification
print("\n4. Sending notification...")
print("   WiFi: Connecting...")
time.sleep(1)
print("   WiFi: Connected (192.168.1.100)")
print("   Notification: Sent successfully")
print("   WiFi: Disconnected")

# Simulate deep sleep
print("\n5. Entering deep sleep...")
print("   Sleep duration: 30 minutes")
print("   Wake-up time: 08:30:00")

print("\n=== System test completed ===")
print("All components working correctly!")
