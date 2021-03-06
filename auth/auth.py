import os
import json
from flask import request, _request_ctx_stack
from functools import wraps
from jose import jwt
from urllib.request import urlopen

AUTH0_DOMAIN = os.environ.get('AUTH0_DOMAIN')
ALGORITHMS = os.environ.get('ALGORITHMS')
API_AUDIENCE = os.environ.get('API_AUDIENCE')


class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


# Auth Header

def get_token_auth_header():
    header_token = request.headers.get('Authorization', None)
    if not header_token:
        raise AuthError({
            'code': 'authorization_header_missing',
            'description': 'Authorization header is expected'
        }, 401)

    token_splited = header_token.split()
    if token_splited[0].lower() != 'bearer':
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization header must start with "Bearer".'
        }, 401)
    if len(token_splited) == 1:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Token not found'
        }, 401)
    if len(token_splited) > 2:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization header must be bearer token.'
        }, 401)

    token = token_splited[1]
    return token


def check_permissions(permission, payload):
    if 'permissions' not in payload:
        raise AuthError({
            'code': 'token_expired',
            'description': 'token does not include permissions'
        }, 400)
    if permission not in payload['permissions']:
        raise AuthError({
            'code': 'not_allowed',
            'description': 'user is not allowed to request'
        }, 403)
    return True


def verify_decode_jwt(token):
    json_url = urlopen(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')
    secret = json.loads(json_url.read())
    header_unverified = jwt.get_unverified_header(token)
    rsa = {}

    if 'kid' not in header_unverified:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization malformed'
        }, 401)

    for key in secret['keys']:
        if key['kid'] == header_unverified['kid']:
            rsa = {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e']
            }
    if rsa:
        try:
            payload = jwt.decode(
                token,
                rsa,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer='https://' +
                AUTH0_DOMAIN +
                '/')
            return payload

        except jwt.ExpiredSignatureError:
            raise AuthError({
                'code': 'token_expired',
                'description': 'Token expired.'
            }, 401)

        except jwt.JWTClaimsError:
            raise AuthError({
                'code': 'invalid_claims',
                'description': 'Incorrect claims. Please, check the audience and issuer.'
            }, 401)

        except Exception:
            raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to parse authentication token.'
            }, 400)

    raise AuthError({
        'code': 'invalid_header',
                'description': 'Unable to find the appropriate key.'
    }, 400)


def requires_auth(permission=''):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = get_token_auth_header()
            payload = verify_decode_jwt(token)
            check_permissions(permission, payload)
            return f(payload, *args, **kwargs)

        return wrapper
    return requires_auth_decorator
