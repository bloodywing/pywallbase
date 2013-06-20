from wallbase import *
import unittest
from ConfigParser import ConfigParser


class SearchTestCase(unittest.TestCase):

    def setUp(self):
        self.config = ConfigParser()
        self.config.readfp(open('./test/config.ini'))
        self.wallbase = wallbase.Wallbase(
            self.config.get('Test', 'username'),
            self.config.get('Test', 'password')
        )  # Since we don't want to provide a real login

    def test_search(self):
        self.assertTrue(len(self.wallbase.search("batman", 1)) > 0)
        self.assertIsInstance(self.wallbase.searchbags, wallbase.SearchbagList)
        self.assertIsInstance(self.wallbase.searchbags[0], wallbase.Searchbag)
