#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name = 'textool',
    version = '0.0.6',
    keywords = ('textool', 'texturepacker'),
    description = 'A command line tool to convert TexturePacker file format. code base on https://github.com/justbilt/untp for author justbilt.',
    license = 'MIT License',
    install_requires = [
        'Pillow',
        'parse'
    ],
    url = '',
    author = 'guobin',
    author_email = 'guobin2013@hotmail.com',
    packages = find_packages("src"),
    package_dir = {'':'src'},
    entry_points = {
        'console_scripts': [
            'textool = textool.textool:main',
        ],
    }
)