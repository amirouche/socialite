"""Basic in-memory in-process cache with expiration"""

class MemoException(Exception):
    pass


class DeadKey(MemoException):
    """The key expired"""
    pass


class Value:
    """Memo's dictionary's value wrapper"""

    __slots__ = ('data', 'expire_at', 'expiration_callback')

    def __init__(self, data, expire_at=None, expiration_callback=None):
        self.data = data
        self.expire_at = expire_at
        self.expiration_callback = expiration_callback


class Memo:
    """FIXME"""

    def __init__(self, app, loop):
        self._container = dict()
        self._loop = loop
        self.app = app

    async def get(self, key):
        """Try to get the value at ``key`` it's not dead.

        If the key is dead, call the value's expriation callback
        and return what the expiration callback returns.

        The expiration callback has the responsability to setup
        a "new" key for the value"""
        value = self._container[key]
        if value.expire_at is None:
            return value.data
        else:
            # the value has an expiration time
            now = self._loop.time()
            if value.expire_at > now:
                # the value expired, delete the key if there is no expiration
                # callback otherwise call the expiration callback
                if value.expiration_callback is None:
                    del self._container[key]
                    raise DeadKey('%s is dead' % key)
                else:
                    out = await value.expiration_callback(self)
                    return out
            else:
                # the value is still valid
                return value.data

    def set(self, key, value, ttl=None, expiration_callback=None):
        """Create a value at key in the memo dictionary"""
        if ttl is None:
            expire_at = None
        else:
            expire_at = self._loop.time() + ttl
        value = Value(value, expire_at, expiration_callback)
        self._container[key] = value
