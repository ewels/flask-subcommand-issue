#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name = 'fsksc',
    author = 'Phil Ewels',
    author_email = 'phil.ewels@scilifelab.se',
    url = 'https://github.com/ewels/flask-subcommand-issue',
    scripts = ['scripts/fsksc'],
    entry_points = {
        'console_scripts': [
            'fsksc_server=fsksc.server.app:server'
        ],
    },
    install_requires = [
        'click',
        'flask',
    ]
)
