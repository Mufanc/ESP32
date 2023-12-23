import asyncio
import heapq
from time import ticks_ms, ticks_add

from asyncio.event import ThreadSafeFlag
from machine import Timer


class PriorityQueue(object):
    def __init__(self):
        self.queue = []

    def add(self, item):
        heapq.heappush(self.queue, item)

    def pop(self):
        return heapq.heappop(self.queue)

    def peek(self):
        return self.queue[0]

    def __len__(self):
        return len(self.queue)


class Scheduler(object):

    _instance = None

    @classmethod
    def init(cls, timer_id: int):
        cls._instance = Scheduler(timer_id)

    @classmethod
    def instance(cls):
        return cls._instance

    def __init__(self, timer_id: int):
        self._timer = Timer(timer_id)
        self._pending_tasks = PriorityQueue()
        self._running_tasks = []
        self._lock = ThreadSafeFlag()

        asyncio.create_task(self._loop())

    async def _loop(self):
        while True:
            await self._lock.wait()
            self._lock.clear()
            self._running_tasks.pop(0)()

    def _callback(self, *_):
        _, callback, in_irq = self._pending_tasks.pop()

        if in_irq:
            callback()
        else:
            self._running_tasks.append(callback)
            self._lock.set()

        if len(self._pending_tasks) != 0:
            self._refresh()

    def _refresh(self):
        current_time = ticks_ms()
        delay = self._pending_tasks.peek()[0] - current_time
        self._timer.init(mode=Timer.ONE_SHOT, period=delay, callback=self._callback)

    def call_later(self, callback, delay_ms: int, in_irq: bool = False):
        current_time = ticks_ms()
        self._pending_tasks.add((ticks_add(current_time, delay_ms), callback, in_irq))
        self._refresh()
