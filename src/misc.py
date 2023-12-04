from machine import Timer


def debounce(threshold: int):
    def decorator(func):
        timer = Timer(1)

        def wrapper(*args):
            timer.init(mode=Timer.ONE_SHOT, period=threshold, callback=lambda *_: func(*args))

        return wrapper

    return decorator
