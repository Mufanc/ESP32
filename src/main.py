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

keys = [0x44, 0x16, 0x0C, 0x18, 0x5E, 0x08, 0x1C, 0x5A, 0x42, 0x52, 0x4A] + [0x07]

lock = ThreadSafeFlag()
playlist = []


@debounce(200, 2)
def on_receive(code, _):
    try:
        index = keys.index(code[1])

        if index == -1:
            return

        if index >= 10:  # 截屏
            beep.dump_and_stop()
            return

        if index == 0:
            beep.stop()
        elif not beep.is_playing():
            playlist.append(index - 1)
            lock.set()
    except ValueError:
        pass


irr = Receiver(25, on_receive)
irr.activate()


def play_music_json(music: str):
    music_info = json.loads(music)
    beep.play(music_info['D'], music_info['V'], music_info['K'], music_info['T'])


def on_request(req: HttpRequest):
    play_music_json(req.body.decode())

    with open('/saved_music', 'wb') as fp:
        fp.write(req.body)

    return ''


async def player_main():
    while True:
        await lock.wait()
        lock.clear()
        index = playlist.pop(0)

        if index == 0:
            try:
                with open('/saved_music', 'r') as fp:
                    if music := fp.read():
                        play_music_json(music)
            except Exception as err:
                print(err)
        else:
            beep.play(*musics[index - 1])


async def main():
    Scheduler.init(1)

    wlan = Network()
    await wlan.connect(configs.ssid, configs.passwd, configs.ifconfig)

    asyncio.create_task(player_main())

    server = HttpServer()
    await server.bind(80)
    await server.serve_forever(on_request)


if __name__ == '__main__':
    ev_loop = asyncio.new_event_loop()
    ev_loop.run_until_complete(main())
