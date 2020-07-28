import sys
import pprint
import json
from urllib.parse import urlencode
from urllib.request import (
  Request,
  urlopen,
  HTTPSHandler,
  build_opener,
  install_opener
)
from urllib.error import (
  HTTPError,
  URLError
)
from http.client import HTTPException

__DEBUG__ = 0

class Auth0Manager():
  # Configuration Values
  AUDIENCE = "https://kilauea.eu.auth0.com/api/v2/"
  DOMAIN = "kilauea.eu.auth0.com"
  CLIENT_ID = "XP3LFijseyLDbqxwwxJ7NJj8U8uVqKkn"
  CLIENT_SECRET = "Z5cz-uPcroAxW8MDCZAl_Pxa2YY86baXeFzJuxuVf0ak9nkAm2L4HKeWDayZDqrq"
  GRANT_TYPE = "client_credentials" # OAuth 2.0 flow to use

  def __init__(self):
    # Get an Access Token from Auth0
    self.base_url = "https://{domain}".format(domain=Auth0Manager.DOMAIN)
    values = {
      'client_id': Auth0Manager.CLIENT_ID,
      'client_secret': Auth0Manager.CLIENT_SECRET,
      'audience': Auth0Manager.AUDIENCE,
      'grant_type': Auth0Manager.GRANT_TYPE
    }
    data = urlencode(values)
    data = data.encode('ascii')
    req = Request(self.base_url + "/oauth/token", data=data)
    response = urlopen(req)
    oauth = json.loads(response.read())
    self.access_token = oauth['access_token']

    if __DEBUG__:
      # Set a logger to debug the https requests
      http_logger = HTTPSHandler(debuglevel = 1)
      opener = build_opener(http_logger)
      install_opener(opener)

  def __request(self, api, data=None, method='GET'):
    # Make an API request
    try:
      res = None
      headers = {
        'Authorization': 'Bearer ' + self.access_token,
        'Content-Type': 'application/json'
      }

      if data:
        data = json.dumps(data).encode('ascii')

      req = Request(self.base_url + "/api/v2/%s" % api, headers=headers, data=data, method=method)
      response = urlopen(req)
      if response.length == 0:
        res = response.status
      else:
        res = json.loads(response.read())
    except HTTPError as e:
      print('HTTPError = ' + str(e.code) + ' ' + str(e.reason))
    except URLError as e:
      print('URLError = ' + str(e.reason))
    except HTTPException as e:
      print('HTTPException')
    except:
      print(sys.exc_info())
    finally:
      return res

  def get(self, api):
    return self.__request(api)

  def post(self, api, values):
    return self.__request(api, data=values, method='POST')

  def delete(self, api, values):
    return self.__request(api, data=values, method='DELETE')

  def getClients(self, name=None):
    res = self.get('clients')
    if name:
      clients = []
      for client in res:
        if client['name'] == name:
          clients.append(client)
      return clients
    return res

  def getResourceServers(self, name=None):
    res = self.get('resource-servers')
    if name:
      resources = []
      for resource in res:
        if resource['name'] == name:
          resources.append(resource)
      return resources
    return res

  def getRoles(self):
    return self.get('roles')

  def getUsers(self):
    return self.get('users')

  def getRole(self, roleId):
    return self.get('roles/%s' % roleId)

  def getRoleUsers(self, roleId):
    return self.get('roles/%s/users' % roleId)

  def getRolePermissions(self, roleId, resource_server_name=None):
    res = self.get('roles/%s/permissions' % roleId)
    if resource_server_name:
      permissions = []
      for permission in res:
        if permission['resource_server_name'] == resource_server_name:
          permissions.append(permission)
      return permissions
    return res

  def patchRolePermissions(self, roleId, new_permissions, resource_server_name=None):
    permissions = self.getRolePermissions(roleId, resource_server_name)
    permissions_name = [permission['permission_name'] for permission in permissions]
    resource_server_identifier = 'coffeeshop'
    deleted_permissions = []
    added_permissions = []
    for new_permission in new_permissions:
      if (new_permission['valid'] == True) and (not new_permission['name'] in permissions_name):
        added_permissions.append({"permission_name": new_permission['name'], 'resource_server_identifier': resource_server_identifier})
      elif (new_permission['valid'] == False) and (new_permission['name'] in permissions_name):
        deleted_permissions.append({"permission_name": new_permission['name'], 'resource_server_identifier': resource_server_identifier})
    if len(deleted_permissions) > 0:
      data = {"permissions": deleted_permissions}
      res = self.delete('roles/%s/permissions' % roleId, data)
    if len(added_permissions) > 0:
      data = {"permissions": added_permissions}
      res = self.post('roles/%s/permissions' % roleId, data)

  def getResourceServerAndRoles(self, resource_server_name):
    resources = self.getResourceServers(resource_server_name)
    resource_and_roles = {}
    if len(resources) == 1:
      resources[0]['scopes'].remove({'description': 'Can manage barista users', 'value': 'manage:baristas'})
      resources[0]['scopes'].remove({'description': 'Can manage manager users', 'value': 'manage:managers'})
      resource_and_roles['resource_server'] = resources[0]
      resource_and_roles['roles'] = []
      roles = self.getRoles()
      for role in roles:
        permissions = self.getRolePermissions(role['id'], resource_server_name)
        if len(permissions) > 0:
          resource_and_roles['roles'].append(role)
    return resource_and_roles

# Standard boilerplate to call the main() function.
if __name__ == '__main__':
  pp = pprint.PrettyPrinter(indent=2)

  m2m = Auth0Manager()

  resource_server_name = 'Coffee Shop'
  coffee_shop_server_and_roles = m2m.getResourceServerAndRoles(resource_server_name)
  pp.pprint(coffee_shop_server_and_roles)

  if len(coffee_shop_server_and_roles) > 0:
    print('%s Roles:' % resource_server_name)
    for role in coffee_shop_server_and_roles['roles']:
      permissions = m2m.getRolePermissions(role['id'], resource_server_name)
      if len(permissions) > 0:
        print('- %s:' % role['name'])
        print('  - Permissions:')
        for permission in permissions:
          print('    %s' % permission['permission_name'])
      
        users = m2m.getRoleUsers(role['id'])
        print('  - Users:')
        for user in users:
          print('    %s' % user['name'])

