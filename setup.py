import os

from setuptools import setup, find_packages
from setuptools.command.build_py import build_py
from setuptools.command.install import install

from build_manpages import __version__
from build_manpages.build_manpages import build_manpages
from build_manpages.build_manpages import get_build_py_cmd
from build_manpages.build_manpages import get_install_cmd


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


def get_readme():
    with open(os.path.join(ROOT_DIR, 'README.rst')) as fh:
        return ''.join(fh.readlines())


setup(
    name='argparse-manpage',
    version=__version__,
    url='https://github.com/praiskup/argparse-manpage',
    license='Apache 2.0',
    py_modules=['build_manpage'],
    author='Gabriele Giammatteo',
    author_email='gabriele.giammatteo@eng.it',
    maintainer='Pavel Raiskup',
    maintainer_email='praiskup@redhat.com',
    packages=find_packages(),
    scripts=['bin/argparse-manpage'],
    data_files=[("", ["LICENSE", "NEWS"])],
    description="Build manual page from python's ArgumentParser object.",
    long_description=get_readme(),
    cmdclass={
        'build_manpages': build_manpages,
        'build_py': get_build_py_cmd(build_py),
        'install': get_install_cmd(install),
    },
)
