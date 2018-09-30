from string import punctuation

import daiquiri
import found
import trafaret as t

from aiohttp import web
from argon2.exceptions import VerifyMismatchError

from socialiter.beyond import h
from socialiter.beyond import beyond
from socialiter.beyond import set
from socialiter.beyond import Style


log = daiquiri.getLogger(__name__)


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
    username=t.String(min_length=1, max_length=255) & t.Regexp(r'^[\w]+$'),
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
        # TODO: Replace with DeepValidationException inherit from SocialiterException
        raise t.DataError()


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


@beyond
async def on_register(event):
    pass


def view_register(model):
    style = {
        'display': 'flex',
        'flex-direction': 'column',
        'justify-content': 'center',
        'align-items': 'center',
        'min-height': '100vh',
    }
    shell = h.div(id="shell", style=Style(**style))
    shell.append(h.h1()["register"])
    form = h.form(style=Style(**{'text-align': 'center'}), on_submit=on_register)
    form.append(h.div()[h.input(
        type="text",
        value=model.get('username') or '',
        placeholder='username',
        on_input=set('username')
    )])
    form.append(h.div()[h.input(
        type="password",
        placeholder='password',
        on_input=set('password')
    )])
    form.append(h.div()[h.input(
        type="password",
        placeholder='confirmation',
        on_input=set('confirmation')
    )])
    form.append(h.div()[h.input(type="submit", value="register")])
    shell.append(form)
    return shell


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


def view_login(model):
    style = {
        'display': 'flex',
        'flex-direction': 'column',
        'justify-content': 'center',
        'align-items': 'center',
        'min-height': '100vh',
    }
    shell = h.div(id="shell", style=Style(**style))
    shell.append(h.h1()["socialiter"])
    form = h.form(style=Style(**{'text-align': 'center'}))
    form.append(h.div()[h.input(type="text", placeholder='username')])
    form.append(h.div()[h.input(type="password", placeholder='passowrd')])
    form.append(h.div()[h.input(type="submit", value="login")])
    shell.append(form)
    shell.append(h.div()[h.a(href="/user/register")["register an account"]])
    shell.append(h.div()[h.a(href="/user/recovery")["password recovery"]])
    return shell


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
