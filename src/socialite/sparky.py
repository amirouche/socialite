from uuid import uuid4

import daiquiri
from immutables import Map

from socialite import fdb
from socialite.base import SubspacePrefix
from socialite.base import SocialiteException


log = daiquiri.getLogger(__name__)


SPARKY = SubspacePrefix.SPARKY.value
PREFIX_DATA = b'\x00'
PREFIX_UUID = b'\x01'
PREFIX_LENGTH = len(SPARKY + PREFIX_DATA)


@fdb.transactional
async def random_uid(tr):
    uid = uuid4().hex
    key = SPARKY + PREFIX_UUID + uid.encode('utf8')
    value = await tr.get(key)
    if value is None:
        tr.set(key, b'')
        return uid
    raise SocialiteException('Unlikely Error!')


@fdb.transactional
async def all(tr):
    start = SPARKY + PREFIX_DATA
    end = fdb.strinc(SPARKY + PREFIX_DATA)
    msg = "fetching everything between start=%r and end=%r"
    log.debug(msg, start, end)
    out = []
    async for key, value in tr.get_range(start, end):
        key = key[PREFIX_LENGTH:]
        graph, subject, predicate = fdb.unpack(key)
        object = fdb.unpack(value)[0]
        out.append((graph, subject, predicate, object))
    return out


@fdb.transactional
async def add(tr, *quads):
    for quad in quads:
        key = SPARKY + PREFIX_DATA + fdb.pack(quad[:3])
        value = fdb.pack((quad[3],))
        tr.set(key, value)


@fdb.transactional
async def remove(tr, *quads):
    for quad in quads:
        key = SPARKY + PREFIX_DATA + fdb.pack(quad[:3])
        tr.clear(key)


class var:

    __slots__ = ('name',)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<var %r>' % self.name


def match(pattern, quad, binding):
    for target, value in zip(pattern, quad):
        if isinstance(target, var):
            try:
                bound = binding[target.name]
            except KeyError:
                binding = binding.set(target.name, value)
                continue
            else:
                if bound == value:
                    continue
                else:
                    return None
        else:
            if target == value:
                continue
            else:
                return None
    return binding


@fdb.transactional
async def where(tr, pattern, *patterns):
    seed = []
    quads = await all(tr)
    # poor man do-while
    for quad in quads:
        binding = Map()
        binding = match(pattern, quad, binding)
        if binding is not None:
            seed.append(binding)
    bindings = seed
    # while
    for pattern in patterns:
        next_bindings = []
        for binding in bindings:
            quads = await all(tr)
            for quad in quads:  # XXX: quads ftw!
                new = match(pattern, quad, binding)
                if new is not None:
                    next_bindings.append(new)
        bindings = next_bindings
    return bindings
