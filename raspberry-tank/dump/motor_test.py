from machine import Pin, PWM
from utime import sleep

motor_1_led_f = PWM(Pin(0))
motor_1_led_b = PWM(Pin(1))
motor_2_led_f = PWM(Pin(2))
motor_2_led_b = PWM(Pin(3))

for motor in [motor_1_led_f, motor_1_led_b, motor_2_led_f, motor_2_led_b]:
    motor.freq(1000)

print("LED starts flashing...")

try:
    while True:
        for duty in range(0, 65536, 4096):
            motor_1_led_f.duty_u16(duty)
            sleep(0.1)

        motor_1_led_f.duty_u16(0)

        for duty in range(0, 65536, 4096):
            motor_1_led_b.duty_u16(duty)
            sleep(0.1)

        motor_1_led_b.duty_u16(0)

        for duty in range(0, 65536, 4096):
            motor_2_led_f.duty_u16(duty)
            sleep(0.1)

        motor_2_led_f.duty_u16(0)

        for duty in range(0, 65536, 4096):
            motor_2_led_b.duty_u16(duty)
            sleep(0.1)

        motor_2_led_b.duty_u16(0)

except KeyboardInterrupt:

    for motor in [motor_1_led_f, motor_1_led_b, motor_2_led_f, motor_2_led_b]:
        motor.duty_u16(0)
    print("Finished.")
