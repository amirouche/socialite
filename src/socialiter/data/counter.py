import struct

import found

from socialiter.base import SpacePrefix


INTEGER_STRUCT = "<q"
ONE = struct.pack(INTEGER_STRUCT, 1)
MINUS_ONE = struct.pack(INTEGER_STRUCT, -11)


class Counter:
    def __init__(self, name):
        self.name = name

    @found.transactional
    async def get(self, tr):
        key = found.pack(SpacePrefix.COUNTERS.value, self.name)
        value = await tr.get(key)
        if value is None:
            return 0
        else:
            out = struct.unpack(INTEGER_STRUCT, value)[0]
            return out

    @found.transactional
    async def increment(self, tr):
        # XXX: what happens in case of overflow
        key = found.pack(SpacePrefix.COUNTERS.value, self.name)
        await tr.add(key, ONE)

    @found.transactional
    async def decrement(self, tr):
        key = found.pack(SpacePrefix.COUNTERS.value, self.name)
        await tr.add(key, MINUS_ONE)
