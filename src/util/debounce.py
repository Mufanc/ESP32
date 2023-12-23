from machine import Timer


def debounce(threshold: int, timer_id):
    def decorator(func):
        timer = Timer(timer_id)

        def wrapper(*args):
            timer.init(mode=Timer.ONE_SHOT, period=threshold, callback=lambda *_: func(*args))

        return wrapper

    return decorator
