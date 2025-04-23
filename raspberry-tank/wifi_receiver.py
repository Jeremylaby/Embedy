import network
import socket
import network
import socket
from time import sleep
import machine
import rp2
import sys


ssid = "Stanislaw's Galaxy A52s 5G"
password = 'Szymon123'


def connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    while wlan.isconnected() == False:
        print('Waiting for connection...')
        sleep(1)
    print(wlan.ifconfig())


connect()
