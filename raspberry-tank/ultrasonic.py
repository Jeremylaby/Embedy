from machine import Pin
TRIGGER_PIN = 27
ECHO_PIN = 26
def ultiasonic_init():
    trigger = Pin(TRIGGER_PIN, Pin.OUT)
    echo = Pin(ECHO_PIN, Pin.IN)
def ultra():
   trigger.low()
   utime.sleep_us(2)
   trigger.high()
   utime.sleep_us(5)
   trigger.low()
   while echo.value() == 0:
       signaloff = utime.ticks_us()
   while echo.value() == 1:
       signalon = utime.ticks_us()
   timepassed = signalon - signaloff
   distance = (timepassed * 0.0343) / 2
   print("The distance from object is ",distance,"cm")
   return