"""
unit-tests helpers
"""

import os
from platform import python_version
from packaging import version
from contextlib import contextmanager

import pytest

def skip_on_python_older_than(minimal_version, message, condition=None):
    """
    Raise the "skip" exception if python doesn't match the minimal required
    version for the calling test case
    """

    if condition is not None and not condition:
        return

    if version.parse(python_version()) < version.parse(minimal_version):
        generic_msg = "Python {0} required, have {1}".format(
            minimal_version,
            python_version(),
        )
        raise pytest.skip("{0} ({1})".format(message, generic_msg))

@contextmanager
def pushd(path):
    old_dir = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(old_dir)
