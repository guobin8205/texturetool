#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name = 'textool',
    version = '1.0.5',
    keywords = ('textool', 'texturepacker'),
    description = 'A command line tool to convert TexturePacker file format.',
    license = 'MIT License',
    install_requires = [
        'Pillow',
        'parse'
    ],
    url = 'https://github.com/guobin8205/texturetool',
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