#!/usr/bin/env python
# -*- coding: utf-8 -*-

# setup.py
"""
A setuptools setup file for DVH Analytics MLC Analyzer
"""
# Copyright (c) 2016-2021 Dan Cutright
# This file is part of DVH Analytics MLC Analyzer, released under a BSD license
#    See the file LICENSE included with this distribution, also
#    available at https://github.com/cutright/DVHA-MLCA

from setuptools import setup, find_packages
from mlca._version import __version__


with open('requirements.txt', 'r') as doc:
    requires = [line.strip() for line in doc]

with open('README.rst', 'r') as doc:
    long_description = doc.read()

CLASSIFIERS = [
    "License :: OSI Approved :: MIT License",
    "Intended Audience :: End Users/Desktop",
    "Intended Audience :: Healthcare Industry",
    "Intended Audience :: Science/Research",
    "Natural Language :: English",
    "Development Status :: 4 - Beta",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Operating System :: OS Independent",
    "Topic :: Scientific/Engineering :: Medical Science Apps.",
    "Topic :: Scientific/Engineering :: Physics"]


setup(
    name='dvha-mlca',
    include_package_data=True,
    python_requires='>3.5',
    packages=find_packages(),
    version=__version__,
    description='Batch analyze DICOM-RT Plan files to calculate Complexity Scores',
    author='Dan Cutright',
    author_email='dan.cutright@gmail.com',
    url='https://github.com/cutright/DVHA-MLCA',
    download_url='https://github.com/cutright/DVHA-MLCA/archive/master.zip',
    license="MIT License",
    keywords=['radiation therapy', 'research', 'dicom', 'dicom-rt', 'analytics'],
    classifiers=CLASSIFIERS,
    install_requires=requires,
    entry_points={'console_scripts': ['mlca = mlca.main:main']},
    long_description=long_description,
    long_description_content_type="text/x-rst"
)
