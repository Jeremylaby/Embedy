from machine import Pin, SPI
from time import ticks_ms, sleep_ms
from lib.nrf24l01 import NRF24L01


spi = SPI(0, sck=Pin(18), mosi=Pin(19), miso=Pin(16))
csn = Pin(17, mode=Pin.OUT, value=1)
ce = Pin(20, mode=Pin.OUT, value=0)


nrf = NRF24L01(spi, csn, ce, payload_size=4)
nrf.open_rx_pipe(1, b"\xd2\xf0\xf0\xf0\xf0")
nrf.start_listening()
print("NRF starts listening")

while True:
    if nrf.any():

        buf = nrf.recv()
        data = buf
        print(f"Odebrano: {list(data)}")

    sleep_ms(20)
