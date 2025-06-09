import machine
from machine import PWM, Pin
import time
MIDDLE = 1024
MAX_VAL = 2048
PWM_MAX = 1024
MAX_DUTY = 65535

led_l_f = PWM(Pin(2))
led_l_b = PWM(Pin(3))
led_r_f = PWM(Pin(4))
led_r_b = PWM(Pin(5))

led_l_f.freq(1000)
led_l_b.freq(1000)
led_r_f.freq(1000)
led_r_b.freq(1000)

def set_led_brightness(led, value):
    scaled = int((value / PWM_MAX) * MAX_DUTY)
    led.duty_u16(scaled)
def control_motor(motor, led_f, led_b):
    if motor==MIDDLE:
        set_led_brightness(led_f,0)
        set_led_brightness(led_b,0)
    elif motor>MIDDLE:
        set_led_brightness(led_f,motor - PWM_MAX)
        set_led_brightness(led_b,0)
    else:
        set_led_brightness(led_f,0)
        set_led_brightness(led_b,PWM_MAX - motor)
def control_leds(motor_l, motor_r):
    control_motor(motor_l,led_l_f,led_l_b)
    control_motor(motor_r,led_r_f,led_r_b)
    

def leds_deinit():
    led_l_f.deinit()
    led_l_b.deinit()
    led_r_f.deinit()
    led_r_b.deinit()
    machine.reset()

