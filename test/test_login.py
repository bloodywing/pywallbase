from wallbase import *
import requests
import unittest
from ConfigParser import ConfigParser


class LoginTestCase(unittest.TestCase):

    def setUp(self):
        self.config = ConfigParser()
        self.config.readfp(open('./test/config.ini'))
        self.wallbase = wallbase.Wallbase(
            self.config.get('Test', 'username'),
            self.config.get('Test', 'password')
        )  # Since we don't want to provide a real login

    def test_login(self):
        self.assertIsInstance(self.wallbase.cookies, requests.cookies.RequestsCookieJar)

    def testDown(self):
        self.wallbase = None
        self.config = None