#!/usr/bin/env python
'''
Setup for clicrud
'''
from setuptools import setup, find_packages

setup(name='clicrud',
<<<<<<< HEAD
      version='0.1.6',
=======
      version='0.1.5',
>>>>>>> d1c37cd8a7f8eeac2e2a15e0c4fb5f23e2134f62
      description='Brocade CLI CRUD Operations Library.',
      author='Brocade Communications Systems, Inc.',
      author_email='dgee@brocade.com',
      url='http://www.brocade.com/',
      packages=find_packages(),
      install_requires=["paramiko", "multiprocessing", "psutil"],
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: Apache Software License',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.7',
          'Topic :: Software Development :: Libraries',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Topic :: System :: Networking'
      ])
