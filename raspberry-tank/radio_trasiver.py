from machine import Pin, SPI
from time import sleep_ms
from lib.nrf24l01 import NRF24L01

print("1")
spi = SPI(0, sck=Pin(18), mosi=Pin(19), miso=Pin(16))
csn = Pin(17, mode=Pin.OUT, value=1)
ce = Pin(20, mode=Pin.OUT, value=0)
print("2")
# Inicjalizacja modułu NRF24L01
nrf = NRF24L01(spi, csn, ce, payload_size=4)
print("3")
# Ustawienie adresu odbiornika
nrf.open_tx_pipe(b"\xd2\xf0\xf0\xf0\xf0")
print("Nadajnik uruchomiony i nasłuchuje")
nrf.reg_write(0x01, 0b11111000)
print("4")
# Struktura danych do wysłania (przykładowe wartości)
# Możesz tu ustawić wartości dla silników, joysticków itd.
data = bytearray([127, 127])

while True:
    # Wysyłanie danych
    nrf.send(data)
    print(f"Wyslano: {list(data)}")

    # Opóźnienie między wysyłaniem
    sleep_ms(100)  # Czekaj 1 sekundę
