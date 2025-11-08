# Test script for stepper motor
# Run this to test motor movement without full system
import sys
sys.path.append('../Code/backend')

from lib.stepper import StepperMotor
import time

# Motor pins - adjust based on your wiring
MOTOR_PIN_1 = 12  # D6
MOTOR_PIN_2 = 13  # D7
MOTOR_PIN_3 = 14  # D5
MOTOR_PIN_4 = 15  # D8

def test_motor():
    """Test stepper motor functionality"""
    print("Initializing motor...")
    motor = StepperMotor(MOTOR_PIN_1, MOTOR_PIN_2, MOTOR_PIN_3, MOTOR_PIN_4)
    
    try:
        print("Test 1: Forward rotation (512 steps)")
        motor.step(512, delay_ms=2)
        time.sleep(1)
        
        print("Test 2: Backward rotation (512 steps)")
        motor.step(-512, delay_ms=2)
        time.sleep(1)
        
        print("Test 3: Rotate 90 degrees")
        motor.rotate_degrees(90, delay_ms=2)
        time.sleep(1)
        
        print("Test 4: Rotate -90 degrees")
        motor.rotate_degrees(-90, delay_ms=2)
        time.sleep(1)
        
        print("Test 5: Full rotation (360 degrees)")
        motor.rotate_degrees(360, delay_ms=2)
        
        print("\nAll tests completed successfully!")
        
    except Exception as e:
        print(f"Error during test: {e}")
    
    finally:
        # Always turn off motor
        motor.off()
        print("Motor powered off")

if __name__ == "__main__":
    test_motor()
