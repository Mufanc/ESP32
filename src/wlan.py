import asyncio

import network


async def connect(ssid, key):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    if not wlan.isconnected():
        wlan.connect(ssid, key)

        while not wlan.isconnected():
            await asyncio.sleep(1)

    print(f'network info: {wlan.ifconfig()}')
