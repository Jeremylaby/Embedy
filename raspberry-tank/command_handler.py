from motor import Motor
import time

AUTHORIZED_TOKEN = "very_secret_key_ilusion_of_safety"


class CommandError(Exception):
    """Ogólny błąd w formacie lub argumentach komendy."""

    pass


class AuthenticationError(CommandError):
    """Niepoprawny klucz dostępu."""

    pass


class UnknownCommandError(CommandError):
    """Nieznany prefiks komendy."""

    pass


class InvalidArgumentsError(CommandError):
    """Błędne lub brakujące argumenty komendy."""

    pass


class InvalidParamError(CommandError):
    """Błędne lub brakujące argumenty w parametrze komendy./."""

    pass


def command_handler(data: str, motor_l: Motor, motor_r: Motor):
    """
    Parsuje linię tekstu 'data' i wykonuje komendę na obiektach motor_l, motor_r.
    :raises AuthenticationError:    gdy klucz jest niepoprawny
    :raises UnknownCommandError:    gdy prefiks nie jest rozpoznany
    :raises InvalidArgumentsError:  gdy brakuje lub są złe argumenty
    :returns: None  (jeśli komenda przeszła pomyślnie)
    """
    parts = data.strip().split()

    if len(parts) < 2:
        raise CommandError("Command is to short")

    key, prefix, *args = parts

    if key != AUTHORIZED_TOKEN:
        raise AuthenticationError("Wrong Secret key")

    if prefix == "-d":
        if len(args) != 2:
            raise InvalidArgumentsError("Command '-d' need two args: speed_l speed_r")
        try:
            speed_l = int(args[0])
            speed_r = int(args[1])
        except ValueError:
            raise InvalidArgumentsError("Speed need to be integer")
        motor_l.set_speed(speed_l)
        motor_r.set_speed(speed_r)
        # print(f"==> motor_l {speed_l} motor_r {speed_r}")
    elif prefix == "-p":
        """Zakładamy że postać każdej komendy (params) to:
        "speed_l speed_r time;
            ....
         sped_l speed_r time;"


        Raises:
            InvalidParamError: Kiedy param nie wygląda tak jak w opisie wyżej czyli nie składa się z 3 wartości
            ten błąd jest zgłaszany
        """
        commands = " ".join(args).rstrip(";").split("; ")
        for command in commands:
            params = command.split(" ")
            if len(params) != 3:
                raise InvalidParamError(
                    f"Params count mismatch: expected 3 arguments, but received {len(params)}."
                )
            speed_l, speed_r, time_s = params
            try:
                speed_l = int(speed_l)
                speed_r = int(speed_r)
                time_s = float(time_s)
            except ValueError:
                raise InvalidArgumentsError(
                    "Speeds must be integers and time must be a float"
                )
            motor_l.set_speed(speed_l)
            motor_r.set_speed(speed_r)
            time.sleep(time_s)
        motor_l.disable()
        motor_r.disable()
            

    else:
        raise UnknownCommandError(f"Uknown command '{prefix}'")
