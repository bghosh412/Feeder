# Configuration file for Fish Feeder
# All configurable parameters for the ESP8266 fish feeder

# WiFi Configuration
WIFI_SSID = "your_wifi_ssid"
WIFI_PASSWORD = "your_wifi_password"

# Feeding Schedule (24-hour format)
FEEDING_TIMES = [
    (8, 0),   # 8:00 AM
    (20, 0),  # 8:00 PM
]

# Motor Configuration
MOTOR_STEPS_PER_FEEDING = 512  # Full rotation for 28BYJ-48
MOTOR_SPEED_MS = 2  # Delay between steps in milliseconds

# Motor pins (GPIO numbers connected to ULN2003)
MOTOR_PIN_1 = 12  # D6
MOTOR_PIN_2 = 13  # D7
MOTOR_PIN_3 = 14  # D5
MOTOR_PIN_4 = 15  # D8

# RTC Configuration (I2C)
RTC_SDA_PIN = 4   # D2
RTC_SCL_PIN = 5   # D1

# Power Management
DEEP_SLEEP_MINUTES = 30  # Wake up every 30 minutes to check schedule

# Notification Configuration (ntfy)
NTFY_TOPIC = "your_fish_feeder_topic"
NTFY_SERVER = "https://ntfy.sh"
SEND_NOTIFICATIONS = True

# Debug Mode
DEBUG = True
