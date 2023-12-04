from beep import Beeper
from ir import Receiver
from misc import debounce
from musics import musics

beep = Beeper(14)

lock = False
playlist = []

keys = [0x44, 0x0C, 0x18, 0x5E, 0x08, 0x1C, 0x5A, 0x42, 0x52, 0x4A]


@debounce(200)
def on_receive(code, _):
    global lock
    try:
        index = keys.index(code[1])

        if index == 0:
            beep.stop()
        else:
            lock = True
            playlist.append(index - 1)
    except ValueError:
        pass


irr = Receiver(25, on_receive)
irr.activate()


def main():
    global lock

    while True:
        while not lock:
            pass

        lock = False
        index = playlist.pop(0)

        beep.music(*musics[index])


if __name__ == '__main__':
    main()
