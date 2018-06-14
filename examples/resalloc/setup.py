# Resalloc setup script.
# Copyright (C) 2017 Red Hat, Inc.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

import os, sys
from setuptools import setup, find_packages
from resalloc.version import resalloc_version
from os import listdir, path

# For the manual pages generator.
from setuptools.command.build_py import build_py
from setuptools.command.install import install
try:
    sys.path = [os.path.join(os.getcwd(), 'build_manpages')] + sys.path
    from build_manpages.build_manpages \
    import build_manpages, get_build_py_cmd, get_install_cmd
except:
    print("=======================================")
    print("Use 'git submodule update --init' first")
    print("=======================================")
    raise

project = "resalloc"
datadir = "share"
pkgdatadir = datadir + "/" + project

def get_requirements():
    with open('requirements.txt') as f:
        return f.read().splitlines()

long_description="""
Resource allocator
""".strip()

setup(
    name=project,
    version=resalloc_version,
    description='Client/server application for maintaining (expensive) resources',
    long_description=long_description,
    author='Pavel Raiskup',
    author_email='praiskup@redhat.com',
    license='GPLv2+',
    url='https://github.com/praiskup/resalloc',
    platforms=['any'],
    packages=find_packages(),
    scripts=['bin/resalloc', 'bin/resalloc-maint'],
    install_requires=get_requirements(),
    cmdclass={
        'build_manpages': build_manpages,
        'build_py': get_build_py_cmd(build_py),
        'install': get_install_cmd(install),
    },
)
