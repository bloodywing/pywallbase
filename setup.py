#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name="wallbase",
      version="0.2.2",
      provides=['wallbase'],
      description="This provides access to wallbase.cc and their features",
      author="Pierre Geier 'epicmuffin'",
      author_email="muffin@tastyespresso.de",
      url="https://github.com/bloodywing",
      packages=["wallbase"],
      license = "Emailware",
      install_requires=["requests"])
