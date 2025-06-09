from machine import Pin, PWM

class Motor:
    """
    Motor driver using two direction pins and one PWM pin.
    SPEED range: 0 .. MAX_SPEED
      MID_SPEED = stop
      > MID_SPEED = forward
      < MID_SPEED = backward
    Duty cycle is a 16-bit value (0 .. 65535)
    """
    MAX_SPEED = 2048
    MID_SPEED = MAX_SPEED // 2
    PWM_FREQ = 1000 

    def __init__(self, pwm_pin, in1_pin, in2_pin):
        self.in1 = Pin(in1_pin, Pin.OUT)
        self.in2 = Pin(in2_pin, Pin.OUT)
        self.pwm = PWM(Pin(pwm_pin, Pin.OUT))
        self.pwm.freq(self.PWM_FREQ)
        self.disable()

    def forward(self):
        self.disable()
        self.in1.high()
        self.in2.low()

    def backward(self):
        self.disable()
        self.in1.low()
        self.in2.high()

    def brake(self):
        self.in1.high()
        self.in2.high()
        self.pwm.duty_u16(0)

    def disable(self):
        self.in1.low()
        self.in2.low()
        self.pwm.duty_u16(0)

    def set_speed(self, speed):
        """
        Set motor speed.
        :param speed: int between 0 and MAX_SPEED
        :raises ValueError: if speed out of range
        """
        if not 0 <= speed <= self.MAX_SPEED:
            raise ValueError(f"Speed must be between 0 and {self.MAX_SPEED}, got {speed}")
        
        if speed == self.MID_SPEED:
            return self.disable()

        delta = abs(speed - self.MID_SPEED)
        duty = int(delta / self.MID_SPEED * 65535)

        if speed > self.MID_SPEED:
            self.forward()
        else:
            self.backward()
        self.pwm.duty_u16(duty)
