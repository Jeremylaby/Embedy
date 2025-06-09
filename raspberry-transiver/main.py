import network
import socket
import time
from machine import ADC, Pin

import network, machine, gc, time
from machine import disable_irq, enable_irq

try:
    import rp2
    HAVE_RP2 = True
except ImportError:
    HAVE_RP2 = False

# ——— KONFIG ———
SSID             = 'PICO_AP_2'
PASSWORD         = 'secret_password_123'
HOST             = '192.168.4.1'
PORT             = 4343
AUTHORIZED_TOKEN = "very_secret_key_ilusion_of_safety"


def led_blink(led: Pin, times: int, delta=0.2):
    for _ in range(times):
        led.toggle()
        time.sleep(delta)
        led.toggle()
        time.sleep(delta)
    led.on()


def fresh_start():
    import network, time, gc

    # 1) Wyłącz punkt dostępowy, jeśli włączony
    ap = network.WLAN(network.AP_IF)
    if ap.active():
        ap.active(False)
        time.sleep(0.1)

    # 2) Zrestartuj interfejs STA: off→on
    sta = network.WLAN(network.STA_IF)
    if sta.active():
        sta.active(False)
        time.sleep(0.1)
    sta.active(True)
    time.sleep(0.1)

    # 3) Rozłącz, gdyby było jakieś stare połączenie
    try:
        sta.disconnect()
    except:
        pass
    time.sleep(0.1)

    # 4) Oczyść pamięć
    gc.collect()




# ——— Reset i “wyczyszczenie” radia Wi-Fi ———
def reset_wifi():
    # 1) wyłącz AP_IF (domyślny punkt dostępu)
    ap = network.WLAN(network.AP_IF)
    if ap.active():
        ap.active(False)
        time.sleep(0.2)

    # 2) wyłącz i włącz STA_IF
    sta = network.WLAN(network.STA_IF)
    if sta.active():
        sta.active(False)
        time.sleep(0.2)
    sta.active(True)
    time.sleep(0.2)

    # 3) jeśli nadal połączony, rozłącz
    if sta.isconnected():
        sta.disconnect()
        time.sleep(0.2)

    # 4) (opcjonalnie) wymuś reload radia przez zmianę kraju
    if HAVE_RP2:
        # zmień na “US”, potem na “PL” – to powoduje soft-reset radia
        rp2.country('US')
        time.sleep(0.1)
        rp2.country('PL')
        time.sleep(0.1)

# ——— Łączenie do Wi-Fi z retry i timeoutem ———
def connect_wifi(retries=5, timeout=10):
    print("Connecting...")
    sta = network.WLAN(network.STA_IF)
    sta.active(True)
    sta.connect(SSID, PASSWORD)
        

    while not sta.isconnected():
        time.sleep(0.5)

    if sta.isconnected():
        print("✅ Połączono, ifconfig():", sta.ifconfig())
        return True

    print("❌ Brak połączenia po wszystkich próbach!")
    return False

# ——— Inicjalizacja joysticka ———
lewa = ADC(Pin(27))
prawa  = ADC(Pin(26))
def parse(raw):
    if   raw > 62250:       return 2048
    elif raw <  3275:       return 0
    elif 29500 < raw < 36050: return 1024
    return raw // 32

def socket_init():
    """
    Tworzy i zwraca połączone gniazdo TCP.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        print(f"Łączę się z {HOST}:{PORT} …")
        s.connect((HOST, PORT))
        print("Połączono!")
        return s
    except OSError as e:
        print("Nie udało się połączyć:", e)
        s.close()
def send_joystick_loop():
    try:
        s=socket_init()
        print(f"✅ TCP OK – wysyłam co 0.5 s do {HOST}:{PORT}")
        while True:
            l = parse(lewa.read_u16())
            r = parse(prawa.read_u16())
            msg = f"{AUTHORIZED_TOKEN} -d {l} {r}\n"
            s.sendall(msg.encode())
            print("▶", msg.strip())
            time.sleep(0.5)

    except Exception as e:
        print("❌ Socket error:", e)

    finally:
        s.close()
        print("🔌 Socket zamknięty")

# ——— Główna logika ———
if __name__ == '__main__':
    
    led = Pin("LED", Pin.OUT)
    led.off()
    
    led.on()
    
    if connect_wifi():
        
        led_blink(led, 4)
        
        send_joystick_loop()


