#!/usr/bin/env python
"""
sentry-xmpp
==============

An extension for Sentry which integrates with XMPP.
"""
from setuptools import setup, find_packages

# See http://stackoverflow.com/questions/9352656/python-assertionerror-when-running-nose-tests-with-coverage
# for why we need to do this.
from multiprocessing import util


tests_require = [
    'nose>=1.1.2',
    'mimic>=0.0.2',
]

install_requires = [
    'sentry>=5.4.1',
    'sleekxmpp>=1.1.1'
]

setup(
    name='sentry-xmpp',
    version='0.0.1',
    author='Christopher Proto',
    author_email='chroto24@gmail.com',
    url='http://chrispro.to/projects/sentry-xmpp',
    description='A Sentry extension which integrates with XMPP',
    long_description=__doc__,
    license='MIT',
    packages=find_packages(exclude=['tests']),
    zip_safe=False,
    install_requires=install_requires,
    tests_require=tests_require,
    extras_require={'test': tests_require},
    test_suite='nose.collector',
    entry_points={
        'sentry.plugins': [
            'xmpp = sentry_xmpp.plugin:XMPPMessage'
        ],
    },
    include_package_data=True,
    classifiers=[
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: OS Independent',
        'Topic :: Software Development'
    ],
)
