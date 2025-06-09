import network
import socket
import time

# Tworzenie Access Pointa
ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid='PICO_NET', password='12345678')  # Nazwa i hasło Wi-Fi

print("Czekam aż AP się uruchomi...")
while ap.active() == False:
    pass

print("AP aktywny! IP:", ap.ifconfig()[0])

# Tworzymy serwer TCP
addr = socket.getaddrinfo('0.0.0.0', 1234)[0][-1]
s = socket.socket()
s.bind(addr)
s.listen(1)

print("Oczekiwanie na połączenie...")

while True:
    cl, addr = s.accept()
    print('Połączono z:', addr)
    cl.send(b'Hello from AP Pico!\n')
    cl.close()
