import os
import sys
from setuptools import setup, find_packages

sys.path = [os.getcwd()] + sys.path

from setuptools.command.build_py import build_py
from setuptools.command.install import install
from build_manpages.build_manpages \
    import build_manpages, get_build_py_cmd, get_install_cmd

setup(
    name='argparse-manpage',
    version='0.9.dev0',
    url='https://github.com/praiskup/argparse-manpage',
    license='Apache 2.0',
    py_modules = ['build_manpage'],
    author='Gabriele Giammatteo',
    author_email='gabriele.giammatteo@eng.it',
    maintainer='Pavel Raiskup',
    maintainer_email='<praiskup@redhat.com>',
    packages=find_packages(),
    scripts=['bin/argparse-manpage'],
    description='Build manual page from python\'s ArgumentParser object.',
    cmdclass={
        'build_manpages': build_manpages,
        'build_py': get_build_py_cmd(build_py),
        'install': get_install_cmd(install),
    },
)
