# SYSTEMY WBUDOWANE 2025
## Stanisław Barycki, Piotr Błaszczyk, Krzysztof Swędzioł

## Opis projektu

Projekt zakłada stworzenie zdalnie sterowanego czołgu z wykorzystaniem dwóch mikrokomputerów Raspberry Pi Pico WH, komunikujących się ze sobą poprzez sieć Wi-Fi. Jeden z nich znajduje się w czołgu i działa jako Access Point oraz serwer TCP, a drugi – umieszczony w kontrolerze – łączy się jako klient TCP i przesyła komendy sterujące ruchem pojazdu.

Sterowanie odbywa się poprzez joystick analogowy, a komunikacja oparta jest na socketach TCP i własnym protokole tekstowym opartym na komendach.

## CZOŁG

### Komponenty czołgu
- Mikrokontroler: Raspberry Pi Pico WH
- Zasilanie: Bateria lipo 3,7V 
- Silniki sterujące ruchem gąsienic w podwoziu
- Sterownik silników: Własna implementacja klasy Motor
- Moduł komunikacyjny Wi-Fi: Pico W jako Access Point

### Funkcjonalność czołgu
- Nasłuch TCP na porcie 4343, połączenie dostępne po SSID: PICO_AP_2
- Obsługa dwóch komend:
  - `-d`: bezpośrednie sterowanie silnikami (speed_l, speed_r)
  - `-p`: tryb "programowy" – zestaw komend w sekwencji z czasem trwania
- Watchdog – zatrzymuje czołg, gdy nie otrzymano komendy w ciągu 2 sekund
- System autoryzacji – wymagana tajna fraza (AUTHORIZED_TOKEN)

### Logika opakowana w pliki:
- `main.py` – serwer TCP i pętla główna
- `motor.py` – klasa sterująca silnikami
- `command_handler.py` – parser komend i wykonanie logiki
- `wifi_receiver_ap.py` – konfiguracja trybu AP


![alt text](photos/image.png)

## kod main.py czołgu

```python
from machine import Pin
from motor import Motor
import time
from command_handler import command_handler, AuthenticationError, UnknownCommandError, InvalidArgumentsError, CommandError
from wifi_receiver_ap import setup

SSID = "PICO_AP_2"
PASSWORD = "secret_password_123"
PORT = 4343
IP = "192.168.4.1"
BUF_SIZE = 1024

M0_IN1_PIN = 13
M0_IN2_PIN = 14
M0_PWM = 15
M1_IN1_PIN = 12
M1_IN2_PIN = 11
M1_PWM = 10

last_command_time = 0
SAFE_TIMEOUT = 2.0

def watchdog_task(motor_l, motor_r, last_command_time, timeout = SAFE_TIMEOUT):
    now = time.ticks_ms()
    elapsed = time.ticks_diff(now, last_command_time) / 1000.0
    print(f"Watchdog last command: {last_command_time} now: {now} elapsed: {elapsed}")
        
    if elapsed > timeout:
        print(f"!! Watchdog: Brak komendy od {elapsed:.1f}s – zatrzymuję pojazd !!")
        motor_l.disable()
        motor_r.disable()
        last_command_time = now
        return True
    return False

def led_blink(led: Pin, times: int, delta=0.2):
    for _ in range(times):
        led.toggle()
        time.sleep(delta)
        led.toggle()
        time.sleep(delta)
    led.on()

def main():
    led = Pin("LED", Pin.OUT)
    led.off()

    motor_l = Motor(M0_PWM, M0_IN1_PIN, M0_IN2_PIN)
    motor_r = Motor(M1_PWM, M1_IN1_PIN, M1_IN2_PIN)

    ap, server = setup(SSID, PASSWORD, PORT)
    led.on()


    try:
        while True:
            #Changed
            motor_l.disable()
            motor_r.disable()

            print("Czekam na klienta...")
            client_sock, client_addr = server.accept()
            client_sock.settimeout(2)
            print("==> Połączono z:", client_addr)
            led_blink(led, 4)

            recv_buffer = b""
            last_command_time = time.ticks_ms()
            try:
                while True:
                    
                    watchdog_task(motor_l, motor_r, last_command_time)
                        
                    try:
                        data = client_sock.recv(BUF_SIZE)
                    except OSError:
                        continue

                    if not data:
                        print("==> Klient się rozłączył")
                        break

                    recv_buffer += data
                    if b'\n' in recv_buffer:
                        print(recv_buffer)
                        line, *recv_buffer = recv_buffer.split(b'\n')
                        if recv_buffer[-1]:
                            line = recv_buffer[-1]
                        line = line.strip()
                        if not line:
                            continue
                        print("==> Odebrano:", line.decode())
                        try:
                            command_line = line.decode()
                            command_handler(command_line, motor_l, motor_r)
                            last_command_time = time.ticks_ms()
                        except (AuthenticationError, UnknownCommandError, InvalidArgumentsError, CommandError) as e:
                            print(f"==> Command handler error {e}")
                        recv_buffer =b""
                    

            except OSError as e:
                print("Błąd podczas komunikacji z klientem:", e)

            finally:
                client_sock.close()
                #Changed
                motor_l.disable()
                motor_r.disable()
                print("Gniazdo klienta zamknięte.\n")

    except KeyboardInterrupt:
        print("\nPrzerwano przez użytkownika (KeyboardInterrupt). Kończę…")

    except Exception as e:
        print("Nieoczekiwany błąd:", e)

    finally:	 
        #Changed
        motor_l.disable()
        motor_r.disable()
        try:
            led.off()
            server.close()
            print("Serwer zamknięty.")
        except:
            pass
        try:
            ap.active(False)
            print("Interfejs AP wyłączony.")
        except:
            pass
        print("Gotowe. Do zobaczenia!")

if __name__ == "__main__":
    main()
```

## Komunikacja Wi-Fi

### Raspberry Pi Pico WH (czołg)
- Tworzy własną sieć Wi-Fi (Access Point)
  
**Parametry:**
- SSID: `PICO_AP_2`
- Hasło: `secret_password_123`
- Adres IP: `192.168.4.1`

### Kontroler (drugi Pico)
- Łączy się z Access Pointem czołgu
- Odczytuje pozycje joysticka (2 osie ADC)
- Przesyła co 0.5 sekundy aktualne komendy w formacie `-d` z tokenem autoryzacyjnym

## Protokół komend

Każda komenda przesyłana z kontrolera do czołgu zawiera:
[TOKEN] [PREFIX] [ARGUMENTY]

**Przykłady:**
very_secret_key_ilusion_of_safety -d 1024 2048
very_secret_key_ilusion_of_safety -p 1024 2048 1.0; 0 0 0.5;

**Obsługiwane komendy:**

| Prefix | Opis | Argumenty |
|--------|------|-----------|
| `-d` | Ruch bezpośredni | `speed_l speed_r` (int) |
| `-p` | Sekwencja ruchów | `speed_l speed_r czas; ...` |

## JOYSTICK

![alt text](photos/image2.png)
![alt text](photos/image3.png)

Kontroler czołgu oparty jest na dwóch potencjometrach analogowych symulujących joystick dwukierunkowy – jeden dla lewej gąsienicy, drugi dla prawej.

## Działanie systemu
- **Dwa wejścia analogowe** (GPIO 27 i 26) odczytują wartości z potencjometrów  
- **Konwersja odczytów** na wartości sterujące:  
  - `0` – pełna prędkość wstecz  
  - `1024` – zatrzymanie  
  - `2048` – pełna prędkość do przodu  
- **Częstotliwość wysyłania**: co 0.5 sekundy  
- **Format polecenia**:  
  `<SECRET_KEY> -d <SPEED_L> <SPEED_R>\n`  

### Przykład polecenia
`very_secret_key_ilusion_of_safety -d 1100 900`

- **Odbiornik**: Raspberry Pi Pico (tryb AP)  
  - Odbiera komendy przez socket TCP  
  - Steruje silnikami zgodnie z wartościami  

## Przetwarzanie wartości analogowych
### Charakterystyka funkcji parse()
- **Martwa strefa** (29500–36050)  
  - Eliminuje przypadkowy ruch przy drganiu joysticka  
  - Zwraca wartość 1024 (zatrzymanie)  
- **Wartości graniczne**:  
  - `> 62250` → 2048 (maks. prędkość do przodu)  
  - `< 3275` → 0 (maks. prędkość wstecz)  
- **Skalowanie**:  
  - Konwersja 16-bitowego ADC (0–65535) na zakres 0–2048  
  - Realizowane przez operację `raw // 32`  

## Diagnostyka systemu
W terminalu debugowym pojawiają się komunikaty:  
`very_secret_key_ilusion_of_safety -d 2048 2048`  

### Cel diagnostyki
1. Weryfikacja działania joysticka  
2. Kontrola komunikacji z czołgiem  
3. Monitorowanie przetwarzania wartości analogowych  
### kod main.py joysticka

```python
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
```

# Uruchamianie systemu

## Po stronie czołgu
1. Wgrywamy pliki:
   - `main.py`
   - `motor.py`
   - `command_handler.py`
   - `wifi_receiver_ap.py`
2. Uruchamiamy `main.py`
3. Weryfikujemy w konsoli:
   - Pojawienie się komunikatu `Czekam na klienta...`

## Po stronie kontrolera
1. Podłączamy joystick do pinów **ADC 26 i 27**
2. Wgrywamy `kontroler.py`
3. Uruchamiamy skrypt i łączymy się z siecią **PICO_AP_2**
4. System automatycznie wysyła komendy co **0.5 sekundy**

---

## Bezpieczeństwo
- Każda komenda zawiera **token autoryzacyjny**
- Komendy z nieprawidłowym tokenem są automatycznie ignorowane
- Mechanizm zapobiega nieautoryzowanemu sterowaniu czołgiem

---

## Dodatki i możliwe rozszerzenia
### Obecne elementy
- **Niewykorzystany czujnik ultradźwiękowy** (może służyć do wykrywania przeszkód)

### Potencjalne rozszerzenia
1. Wprowadzenie alternatywnych protokołów komunikacji:
   - Serwer UDP
   - Protokół MQTT
2. **Przycisk awaryjny STOP** na kontrolerze
3. Udoskonalenie systemu watchdog:
   - Ręczne zatrzymanie silników
   - Timeouty połączone z sygnalizacją LED
   - Automatyczne bezpieczne wyłączenie przy braku komunikacji


### Co można było poprawić? / retrospekcja

1. **Komunikacja joysticka z czołgiem**
   - Wi-Fi działa tylko na jednej częstotliwości (2,4 GHz), co powodowało trudne do zdebugowania anomalie. Na przykład, gdy w laptopie obok było włączone Wi-Fi, czołg nie łączył się z joystickiem; po wyłączeniu Wi-Fi na laptopie procedura parowania zaczynała działać poprawnie. Podobne zjawisko zauważyliśmy, testując w pokoju w akademiku vs. na balkonie.  
   - Zasięg jest dość krótki i szybko zanika.  
   - Możliwe (choć nie mamy pewności), że łączność radiowa na innej, prawdopodobnie niższej, częstotliwości działałaby lepiej i efektywniej. Co więcej, w pierwotnych planach rozważaliśmy zastosowanie transmiterów radiowych, ale porzuciliśmy ten pomysł na rzecz wbudowanego Wi-Fi w Raspberry Pi.

2. **Zasilanie**
   - Bateria szybko się rozładowuje, a gąsienice mają mały „kop”. Podejrzewamy też, że ograniczony zasięg może wynikać z niewystarczającej mocy zasilania. Eksperymentowaliśmy z mocniejszą baterią, ale mieliśmy wrażenie że zaraz coś wybuchnie / spali się, dlatego zostaliśmy przy słabszych ogniwach. Kontynuując projekt, należałoby zrobić lepszy research i dokładniejsze testy z mocniejszym zasilaniem.

3. **Obudowa**
   - Jak widać na zdjęciach, kabelki wystają, a joystick to de facto deska. Aby estetycznie dopieścić całość, warto zainwestować w solidniejszą, bardziej dopracowaną obudowę. To już jednak kwestia estetyki, a nie funkcjonalności.



