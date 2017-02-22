import os
import logging
import unittest

from bimclient import bimclient


class TestServerMethods(unittest.TestCase):
  def setUp(self):
    self.server = bimclient.connect(os.getenv('BIMCLIENT_URL'))

  def test_connect(self):
    self.assertEquals(len(self.server.version), 6)

  def test_login(self):
    self.server.login(os.getenv('BIMCLIENT_USER'),
                      os.getenv('BIMCLIENT_PW'))

  def test_projects(self):
    projects = self.server.projects()
    self.assertGreater(len(projects), 0)


if __name__ == '__main__':
  logging.basicConfig(level=logging.DEBUG)
  unittest.main()
