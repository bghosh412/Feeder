# Test script for microstepping servo control on ESP32 (MicroPython)
# Microstepping: 80 duty for 10ms, then hold at 73 duty for 1 second, repeat
# Goal: Move 22.5 degrees and count cycles needed for calibration
# Connect servo signal to GPIO 18
# Power servo with 5V (not ESP32 3.3V!)
# Press Ctrl+C or reset board to stop

from machine import Pin, PWM
import time

SERVO_PIN = 18  # Use GPIO18 (D18)
STOP_DUTY = 75  # Stop/neutral position (initial)
PULSE_DUTY = 71  # Movement duty cycle (104)
HOLD_DUTY = 73  # Hold position during sleep
PULSE_DURATION_MS = 175  # Duration of each pulse in milliseconds
SLEEP_DURATION_S = 2  # Sleep between pulses in seconds

def continuous_microstep():
    # Initialize PWM for servo
    servo = PWM(Pin(SERVO_PIN), freq=50)
    print(f"Hold duration: {SLEEP_DURATION_S}s")
    print("Press Ctrl+C or reset board to stop\n")

    cycle_count = 0

    try:
        # First, set to stop position
        #servo.duty(STOP_DUTY)
        servo.deinit()
        servo = PWM(Pin(SERVO_PIN), freq=50)
        print("Starting position: STOP")
        time.sleep(2)  # Wait 2 seconds before starting

        # Continuous loop
        while True:
            cycle_count += 1

            # Pulse ON: Set to movement duty
            servo.duty(PULSE_DUTY)
            print(f"Cycle {cycle_count}: ON (duty={PULSE_DUTY})")
            time.sleep_ms(PULSE_DURATION_MS)

            # Deinit to stop the motor completely between pulses
            servo.deinit()
            print(f"Cycle {cycle_count}: DEINIT (motor stopped)")
            time.sleep(SLEEP_DURATION_S)
            # Re-initialize for next cycle
            servo = PWM(Pin(SERVO_PIN), freq=50)

    except KeyboardInterrupt:
        print(f"\n\nStopped after {cycle_count} cycles")
        print("Count how many cycles the motor moved and calculate:")
        print("  cycles_per_22.5_degrees = observed_cycles_for_22.5_degrees")
    finally:
        servo.deinit()
        print("Servo deinitialized")

# Run continuous test
if __name__ == '__main__':
    try:
        continuous_microstep()
    except Exception as e:
        print(f"Error: {e}")
