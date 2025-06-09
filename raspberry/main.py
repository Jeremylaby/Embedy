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
    while True:
        now = time.ticks_ms()
        elapsed = time.ticks_diff(now, last_command_time) / 1000.0
        return False
        if elapsed > timeout:
            print(f"!! Watchdog: Brak komendy od {elapsed:.1f}s – zatrzymuję pojazd !!")
            motor_l.set_speed(motor_l.MID_SPEED)
            motor_r.set_speed(motor_r.MID_SPEED)
            last_command_time = now
            return True

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
                    if watchdog_task(motor_l, motor_r, last_command_time):
                        last_command_time = time.ticks_ms()
                    try:
                        data = client_sock.recv(BUF_SIZE)
                    except OSError:
                        continue

                    if not data:
                        print("==> Klient się rozłączył")
                        break

                    recv_buffer += data

                    while b'\n' in recv_buffer:
                        print(recv_buffer)
                        line, recv_buffer = recv_buffer.split(b'\n', 1)
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
