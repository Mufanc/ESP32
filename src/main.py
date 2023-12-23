import asyncio
import json

from asyncio.event import ThreadSafeFlag

import configs
from beep import Beep
from display import Screen
from musics import musics
from server import HttpServer, HttpRequest
from util.debounce import debounce
from util.ir import Receiver
from util.scheduler import Scheduler
from util.wlan import Network

screen = Screen(18, 23)
beep = Beep(14, screen)

keys = [0x44, 0x0C, 0x18, 0x5E, 0x08, 0x1C, 0x5A, 0x42, 0x52, 0x4A] + [0x07]

lock = ThreadSafeFlag()
playlist = []


@debounce(200, 2)
def on_receive(code, _):
    try:
        index = keys.index(code[1])

        if index == -1:
            return

        if index >= 9:  # 截屏
            beep.dump_and_stop()
            return

        if index == 0:
            beep.stop()
        elif not beep.is_playing():
            playlist.append(index)
            lock.set()
    except ValueError:
        pass


irr = Receiver(25, on_receive)
irr.activate()


def on_music(req: HttpRequest):
    music_info = json.loads(req.body)
    beep.play(music_info['D'], music_info['V'], music_info['K'], music_info['T'])
    return ''


async def player_main():
    while True:
        await lock.wait()
        lock.clear()
        index = playlist.pop(0)
        beep.play(*musics[index - 1])


async def main():
    Scheduler.init(1)

    wlan = Network()
    await wlan.connect(configs.ssid, configs.passwd, configs.ifconfig)

    asyncio.create_task(player_main())

    server = HttpServer()
    await server.bind(80)
    await server.serve_forever(on_music)


if __name__ == '__main__':
    ev_loop = asyncio.new_event_loop()
    ev_loop.run_until_complete(main())
