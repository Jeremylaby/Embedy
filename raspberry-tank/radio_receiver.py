from machine import Pin, SPI, UART
from lib.nrf24l01 import NRF24L01
import utime

# SPI: SCK=GP18, MOSI=GP19, MISO=GP20
spi = SPI(0, sck=Pin(18), mosi=Pin(19), miso=Pin(20))
csn = Pin(16, Pin.OUT)
ce = Pin(17, Pin.OUT)

# Upewnij się, że payload_size zgadza się z nadajnikiem!
nrf = NRF24L01(spi, csn, ce, payload_size=2)
# Adres musi być dokładnie taki jak w nadajniku
nrf.open_rx_pipe(1, b'\xe9\xe8\xf0\xf0\xe1')
nrf.start_listening()

print("Nasłuchuję danych NRF24L01...")

while True:
    if nrf.any():
        try:
            buf = nrf.recv()
            print("✅ Odebrano:", buf)

            if len(buf) == 2:
                motor1 = buf[0]
                motor2 = buf[1]
                print(f"motor1: {motor1}, motor2: {motor2}")
        except OSError as e:
            print("Błąd odbioru:", e)

    else:
        print("Brak danych...")
    utime.sleep(0.1)
