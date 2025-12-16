import time

_user_input = None


def set_user_input(value: str):
    global _user_input
    _user_input = value


def wait_for_user_input() -> str:
    global _user_input
    while _user_input is None:
        time.sleep(0.2)
    value = _user_input
    _user_input = None
    return value