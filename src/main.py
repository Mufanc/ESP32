import asyncio

import configs
import wlan
from display import Screen
from rain_detector import RainDetector
from supervisor import Supervisor

detector = RainDetector(34)
screen = Screen(18, 23)


async def loop():
    supervisor = Supervisor.create(configs.supervisor_ip, configs.supervisor_port)

    while True:
        value = detector.read()
        level = (1 - (value + 1) / 4096) * 100

        state = detector.parse_state(value)

        if state == detector.NO_RAIN:
            screen.image('images/nahida_clip.bin')  # depends:images/nahida_clip.bin
        elif state == detector.RAINING_SMALL:
            screen.message("Raining\nBut not heavily")
        else:
            screen.message(f"Raining\nIntensity={level:.1f}%")

        if supervisor:
            supervisor.send(f'\r\x1b[2KIntensity = {level:.1f}%')

        await asyncio.sleep_ms(200)


async def main():
    await wlan.connect(configs.wlan_ssid, configs.wlan_password)
    await loop()


if __name__ == '__main__':
    event_loop = asyncio.new_event_loop()
    event_loop.run_until_complete(main())
