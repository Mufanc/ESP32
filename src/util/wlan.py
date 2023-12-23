import asyncio

import network


class Network(object):
    def __init__(self):
        self.wlan = network.WLAN(network.STA_IF)

    async def connect(self, ssid, key, ifconfig=None):
        print(f'connecting: {ssid}')

        self.wlan.active(True)
        self.wlan.ifconfig(ifconfig)

        if not self.wlan.isconnected():
            self.wlan.connect(ssid, key)

            while not self.wlan.isconnected():
                await asyncio.sleep(1)

        print(f'network info: {self.wlan.ifconfig()}')

    async def ipaddr(self) -> str | None:
        if not self.wlan.isconnected():
            return None

        return self.wlan.ifconfig()[0]
