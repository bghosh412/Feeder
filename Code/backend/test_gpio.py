# Simple GPIO test for ESP32 stepper motor pins
# This will blink each pin one at a time to verify connections

import time
from machine import Pin

# Your current pin configuration
pins = [19, 18, 5, 17]  # IN1, IN2, IN3, IN4

print("Testing GPIO pins for stepper motor...")
print("Pins:", pins)
print("Watch the LEDs on your ULN2003 board")
print()

# Initialize all pins as outputs
gpio_pins = [Pin(p, Pin.OUT) for p in pins]

# Turn all off first
for p in gpio_pins:
    p.value(0)

print("Starting pin test (each pin will blink 3 times)...")
time.sleep(2)

# Test each pin individually
for i, pin in enumerate(gpio_pins):
    print(f"Testing GPIO {pins[i]} (IN{i+1})...")
    for _ in range(3):
        pin.value(1)
        time.sleep_ms(500)
        pin.value(0)
        time.sleep_ms(500)
    time.sleep(1)

print("\nNow testing full sequence (one cycle)...")
sequence = [
    [1, 0, 0, 0],
    [1, 1, 0, 0],
    [0, 1, 0, 0],
    [0, 1, 1, 0],
    [0, 0, 1, 0],
    [0, 0, 1, 1],
    [0, 0, 0, 1],
    [1, 0, 0, 1],
]

for step in sequence:
    for pin_idx, value in enumerate(step):
        gpio_pins[pin_idx].value(value)
    print("Step:", step)
    time.sleep_ms(100)

# Turn all off
for p in gpio_pins:
    p.value(0)

print("\nTest complete!")
