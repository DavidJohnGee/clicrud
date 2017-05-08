#!/usr/bin/env python
'''
Setup for clicrud
'''
from setuptools import setup, find_packages

setup(name='clicrud',
      version='0.3.03',
      description='Brocade CLI CRUD Operations Library.',
      author='Brocade Communications Systems, Inc.',
      author_email='dgee@brocade.com',
      url='http://www.brocade.com/',
      packages=find_packages(),
      install_requires=["paramiko>=2.0.2", "multiprocessing>=2.6.2.1", "psutil>=4.3.1", "jinja2"],
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
