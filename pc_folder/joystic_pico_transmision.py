import socket
import pygame
import time
LOWER_MID = 0.44
UPPER_MID = 0.55
MIDLE_VAL = 1024
MAX_VAL = 2048

AUTHORIZED_TOKEN = "PICO_1234_TAJNE_HASLO"
HOST = "192.168.164.17"
PORT = 1235

def joistic_init():
    pygame.init()
    pygame.joystick.init()
    joystick_count = pygame.joystick.get_count()
    print(f"Liczba joysticków: {joystick_count}")
    return joystick_count
def send_message(s, motor_l, motor_r):
    message = f"-d {motor_l} {motor_r}"
    s.send(message.encode())

def map_value(val):
    val = -val
    val = (val + 1.0)/2.0
    if val>=LOWER_MID and val<=UPPER_MID:
        return int(MIDLE_VAL)
    return int(val*MAX_VAL)
def socket_init():
    s = socket.socket()
    s.connect((HOST, PORT))
    s.send(f"{AUTHORIZED_TOKEN}".encode())
    return s
def main():
    if joistic_init() >0:
        joystick = pygame.joystick.Joystick(0)
        joystick.init()
        print(f"Kontroler {joystick.get_name()} jest podłączony")
        s = socket_init()
        try:
            while True:
                pygame.event.pump() 
                left_y = map_value(joystick.get_axis(1))
                right_y = map_value(joystick.get_axis(3))
                send_message(s, left_y, right_y)
                time.sleep(0.5)

        except KeyboardInterrupt:
            print("Program zakończony")
            pygame.quit()
            s.close()
    else:
        print("Nie znaleziono żadnych joysticków")


if __name__ == "__main__":
    main()