from math import inf
import socket
import sys


# ——— KONFIG ———
SSID = "PICO_AP_2"
PASSWORD = "secret_password_123"
HOST = "192.168.4.1"  # <- domyślny IP Pico W w trybie AP
PORT = 4343
BUF_SIZE = 1024


# Jeśli używasz autoryzacji, zdefiniuj token; inaczej usuń poniższe
AUTHORIZED_TOKEN = "very_secret_key_ilusion_of_safety"

# ——— FUNKCJE ———
1
paths = {"path_1": [[1024, 1024, 1], [2048, 2048, 1], [1024, 2048, 2], [2048, 1024, 2]],
         "path_2": [[1024, 1024, 1], [2048, 2048, 5], [0, 2048, 10], [0, 0, 5],[2048, 0, 10],]}


def send_message( path: str):
    """
    Wysyła jedną linię: "-d <left> <right>"
    """
    msg = f"{AUTHORIZED_TOKEN} -p {path}\n"
    try:
        sock = socket_init()
        print(msg)
        sock.sendall(msg.encode())
    except OSError as e:
        print("Błąd wysyłania:", e)
        raise
    finally:
        sock.close()


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

def send_path(path):
    params = []
    for param_values in path:
        params.append(" ".join(map(str, param_values)))
    params_str = "; ".join(params)
    params_str+=";"
    send_message( params_str)
    
def display_path(path):
    while True:
        print("Your path: ")
        for i, params in enumerate(path):
            print(f"param_{i}: {' '.join(map(str, params))};")
        print("Are you sure [y/n]")
        cmd = input("==> ")
        if cmd == "n":
            break
        if cmd == "y":
            send_path(path)
            break


def main():
    try:
        while True:
            print("Wybierz numer drogi lub x aby wyjść: ")
            path_keys = list(paths.keys())
            for i, key in enumerate(path_keys):
                print(f"{i}: {key}")
            cmd = input("==> ")

            if cmd == "x":
                break
            if not cmd.isdigit():
                print("Zła komenda")
                continue
            idx = int(cmd)
            if idx < 0 or idx >= len(paths):
                continue
            display_path(paths[path_keys[idx]])

    except KeyboardInterrupt:
        print("\nZakończono przez użytkownika.")
    except Exception as e:
        print("Wystąpił błąd w pętli głównej:", e)
    finally:
        print("Socket zamknięty, pygame wypięty.")


if __name__ == "__main__":
    main()
