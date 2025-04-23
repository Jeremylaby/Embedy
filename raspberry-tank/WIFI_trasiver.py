import network
import socket
import time

ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid='PICO_NET', password='12345678')

print("Czekam aż AP się uruchomi...")
while ap.active() == False:
    pass

print("AP aktywny! IP:", ap.ifconfig()[0])


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
