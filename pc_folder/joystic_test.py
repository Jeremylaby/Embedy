import pygame
import time
LOWER_MID = 0.44
UPPER_MID = 0.55
# Inicjalizacja pygame
pygame.init()

# Inicjalizowanie joysticków
pygame.joystick.init()
def map_value(val):
    val = -val
    val = (val + 1.0)/2.0
    if val>=LOWER_MID and val<=UPPER_MID:
        return 127
    return val*255
# Sprawdzanie liczby dostępnych joysticków
joystick_count = pygame.joystick.get_count()
print(f"Liczba joysticków: {joystick_count}")

# Jeśli jest co najmniej jeden joystick, użyj go
if joystick_count > 0:
    joystick = pygame.joystick.Joystick(0)  # Wybierz pierwszy joystick (kontroler PS4)
    joystick.init()
    print(f"Kontroler {joystick.get_name()} jest podłączony")

    try:
        while True:

            pygame.event.pump() 
            left_y = map_value(joystick.get_axis(1))  # Oś Y lewego joysticka

            right_y = map_value(joystick.get_axis(3))  # Oś Y prawego joysticka

            # Wydruk wartości joysticków
            print(f"Left Joystick: Y = {left_y:.2f}")
            print(f"Right Joystick: Y = {right_y:.2f}")

            # Oczekiwanie przed kolejnym odczytem
            time.sleep(1)

    except KeyboardInterrupt:
        print("Program zakończony")
        pygame.quit()
else:
    print("Nie znaleziono żadnych joysticków")
