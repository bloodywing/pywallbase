#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name="wallbase",
      version="0.1",
      provides=['wallbase'],
      description="This provides access to wallbase.cc and their features",
      author="Pierre Geier 'epicmuffin'",
      author_email="muffin@tastyespresso.de",
      url="https://github.com/bloodywing",
      packages=["wallbasefs"],
      license = "Emailware",
      install_requires=["requests"])
