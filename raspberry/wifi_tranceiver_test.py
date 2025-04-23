import network
import time
import socket

def ap_mode(ssid, password):
    # 1) Włączamy AP:
    ap = network.WLAN(network.AP_IF)
    ap.config(essid=ssid, password=password)
    ap.active(True)
    while not ap.active():
        time.sleep(0.5)
    ip = ap.ifconfig()[0]
    print("✅ AP aktywne. SSID:", ssid)
    print("🌐 IP Pico:", ip)

    # 2) Tworzymy gniazdo TCP na porcie 1234:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', 1234))
    s.listen(1)
    print("🎧 Nasłuchuję na porcie 1234...")

    # 3) Akceptujemy jedno połączenie:
    conn, addr = s.accept()
    print("📡 Połączono z:", addr)

    # 4) W pętli wysyłamy 'ping'
    try:
        while True:
            msg = "ping\n"
            conn.send(msg.encode())
            print("Wysłano:", msg.strip())
            time.sleep(2)
    except Exception as e:
        print("⚠️ Błąd lub klient się rozłączył:", e)
    finally:
        conn.close()
        s.close()
        print("🔌 Gniazda zamknięte, restartuję AP...")
        time.sleep(1)
        ap_mode(ssid, password)  # restart serwera

# Uruchom AP z własnym SSID / hasłem:
ap_mode('PICO_WIFI', 'seks12345')