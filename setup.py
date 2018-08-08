#!/usr/bin/env python

from setuptools import setup


setup(name='tap-uservoice',
      version='0.1.0',
      description='Singer.io tap for extracting data from the Uservoice API',
      author='Fishtown Analytics',
      url='http://fishtownanalytics.com',
      classifiers=['Programming Language :: Python :: 3 :: Only'],
      py_modules=['tap_uservoice'],
      install_requires=[
          'singer-python==5.1.5',
          'backoff==1.3.2',
          'requests==2.18.4',
          'funcy==1.10.1',
      ],
      entry_points='''
          [console_scripts]
          tap-uservoice=tap_uservoice:main
      ''',
      packages=['tap_uservoice', 'tap_uservoice.streams'])
