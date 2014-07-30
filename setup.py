#!/usr/bin/env python

from setuptools import setup, find_packages
import fnmatch, os

packages = [pkg for pkg in find_packages('.') if pkg.startswith('pyupdater')]

setup(name='py4a-updater',
	  version='1.0',
	  description='Private updater for python-for-android applications',
	  author='Ryan Pessa',
	  author_email='dkived@gmail.com',
	  packages=packages,

	  install_requires=[
		'kivy>=1.8.0',
		'jnius'
	  ],
	  
	  )

