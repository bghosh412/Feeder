# Servo calibration service for continuous rotation servo
# Manages min_duty, max_duty, stop_duty values and testing

import json
from machine import Pin, PWM
import time

# Data file path
CALIBRATION_FILE = 'data/calibration.json'

# Default calibration values
DEFAULT_VALUES = {
    'min_duty': 26,   # Full reverse
    'max_duty': 230,  # Full forward
    'stop_duty': 128  # Stop position
}

def read_calibration():
    """Read calibration values from file, return defaults if not found."""
    try:
        with open(CALIBRATION_FILE, 'r') as f:
            data = json.load(f)
            return data
    except:
        return DEFAULT_VALUES.copy()

def write_calibration(data):
    """Write calibration values to file."""
    try:
        with open(CALIBRATION_FILE, 'w') as f:
            json.dump(data, f)
        return True
    except Exception as e:
        print(f"Error writing calibration: {e}")
        return False

def update_calibration(param, value):
    """Update a specific calibration parameter."""
    data = read_calibration()
    if param in ['min_duty', 'max_duty', 'stop_duty']:
        data[param] = int(value)
        return write_calibration(data)
    return False

def move_servo_to_duty(servo_pin, duty):
    """
    Move servo to specific duty value.
    This is used during calibration to test different duty values.
    """
    try:
        servo = PWM(Pin(servo_pin), freq=50)
        duty = int(duty)
        servo.duty(duty)
        print(f"Moved servo to duty: {duty}")
        time.sleep(0.5)  # Brief hold
        # Keep servo active (don't deinit) so user can observe position
        return True
    except Exception as e:
        print(f"Error moving servo: {e}")
        return False

def stop_servo(servo_pin):
    """
    Stop and deinitialize the servo motor.
    This removes power from the servo.
    """
    try:
        servo = PWM(Pin(servo_pin), freq=50)
        servo.deinit()
        print("Servo stopped and deinitialized")
        return True
    except Exception as e:
        print(f"Error stopping servo: {e}")
        return False

def test_servo(servo_pin, test_type, **kwargs):
    """
    Test servo with specified parameters.
    test_type: 'duty' or 'speed'
    For 'duty': duty_type = 'min', 'max', or 'stop'
    For 'speed': speed = -100 to 100
    """
    try:
        calibration = read_calibration()
        servo = PWM(Pin(servo_pin), freq=50)
        
        if test_type == 'duty':
            duty_type = kwargs.get('duty_type', 'stop')
            if duty_type == 'min':
                duty = calibration['min_duty']
            elif duty_type == 'max':
                duty = calibration['max_duty']
            else:  # stop
                duty = calibration['stop_duty']
            servo.duty(duty)
            print(f"Testing {duty_type} duty: {duty}")
            time.sleep(1.5)
        
        elif test_type == 'speed':
            speed = kwargs.get('speed', 0)
            speed = max(-100, min(100, speed))  # Clamp to -100..100
            
            min_duty = calibration['min_duty']
            max_duty = calibration['max_duty']
            stop_duty = calibration['stop_duty']
            
            if speed == 0:
                duty = stop_duty
            elif speed > 0:
                duty = int(stop_duty + (max_duty - stop_duty) * speed / 100)
            else:
                duty = int(stop_duty + (min_duty - stop_duty) * (-speed) / 100)
            
            servo.duty(duty)
            print(f"Testing speed {speed}: duty={duty}")
            time.sleep(1.5)
        
        servo.deinit()
        return True
    except Exception as e:
        print(f"Error testing servo: {e}")
        return False
