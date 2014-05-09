#!/usr/bin/env python

import sys

from distutils.core import setup

# this affects the names of all the directories we do stuff with
sys.path.insert(0, './')

from sslfetch import __version__


#__version__ = os.getenv('VERSION', default='9999')


setup(name          = 'ssl-fetch',
      version       = __version__,
      description   = "A python interface wrapper for the dev-python/requests package",
      author        = 'Brian Dolbec',
      author_email  = 'dolsen@gentoo.org',
      url           = "https://github.com/dol-sen/ssl-fetch",
      packages      = ['sslfetch'],
      license       = 'GPL-2',
      long_description=open('README.md').read(),
      keywords='ssl',
      classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: GNU General Public License v2 (GPLv2)'
          'Programming Language :: Python :: 2.7',
          'Operating System :: OS Independent',
          'Topic :: System :: Systems Administration'
          ],
      )

