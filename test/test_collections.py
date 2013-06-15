from wallbase import *
import unittest
from ConfigParser import ConfigParser
from random import getrandbits


class CollectionsTestCase(unittest.TestCase):

    def setUp(self):
        self.randomstring = str(getrandbits(32))
        self.config = ConfigParser()
        self.added_collection = False
        self.config.readfp(open('./test/config.ini'))
        self.wallbase = wallbase.Wallbase(
            self.config.get('Test', 'username'),
            self.config.get('Test', 'password')
        )  # Since we don't want to provide a real login

    def test_addcollection(self):
        self.added_collection = self.wallbase.add_collection("T" + self.randomstring)
        self.assertIsNot(self.added_collection, False)

    def test_addtofavorites(self):
        self.assertTrue(self.wallbase.add_to_favorites(129791, self.added_collection))

    def tearDown(self):
        self.wallbase.del_collection(int(self.added_collection))
        self.wallbase = None
        self.config = None
        