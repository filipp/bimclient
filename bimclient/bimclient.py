import json
import logging
import base64
import tempfile
import subprocess

import requests


class Session(object):
  def __init__(self, url):
    self.session_id = None
    self.url = url.rstrip('/') + '/'

  def __enter__(self):
    return self

  def __exit__(self, *args):
    pass

  def __dict__(self):
    return self.response

  def request(self, method, data=None):
    """
    Sends a request to the BIM server.
    """
    url = self.url + method
    params = {}

    if self.session_id:
      params['session-id'] = self.session_id

    if data:
      self._request = requests.post(url, json=data)
    else:
      self._request = requests.get(url, params=params)

    self._text = self._request.text

    if method.endswith('get-server-public-key'):
      logging.debug('Got public key: %s' % self._text)
      self.key = self._text
      return self

    try:
      self.response = self._request.json()
    except ValueError:
      raise Exception(self._text)
    
    if method.endswith('get-server-info'):
      self.server = self.response
      self.id = self.response.get('serverId')
      self.version = self.response.get('versionString')
      self.name = self.response.get('friendlyName')
      self.license = self.response.get('license')
      self.platform = self.response.get('platform')

    return self

  def encrypt_password(self, password):
    """
    Encrypts the supplied password with the server's public key
    and returns the encrypted password
    """
    with tempfile.NamedTemporaryFile() as f:
      f.write(self.key)
      logging.debug('Wrote public key to %s' % f.name)
      f.seek(0)
      p = subprocess.Popen(['openssl', 'rsautl', '-encrypt',
                            '-inkey', f.name, '-pubin'],
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE)
      o, e = p.communicate(password + '00000000')
      password = base64.b64encode(o)

      return password

  def login(self, username, password):
    """
    Authenticates with the BIM server.
    """
    self.request('management/latest/get-server-public-key')
    password = self.encrypt_password(password)
    d = {'username': username, 'password': password}
    logging.debug('Auth request: %s' % d)
    self.request('management/latest/create-session', data=d)
    logging.debug(self.response)
    self.user_id = self.response.get('user-id')
    self.session_id = self.response.get('session-id')
    self.session_timeout = self.response.get('expire-timeout')

    if not self.user_id:
      raise Exception('Authentication failed')

    return self

  def projects(self):
    self.request('management/latest/get-projects-by-criterion')
    return self.response


def connect(url):
  with Session(url) as session:
    return session.request('get-server-info')
