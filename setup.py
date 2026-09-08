#!/usr/bin/env python

from setuptools import setup


setup(name='tap-uservoice',
      version='1.1.1',
      description='Singer.io tap for extracting data from the Uservoice API',
      author='Fishtown Analytics',
      url='http://fishtownanalytics.com',
      classifiers=['Programming Language :: Python :: 3 :: Only'],
      py_modules=['tap_uservoice'],
      install_requires=[
          'singer-python==6.8.0',
          'backoff==2.2.1',
          'requests==2.34.2',
          'python-dateutil==2.9.0',
          'funcy==2.0',
      ],
      extras_require={
          'dev': [
              'pylint',
              'pytest',
              'coverage',
          ],
      },
      entry_points='''
          [console_scripts]
          tap-uservoice=tap_uservoice:main
      ''',
      packages=['tap_uservoice', 'tap_uservoice.streams'])
