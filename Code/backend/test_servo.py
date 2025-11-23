# Test script for MG996 continuous rotation servo on ESP32 (MicroPython)
# Connect servo signal to GPIO 17 (change as needed)
# Power servo with 5V (not ESP32 3.3V!)




from machine import Pin, PWM
import time

SERVO_PIN = 18  # Use GPIO18 (D18)
servo = PWM(Pin(SERVO_PIN), freq=50)

# Calibration values (edit as needed)
min_duty = 60   # 0.5ms pulse (full reverse)
max_duty = 95  # ~2.9ms pulse (full forward)
stop_duty = (min_duty + max_duty) // 2  # ~128 (1.5ms pulse)

def set_raw_duty(duty):
    servo.duty(duty)
    print(f"Set raw duty: {duty}")
    time.sleep(1.5)

def set_speed(speed):
    global min_duty, max_duty, stop_duty
    # Clamp speed to -100..100
    if speed < -100: speed = -100
    if speed > 100: speed = 100
    if speed == 0:
        duty = stop_duty
    elif speed > 0:
        duty = int(stop_duty + (max_duty - stop_duty) * speed / 100)
    else:
        duty = int(stop_duty + (min_duty - stop_duty) * (-speed) / 100)
    servo.duty(duty)
    print(f"Set speed: {speed}, duty: {duty}")
    time.sleep(1.5)

def calibrate():
    global min_duty, max_duty, stop_duty
    print("\n--- Servo Calibration Mode ---")
    print("You can test and update min_duty, max_duty, and stop_duty.")
    print("Type 'q' to quit calibration mode.\n")
    while True:
        print(f"Current values: min_duty={min_duty}, max_duty={max_duty}, stop_duty={stop_duty}")
        print("Options:")
        print("  1: Set min_duty (full reverse)")
        print("  2: Set max_duty (full forward)")
        print("  3: Set stop_duty (stop)")
        print("  4: Test min_duty")
        print("  5: Test max_duty")
        print("  6: Test stop_duty")
        print("  7: Test set_speed(-100, 0, 100)")
        print("  q: Quit calibration mode")
        opt = input("Select option: ").strip()
        if opt == '1':
            val = input("Enter new min_duty (int): ").strip()
            try:
                min_duty = int(val)
            except:
                print("Invalid input.")
        elif opt == '2':
            val = input("Enter new max_duty (int): ").strip()
            try:
                max_duty = int(val)
            except:
                print("Invalid input.")
        elif opt == '3':
            val = input("Enter new stop_duty (int): ").strip()
            try:
                stop_duty = int(val)
            except:
                print("Invalid input.")
        elif opt == '4':
            set_raw_duty(min_duty)
        elif opt == '5':
            set_raw_duty(max_duty)
        elif opt == '6':
            set_raw_duty(stop_duty)
        elif opt == '7':
            set_speed(-100)
            set_speed(0)
            set_speed(100)
            set_speed(0)
        elif opt == 'q':
            print("Exiting calibration mode.")
            break
        else:
            print("Invalid option.")

try:
    print("Testing continuous rotation servo...")
    calibrate()
finally:
    servo.deinit()
    print("Test complete.")
