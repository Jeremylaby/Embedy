from math import inf
import socket
import pygame
import time
import sys






# ——— KONFIG ———
SSID       = "PICO_AP_2"
PASSWORD   = "secret_password_123"
HOST       = "192.168.4.1"   # <- domyślny IP Pico W w trybie AP
PORT       = 4343
BUF_SIZE   = 1024

# Zakresy joysticka → wartości PWM
LOWER_MID  = 0.44
UPPER_MID  = 0.55
MID_VAL    = 1024
MAX_VAL    = 2048

# Jeśli używasz autoryzacji, zdefiniuj token; inaczej usuń poniższe
AUTHORIZED_TOKEN = "very_secret_key_ilusion_of_safety"

# ——— FUNKCJE ———

def joystick_init():
    pygame.init()
    pygame.joystick.init()
    count = pygame.joystick.get_count()
    print(f"Liczba joysticków: {count}")
    return count

def map_value(val: float) -> int:
    """
    Mapiuje oś joysticka [-1..+1] na zakres [0..MAX_VAL],
    z martwą strefą pomiędzy LOWER_MID i UPPER_MID.
    """
    val = -val  # odwrócenie osi Y
    val = (val + 1.0) / 2.0  # teraz [0..1]
    if LOWER_MID <= val <= UPPER_MID:
        return MID_VAL
    return int(val * MAX_VAL)

def send_message(sock: socket.socket, left: int, right: int):
    """
    Wysyła jedną linię: "-d <left> <right>"
    """
    msg = f"{AUTHORIZED_TOKEN} -d {left} {right}\n"
    try:
        print(msg)
        sock.sendall(msg.encode())
    except OSError as e:
        print("Błąd wysyłania:", e)
        raise

def socket_init() -> socket.socket:
    """
    Tworzy i zwraca połączone gniazdo TCP.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(5)  # timeout 5s na connect/recv
    try:
        print(f"Łączę się z {HOST}:{PORT} …")
        s.connect((HOST, PORT))
        print("Połączono!")
        return s
    except OSError as e:
        print("Nie udało się połączyć:", e)
        s.close()
        sys.exit(1)


def main():
    last_l = inf
    last_r = inf
    last_send_time = time.time()
    # 1) Upewnij się, że joystick jest podłączony
    if joystick_init() == 0:
        print("Nie znaleziono joysticka. Kończę.")
        return

    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    print("Sterownik:", joystick.get_name())

    # 2) Inicjalizuj socket
    sock = socket_init()

    try:
        while True:
            pygame.event.pump()  # odczyt zdarzeń
            left  = map_value(joystick.get_axis(1))
            right = map_value(joystick.get_axis(3))
            now = time.time()

            changed = (left != last_l) or (right != last_r) 
            timed_out = (now - last_send_time) >= 1.0  # co 1 sekundę

            if (changed or timed_out):
                send_message(sock, left, right)
                last_l = left
                last_r = right
                last_send_time = now

            time.sleep(0.2)

    except KeyboardInterrupt:
        print("\nZakończono przez użytkownika.")
    except Exception as e:
        print("Wystąpił błąd w pętli głównej:", e)
    finally:
        sock.close()
        pygame.quit()
        print("Socket zamknięty, pygame wypięty.")

if __name__ == "__main__":
    main()
