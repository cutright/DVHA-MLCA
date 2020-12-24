#!/usr/bin/env python
# -*- coding: utf-8 -*-

# setup.py
"""
A setuptools setup file for DVH Analytics MLC Analyzer
"""
# Copyright (c) 2016-2020 Dan Cutright
# This file is part of DVH Analytics MLC Analyzer, released under a BSD license.
#    See the file LICENSE included with this distribution, also
#    available at https://github.com/cutright/DVHA-MLCA

from setuptools import setup, find_packages
from mlca._version import __version__


with open('requirements.txt', 'r') as doc:
    requires = [line.strip() for line in doc]

with open('README.rst', 'r') as doc:
    long_description = doc.read()


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
    keywords=['dvh', 'radiation therapy', 'research', 'dicom', 'dicom-rt', 'analytics'],
    classifiers=[],
    install_requires=requires,
    entry_points={'console_scripts': ['mlca = mlca.main:main']},
    long_description=long_description,
    long_description_content_type="text/markdown"
)
