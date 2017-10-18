# -*- coding: utf-8 -*-
import codecs
import re
import sys
from setuptools import setup


REQUIRES = [
    'click>=4.0',
]

if 'win32' in str(sys.platform).lower():
    # Terminal colors for Windows
    REQUIRES.append('colorama>=0.2.4')

def find_version(fname):
    """Attempts to find the version number in the file names fname.
    Raises RuntimeError if not found.
    """
    version = ''
    with codecs.open(fname, 'r', encoding='utf-8') as fp:
        reg = re.compile(r'__version__ = [\'"]([^\'"]*)[\'"]')
        for line in fp:
            m = reg.match(line)
            if m:
                version = m.group(1)
                break
    if not version:
        raise RuntimeError('Cannot find version information')
    return version

__version__ = find_version('doitlive/__init__.py')

def read(fname):
    with codecs.open(fname, 'r', encoding='utf-8') as fp:
        content = fp.read()
    return content

setup(
    name='doitlive',
    version=__version__,
    description='Because sometimes you need to do it live.',
    long_description=read('README.rst'),
    author='Steven Loria',
    author_email='sloria1@gmail.com',
    url='https://github.com/sloria/doitlive',
    install_requires=REQUIRES,
    license='MIT',
    zip_safe=False,
    keywords='doitlive cli live coding presentations shell',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Environment :: Console',
    ],
    packages=['doitlive'],
    entry_points={
        'console_scripts': [
            'doitlive = doitlive:cli'
        ]
    },
    tests_require=['pytest'],
)
