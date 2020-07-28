import json
from flask import request, _request_ctx_stack, session
from functools import wraps
from jose import jwt
from urllib.request import urlopen
from authlib.integrations.flask_client import OAuth
import app.mod_auth.constants as constants

AUTH0_DOMAIN = 'kilauea.eu.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'calendar'

## AuthError Exception
'''
AuthError Exception
A standardized way to communicate auth failure modes
'''
class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


## Auth Header

'''
@DONE implement get_token_auth_header() method
    it should attempt to get the header from the request
        it should raise an AuthError if no header is present
    it should attempt to split bearer and the token
        it should raise an AuthError if the header is malformed
    return the token part of the header
'''
def get_token_auth_header():
    """Obtains the Access Token from the Authorization Header
    """
    auth = request.headers.get('Authorization', None)
    if not auth:
        raise AuthError({
            'code': 'authorization_header_missing',
            'description': 'Authorization header is expected.'
        }, 401)

    parts = auth.split()
    if parts[0].lower() != 'bearer':
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization header must start with "Bearer".'
        }, 401)

    elif len(parts) == 1:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Token not found.'
        }, 401)

    elif len(parts) > 2:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization header must be bearer token.'
        }, 401)

    token = parts[1]
    return token

'''
@implement check_permissions(permission, payload) method
    @INPUTS
        permission: string permission (i.e. 'post:drink')
        payload: decoded jwt payload

    it should raise an AuthError if permissions are not included in the payload
        !!NOTE check your RBAC settings in Auth0
    it should raise an AuthError if the requested permission string is not in the payload permissions array
    return true otherwise
'''
def check_permissions(permission, payload):
  if 'permissions' not in payload:
    raise AuthError({
      'code': 'invalid_claims',
      'description': 'Permissions not included in JWT.'
    }, 400)

  if permission not in payload['permissions']:
    raise AuthError({
      'code': 'unauthorized',
      'description': 'Permission not found.'
    }, 401)
  return True

'''
@implement verify_decode_jwt(token) method
    @INPUTS
        token: a json web token (string)

    it should be an Auth0 token with key id (kid)
    it should verify the token using Auth0 /.well-known/jwks.json
    it should decode the payload from the token
    it should validate the claims
    return the decoded payload

    !!NOTE urlopen has a common certificate error described here: https://stackoverflow.com/questions/50236117/scraping-ssl-certificate-verify-failed-error-for-http-en-wikipedia-org
'''
def verify_decode_jwt(token):
  jsonurl = urlopen(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')
  jwks = json.loads(jsonurl.read())
  unverified_header = jwt.get_unverified_header(token)
  rsa_key = {}
  if 'kid' not in unverified_header:
    raise AuthError({
      'code': 'invalid_header',
      'description': 'Authorization malformed.'
    }, 401)

  for key in jwks['keys']:
    if key['kid'] == unverified_header['kid']:
      rsa_key = {
        'kty': key['kty'],
        'kid': key['kid'],
        'use': key['use'],
        'n': key['n'],
        'e': key['e']
      }
  if rsa_key:
    try:
      payload = jwt.decode(
        token,
        rsa_key,
        algorithms=ALGORITHMS,
        audience=API_AUDIENCE,
        issuer='https://' + AUTH0_DOMAIN + '/'
      )
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
      }, 401)
  
  raise AuthError({
    'code': 'invalid_header',
    'description': 'Unable to find the appropriate key.'
  }, 401)

'''
@implement @requires_auth(permission) decorator method
    @INPUTS
        permission: string permission (i.e. 'post:drink')

    it should use the get_token_auth_header method to get the token
    it should use the verify_decode_jwt method to decode the jwt
    it should use the check_permissions method validate claims and check the requested permission
    return the decorator which passes the decoded payload to the decorated method
'''
def requires_auth(permission=None):
  def requires_auth_decorator(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
      if constants.PROFILE_KEY not in session:
        raise AuthError({
          'code': 'unauthorized',
          'description': 'Permission not found.'
        }, 401)
      if constants.JWT_TOKEN not in session:
        raise AuthError({
          'code': 'invalid_header',
          'description': 'Token not found.'
        }, 401)
      token = session[constants.JWT_TOKEN] #get_token_auth_header()
      payload = verify_decode_jwt(token)
      if permission:
        check_permissions(permission, payload)
        return f(payload, *args, **kwargs)
      else:
        return f(*args, **kwargs)

    return wrapper

  return requires_auth_decorator

# class Auth0:
#   clientId = 'orQ0YNyItHpZHVAwpG2PaRMWjL82qJwg' # the client id generated for the auth0 app
#   callbackURL = 'http://localhost:5000/auth/callback/' # the base url of the running ionic application.
#   apiServerUrl = 'http://localhost:5000' # // the running FLASK api server url

#   @staticmethod
#   def build_login_link(callbackPath=''):
#     link = 'https://'
#     link += AUTH0_DOMAIN
#     link += '/authorize?'
#     link += 'audience=' + API_AUDIENCE + '&'
#     link += 'response_type=token&'
#     link += 'client_id=' + Auth0.clientId + '&'
#     link += 'redirect_uri=' + Auth0.callbackURL + callbackPath
#     return link

#   @staticmethod
#   def build_logout_link(callbackPath=''):
#     link = 'https://'
#     link += AUTH0_DOMAIN
#     link += '/v2/logout?'
#     link += 'client_id=' + this.clientId + '&'
#     link += 'returnTo=' + this.callbackURL + callbackPath
#     return link
