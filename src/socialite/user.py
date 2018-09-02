from string import punctuation

import trafaret as t
from trafaret import DataError
from argon2.exceptions import VerifyMismatchError

from socialite.helpers import no_auth


# account

def strong_password(string):
    """Check that ``string`` is strong enough password"""
    if (any(char.isdigit() for char in string)
            and any(char.islower() for char in string)
            and any(char.isupper() for char in string)
            and any(char in punctuation for char in string)):
        return string
    else:
        raise t.DataError('Password is not strong enough')


account_new_validate = t.Dict(
    username=t.String(min_length=1, max_length=255) & t.Regexp(r'^[\w-]+$'),
    password=t.String(min_length=10, max_length=255) & strong_password,
    validation=t.String(),
)


@no_auth
async def account_new(request):
    """Create a new account raise bad request in case of error"""
    data = await request.json()
    try:
        data = account_new_validate(data)
    except t.DataError as exc:
        return web.json_response(exc.as_dict(), status=400)
    else:
        errors = dict()
        # check that the user is not already taken
        async with request.app['asyncpg'].acquire() as cnx:
            # TODO: try/except postgresql UniqueViolationError will be more
            # idiomatic
            # TODO: do that in transaction!
            query = 'SELECT COUNT(uid) FROM users WHERE username = $1;'
            count = await cnx.fetchval(query, data['username'])
            if count != 0:
                errors['username'] = 'There is already an user with that username'
            # check that the passwords are the same
            if data['password'] != data['validation']:
                errors['validation'] = 'Does not match password'
            # if there is an error return it otherwise, say it's ok
            if errors:
                return web.json_response(errors, status=400)

            password = request.app['hasher'].hash(data['password'])
            query = 'INSERT INTO users (username, password) VALUES ($1, $2)'
            await cnx.execute(query, data['username'], password)
            return web.json_response({})


@no_auth
async def account_login(request):
    """Try to login an user, return token if successful"""
    data = await request.json()
    # FIXME: validate and always report to the user that the login failed
    async with request.app['asyncpg'].acquire() as cnx:
        username = data['username']
        query = 'SELECT uid, password FROM users WHERE username = $1'
        row = await cnx.fetchrow(query, username)
        if row is None:
            return web.Response(status=401)
        else:
            try:
                request.app['hasher'].verify(row['password'], data['password'])
            except VerifyMismatchError:
                return web.Response(status=401)
            else:
                token = request.app['signer'].sign(str(row['uid']))
                token = token.decode('utf-8')
                out = dict(token=token)
            return web.json_response(out)
