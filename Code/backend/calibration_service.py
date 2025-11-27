# Servo calibration service for continuous rotation servo
# Manages duty cycle and pulse duration for food dispensing

from machine import Pin, PWM
import time

# Data file path
CALIBRATION_FILE = 'data/calibration.txt'
SERVO_PIN = 18  # GPIO pin for servo

# Default calibration values
DEFAULT_DUTY_CYCLE = 80
DEFAULT_PULSE_DURATION = 10  # milliseconds

def read_calibration():
    """Read duty cycle and pulse duration from file.
    Returns: tuple (duty_cycle, pulse_duration_ms)
    """
    try:
        with open(CALIBRATION_FILE, 'r') as f:
            data = f.read().strip()
            parts = data.split(',')
            duty_cycle = int(parts[0])
            pulse_duration = int(parts[1])
            return duty_cycle, pulse_duration
    except:
        # Return defaults if file doesn't exist or is corrupt
        return DEFAULT_DUTY_CYCLE, DEFAULT_PULSE_DURATION

def save_calibration(duty_cycle, pulse_duration):
    """Save duty cycle and pulse duration to file.
    Args:
        duty_cycle: PWM duty cycle value
        pulse_duration: pulse duration in milliseconds
    """
    try:
        with open(CALIBRATION_FILE, 'w') as f:
            f.write(f"{duty_cycle},{pulse_duration}")
        return True
    except Exception as e:
        print(f"Error saving calibration: {e}")
        return False

def adjust_duty_cycle(increment):
    """Adjust duty cycle by increment value.
    Args:
        increment: positive to increase, negative to decrease
    Returns: tuple (new_duty_cycle, pulse_duration)
    """
    duty_cycle, pulse_duration = read_calibration()
    duty_cycle += increment
    # Clamp duty cycle to reasonable range (0-1023 for ESP32)
    duty_cycle = max(0, min(1023, duty_cycle))
    save_calibration(duty_cycle, pulse_duration)
    return duty_cycle, pulse_duration

def adjust_pulse_duration(increment):
    """Adjust pulse duration by increment value (in milliseconds).
    Args:
        increment: positive to increase, negative to decrease
    Returns: tuple (duty_cycle, new_pulse_duration)
    """
    duty_cycle, pulse_duration = read_calibration()
    pulse_duration += increment
    # Clamp pulse duration to reasonable range (1-1000ms)
    pulse_duration = max(1, min(1000, pulse_duration))
    save_calibration(duty_cycle, pulse_duration)
    return duty_cycle, pulse_duration

def get_current_calibration():
    """Get current calibration values as a dictionary."""
    duty_cycle, pulse_duration = read_calibration()
    return {
        'duty_cycle': duty_cycle,
        'pulse_duration': pulse_duration
    }

def disburseFood():
    """Disburse food using calibrated servo settings.
    Reads duty cycle and pulse duration from file, runs servo, then deinits.
    """
    import gc
    
    # Free memory before servo operation
    gc.collect()
    
    duty_cycle, pulse_duration = read_calibration()
    
    try:
        # Initialize servo PWM
        servo = PWM(Pin(SERVO_PIN), freq=50)
        
        # Apply duty cycle for specified duration
        servo.duty(duty_cycle)
        print(f"Dispensing food: duty={duty_cycle}, duration={pulse_duration}ms")
        time.sleep_ms(pulse_duration)
        
        # Deinitialize to stop motor
        servo.deinit()
        print("Food dispensed, servo deinitialized")
        
        # Clean up after servo operation
        gc.collect()
        
        return True
        
    except Exception as e:
        print(f"Error dispensing food: {e}")
        # Clean up on error too
        gc.collect()
        return False

def test_calibration():
    """Test current calibration by running servo with current settings.
    Returns current calibration values after test.
    """
    import gc
    
    # Free memory before test
    gc.collect()
    
    duty_cycle, pulse_duration = read_calibration()
    
    try:
        # Initialize servo PWM
        servo = PWM(Pin(SERVO_PIN), freq=50)
        
        # Apply duty cycle for specified duration
        servo.duty(duty_cycle)
        print(f"Testing: duty={duty_cycle}, duration={pulse_duration}ms")
        time.sleep_ms(pulse_duration)
        
        # Deinitialize to stop motor
        servo.deinit()
        print("Test complete, servo deinitialized")
        
        # Clean up after test
        gc.collect()
        
        return {
            'success': True,
            'duty_cycle': duty_cycle,
            'pulse_duration': pulse_duration
        }
        
    except Exception as e:
        print(f"Error testing calibration: {e}")
        gc.collect()
        return {
            'success': False,
            'error': str(e)
        }
