# 28BYJ-48 Stepper Motor Driver
# Controls the stepper motor via ULN2003 driver
import utime as time
from machine import Pin

class StepperMotor:
    """Driver for 28BYJ-48 stepper motor with ULN2003"""
    
    # Half-step sequence for smoother operation and better torque
    HALF_STEP_SEQUENCE = [
        [1, 0, 0, 0],
        [1, 1, 0, 0],
        [0, 1, 0, 0],
        [0, 1, 1, 0],
        [0, 0, 1, 0],
        [0, 0, 1, 1],
        [0, 0, 0, 1],
        [1, 0, 0, 1],
    ]
    
    def __init__(self, pin1, pin2, pin3, pin4):
        """Initialize stepper motor pins"""
        self.pins = [
            Pin(pin1, Pin.OUT),
            Pin(pin2, Pin.OUT),
            Pin(pin3, Pin.OUT),
            Pin(pin4, Pin.OUT),
        ]
        self.current_step = 0
        self.off()
    
    def step(self, steps, delay_ms=2):
        """
        Rotate motor by specified number of steps
        Positive steps = clockwise, Negative = counter-clockwise
        """
        direction = 1 if steps > 0 else -1
        steps = abs(steps)
        
        for _ in range(steps):
            # Set pins according to sequence
            sequence = self.HALF_STEP_SEQUENCE[self.current_step]
            for pin_idx, value in enumerate(sequence):
                self.pins[pin_idx].value(value)
            
            # Move to next step
            self.current_step = (self.current_step + direction) % len(self.HALF_STEP_SEQUENCE)
            
            # Delay between steps
            time.sleep_ms(delay_ms)
    
    def rotate_degrees(self, degrees, delay_ms=2):
        """Rotate motor by specified degrees"""
        # 28BYJ-48 has 4096 steps per full rotation (with half-stepping)
        steps = int((degrees / 360) * 4096)
        self.step(steps, delay_ms)
    
    def off(self):
        """Turn off all motor pins to save power"""
        for pin in self.pins:
            pin.value(0)
