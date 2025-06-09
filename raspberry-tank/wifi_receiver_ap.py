import network
import time
import socket

def ap_setup(ssid, password):
    ap = network.WLAN(network.AP_IF)
    ap.config(essid=ssid, password=password)
    ap.active(True)
    while not ap.active():
        time.sleep(0.5)
    ip = ap.ifconfig()[0]
    print("AP aktywne. SSID:", ssid)
    print("IP Pico:", ip)
    return ap, ip
def socket_setup(ip, port):
    addr = (ip, port)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(addr)
    s.listen(1)
    print("Serwer TCP nasłuchuje na:", addr)
    return s
def setup(ssid, password, port):
    ap, ip = ap_setup(ssid, password)
    server_socket = socket_setup(ip, port)
    return ap, server_socket




