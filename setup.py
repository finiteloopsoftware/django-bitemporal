#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from setuptools import setup
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup

from bitemporal import __version__


setup(
    name='django-bitemporal',
    version=__version__,
    description='Bitemporal data support for the Django ORM',
    author='Finite Loop Software',
    author_email='admin@finiteloopsoftware.com',
    url='http://github.com/finiteloopsoftware/django-bitemporal/',
    long_description=open('README.rst', 'r').read(),
    packages=[
        'bitemporal',
    ],
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities'
    ],
)
