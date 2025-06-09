import network
import socket
import json
from time import sleep
import machine
import rp2
import sys
from diode_test import control_leds, leds_deinit

AUTHORIZED_TOKEN = "PICO_1234_TAJNE_HASLO"
ssid = "Stanislaw's Galaxy A52s 5G"
password = 'Szymon1234'


def connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    while wlan.isconnected() == False:
        print('Waiting for connection...')
        sleep(1)
    print(wlan.ifconfig()[0])


try:
    connect()

    PORT = 1235
    s = socket.socket()
    s.bind(('0.0.0.0', PORT))
    s.listen(1)
    print(f"Serwer nasłuchuje na porcie {PORT}...")

    while True:
        auth = ""
        conn, addr = s.accept()
        print(f"Połączono z {addr}")
        login = conn.recv(1024)
        if login:
            auth = login.decode()
            print(auth)
        if auth == AUTHORIZED_TOKEN:
            while True:
                data = conn.recv(1024)
                if data:
                    message = data.decode()
                    message = message.split(" ")
                    op = message[0]
                    if op == "-d":
                        if len(message) == 3:
                            motor_l = message[1]
                            motor_r = message[2]
                            control_leds(int(motor_l), int(motor_r))
                            print(f"motor1= {motor_l}")
                            print(f"motor2= {motor_r}")
                        else:
                            print("wrong_message")
        conn.close()
        print("Zamknięto połączenie")

except KeyboardInterrupt:
    print("\nPrzerwano działanie serwera przez użytkownika.")
    s.close()
    print("Zamknięto gniazdo serwera.")
    sys.exit(0) 
