from string import punctuation

import daiquiri
import found
import trafaret as t

from aiohttp import web
from argon2.exceptions import VerifyMismatchError

from socialite.helpers import no_auth


log = daiquiri.getLogger(__name__)


@no_auth
async def register_get(request):
    context = {'settings': request.app['settings'], 'errors': {}, 'values': {}, }
    return request.app.render('user/register.jinja2', request, context)


def strong_password(string):
    """Check that ``string`` is strong enough password"""
    if (any(char.isdigit() for char in string)
            and any(char.islower() for char in string)
            and any(char.isupper() for char in string)
            and any(char in punctuation for char in string)):
        return string
    else:
        raise t.DataError('Password is not strong enough')


user_validate = t.Dict(
    username=t.String(min_length=1, max_length=255) & t.Regexp(r'^[\w-]+$'),
    password=t.String(min_length=10, max_length=255) & strong_password,
    validation=t.String(),
)


@found.transactional
async def register(tr, sparky, username, password):
    tuples = (
        (sparky.var('uid'), "name", username),
    )
    actors = await sparky.where(tr, *tuples)
    try:
        actors[0]
    except IndexError:
        uid = await sparky.uuid(tr)
        tuples = (
            (uid, 'name', username),
            (uid, 'password', password),
            (uid, 'is a', 'user'),
        )
        await sparky.add(tr, *tuples)
        return uid
    else:
        # TODO: Replace with DeepValidationException inherit from SocialiteException
        raise t.DataError()


@no_auth
async def register_post(request):
    """Create a new user raise bad request in case of error"""
    context = {
        'settings': request.app['settings'],
        'errors': {},
        'values': {},
    }
    data = await request.post()
    try:
        data = user_validate(data)
    except t.DataError as exc:
        log.debug('shallow validation failed')
        context['errors'] = exc.as_dict()
        context['values']["username"] = data.get("username")
        return request.app.render('user/register.jinja2', request, context)
    else:
        log.debug('shallow validation done')
        # Check that the passwords are the same
        if data['password'] != data['validation']:
            log.debug('deep validation failed: passwords do not match')
            context['values']["username"] = data.get("username")
            context['errors']['password'] = "Doesn't match validation"  # nosec
            return request.app.render('user/register.jinja2', request, context)
        # Check that the username is not already taken and register the new user
        password = request.app['hasher'].hash(data['password'])
        username = data['username']
        try:
            await register(request.app['db'], request.app['sparky'], username, password)
        except t.DataError:
            log.debug('deep validation failed: username taken')
            context['errors']['username'] = "Username already in use"
            return request.app.render('user/register.jinja2', request, context)
        else:
            log.debug("accout created with username='%s'", username)
            return web.HTTPSeeOther(location='/')


@found.transactional
async def user_by_username(tr, sparky, username):
    tuples = (
        (sparky.var('uid'), 'name', username),
        (sparky.var('uid'), 'password', sparky.var('password')),
    )
    users = await sparky.where(tr, *tuples)
    assert len(users) == 1
    user = users[0]
    user = user.set('name', username)
    return user


@no_auth
async def login_post(request):
    """Try to login an user, return token if successful"""
    data = await request.post()
    username = data['username']
    try:
        user = await user_by_username(request.app["db"], request.app['sparky'], username)
    except IndexError:
        context = {"settings": request.app["settings"], "error": "Wrong credentials"}
        return request.app.render('user/login.jinja2', request, context)
    else:
        password = data["password"]
        try:
            request.app['hasher'].verify(user['password'], password)
        except VerifyMismatchError:
            context = {"settings": request.app["settings"], "error": "Wrong credentials"}
            return request.app.render('user/login.jinja2', request, context)
        else:
            uid = user['uid']
            token = request.app['signer'].sign(uid.hex)
            token = token.decode('utf-8')
            redirect = web.HTTPSeeOther(location='/home')
            max_age = request.app['settings'].TOKEN_MAX_AGE
            redirect.set_cookie('token', token, max_age=max_age)
            raise redirect


@no_auth
async def login_get(request):
    context = {'settings': request.app['settings'], 'errors': {}}
    return request.app.render('user/login.jinja2', request, context)


@found.transactional
async def user_by_uid(tr, sparky, uid):
    tuples = (
        (uid, 'name', sparky.var('name')),
        (uid, 'password', sparky.var('password')),
    )
    users = await sparky.where(tr, *tuples)
    assert len(users) == 1
    user = users[0]
    user = user.set('uid', uid)
    return user
