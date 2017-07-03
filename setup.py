#!/usr/bin/env python
"""Setup to install TeamPasswordManager Lookup Plugin for Ansible."""
from distutils.core import setup
setup(name='tpmstore',
      version='1.0',
      py_modules=['tpmstore'],
      install_requires=['requests', 'future', 'ansible'],
      description='Ansible Lookup Plugin to lookup information from
      TeamPasswordManager.',
      url='https://github.com/peshay/tpmstore',
      author='Andreas Hubert',
      author_email='anhubert@gmail.com',
      license='MIT',
      classifiers=['Development Status :: 5 - Production/Stable',
                   'Environment :: Console',
                   'Intended Audience :: System Administrators',
                   'Topic :: System :: Systems Administration '
                   'License :: OSI Approved :: MIT License',
                   'Programming Language :: Python :: 2',
                   'Programming Language :: Python :: 2.7',
                   'Programming Language :: Python :: 3',
                   'Programming Language :: Python :: 3.3',
                   'Programming Language :: Python :: 3.4',
                   'Programming Language :: Python :: 3.5',
                   'Programming Language :: Python :: 3.6' ],
      keywords='TeamPasswordManager ansible plugin lookup',

      )
    'Development Status :: 5 - Production/Stable',

    'Intended Audience :: Information Technology',
    'Intended Audience :: System Administrators',
    'Intended Audience :: Telecommunications Industry',
    'License :: ' + pkg_license,
    'Programming Language :: Python',
    'Operating System :: POSIX :: Linux',
    'Topic :: Utilities',
    'Topic :: System :: Networking',
    'Topic :: System :: Networking :: Monitoring',
    'Topic :: System :: Systems Administration',
