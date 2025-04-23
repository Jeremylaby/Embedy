import socket
import time

# 1) Upewnij się, że jesteś połączony z siecią Wi-Fi 'PICO_WIFI'
# 2) Wpisz tu IP Pico (domyślnie 192.168.4.1)
PICO_IP = '192.168.4.1'
PICO_PORT = 1234

def main():
    while True:
        try:
            print("🔌 Próbuję połączyć się z Pico...")
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((PICO_IP, PICO_PORT))
            print(f"✅ Połączono z {PICO_IP}:{PICO_PORT}")
            break
        except OSError as e:
            print("❌ Nie udało się połączyć, ponawiam za 2 s...", e)
            time.sleep(2)

    try:
        while True:
            data = s.recv(1024)
            if not data:
                print("⚠️ Połączenie zerwane przez serwer")
                break
            # usuwamy ewentualne znaki nowej linii na końcu
            text = data.decode().strip()
            print("◀ Otrzymano od Pico:", text)
    except KeyboardInterrupt:
        print("\n👋 Kończę odbiór.")
    finally:
        s.close()

if __name__ == '__main__':
    main()