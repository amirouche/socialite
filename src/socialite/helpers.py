import async_timeout


async def fetch(session, url):
    async with async_timeout.timeout(60):
        async with session.get(url) as response:
            return await response.text()


def no_auth(handler):
    """Decorator to tell the ``middleware_check_auth`` to not check for the token

    """
    handler.no_auth = True
    return handler
