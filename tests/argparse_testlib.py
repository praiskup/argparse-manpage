"""
unit-tests helpers
"""

from platform import python_version
from pkg_resources import parse_version

import pytest

def skip_on_python_older_than(minimal_version, message, condition=None):
    """
    Raise the "skip" exception if python doesn't match the minimal required
    version for the calling test case
    """

    if condition is not None and not condition:
        return

    if parse_version(python_version()) < parse_version(minimal_version):
        generic_msg = "Python {0} required, have {1}".format(
            minimal_version,
            python_version(),
        )
        raise pytest.skip("{0} ({1})".format(message, generic_msg))
