"""
Tests for the 'argparse-manpage' script.
"""

import os
import shutil
import sys
import subprocess
import tempfile
import warnings

from packaging import version

import setuptools

from test_examples import run_setup_py
from argparse_testlib import pushd
from argparse_manpage.compat import get_reproducible_date

SIMPLE_FILE_CONTENTS = """\
import argparse

def get_parser():
        parser = argparse.ArgumentParser({ap_arguments})
        parser.add_argument("test")
        return parser

def main():
        print("here")
        get_parser().parse_args()

if __name__ == "__main__":
        main()
"""

SIMPLE_OUTPUT = """\
.TH {NAME} "1" "{DATE}" "{name}{version}" "Generated Python Manual"
.SH NAME
{name}
.SH SYNOPSIS
.B {name}
[-h] test

.TP
\\fBtest\\fR
"""

FULL_OUTPUT = """\
.TH {NAME} "3" "{DATE}" "Proj\\-On\\-Cmdline 1.alpha" "Some\\-long Manual Name"
.SH NAME
{name} \\- some description
.SH SYNOPSIS
.B {name}
[-h] test

.TP
\\fBtest\\fR
.SH EXTRA SECTION
This is an extra section.

.SH AUTHOR
.nf
John Doe <jdoe@example.com>
Developer extraordinaire.
.fi
.nf
Mr. Foo <mfoo@example.com> and friends
.fi
"""

SETUP_PY_FILE_CONTENTS = """\
from build_manpages import build_manpages, get_install_cmd, get_build_py_cmd
from setuptools import setup

setup(
    cmdclass={
        'build_manpages': build_manpages,
        'build_py': get_build_py_cmd(),
        'install': get_install_cmd(),
    }
)
"""

PYPROJECT_TOML_FILE_CONTENTS = """\
[tool.build_manpages]
manpages = [
    "some-file.1:project_name=some-file:module=somefile:function=get_parser",
]
"""

DATE = get_reproducible_date().replace("-", "\\-")

class TestsArgparseManpageScript:
    def setup_method(self, _):
        self.workdir = tempfile.mkdtemp(prefix="argparse-manpage-tests-")
        os.environ["PYTHON"] = sys.executable
        os.environ["PYTHONPATH"] = os.getcwd()

    def teardown_method(self, _):
        shutil.rmtree(self.workdir)

    @staticmethod
    def _get_am_executable():
        testdir = os.path.dirname(__file__)
        executable = os.path.join(testdir, '..', 'argparse-manpage')
        return executable

    def test_filepath_function(self):
        """
        Test --pyfile && --function.
        """
        name = "some-file"
        expname = r"some\-file"
        tested_executable = os.path.join(self.workdir, name)
        with open(tested_executable, "w+") as script_fd:
            script_fd.write(SIMPLE_FILE_CONTENTS.format(ap_arguments=""))

        cmd = [
            self._get_am_executable(),
            "--pyfile", tested_executable,
            "--function", "get_parser",
        ]
        output = subprocess.check_output(cmd).decode("utf-8")
        assert output == SIMPLE_OUTPUT.format(name=expname, version="",
                                              NAME=expname.upper(), DATE=DATE)

    def test_filepath_prog(self):
        """
        Test --pyfile --function with prog explicitly specified in
        ArgumentParser name.
        """
        name = "some-file"
        expname = "progname"
        tested_executable = os.path.join(self.workdir, name)
        with open(tested_executable, "w+") as script_fd:
            script_fd.write(SIMPLE_FILE_CONTENTS.format(ap_arguments='"progname"'))

        cmd = [
            self._get_am_executable(),
            "--pyfile", tested_executable,
            "--function", "get_parser",
        ]
        output = subprocess.check_output(cmd).decode("utf-8")
        name="progname"
        assert output == SIMPLE_OUTPUT.format(name=expname, version="",
                                              NAME=expname.upper(), DATE=DATE)

    def test_full_args(self):
        """
        Submit as many commandline arguments as possible.
        """
        name = "full_name"
        tested_executable = os.path.join(self.workdir, name)
        with open(tested_executable, "w+") as script_fd:
            script_fd.write(SIMPLE_FILE_CONTENTS.format(ap_arguments='"progname"'))

        cmd = [
            self._get_am_executable(),
            "--pyfile", tested_executable,
            "--function", "get_parser",
            "--manual-section", "3",
            "--manual-title", "Some-long Manual Name",
            "--version", "1.alpha",
            "--author", "John Doe <jdoe@example.com>",
            "--author", "Mr. Foo <mfoo@example.com> and friends",
            "--project-name", "Proj-On-Cmdline",
            "--description", "some description",
            "--long-description", "Some long description.",  # unused
            "--include", "tests/extra.man",
        ]
        output = subprocess.check_output(cmd).decode("utf-8")
        name="progname"
        assert output == FULL_OUTPUT.format(name=name, NAME=name.upper(),
                                            DATE=DATE)

    def test_pyproject_toml(self):
        """
        Test that we can read information from pyproject.toml.
        """
        current_dir = os.getcwd()
        with pushd(self.workdir):
            with open("pyproject.toml", "w+") as script_fd:
                script_fd.write(PYPROJECT_TOML_FILE_CONTENTS.format(gitdir=current_dir))
            with open("setup.py", "w+") as script_fd:
                script_fd.write(SETUP_PY_FILE_CONTENTS)

            modname = "somefile"
            name = r"some\-file"
            os.mkdir(modname)
            with open(os.path.join(modname, "__init__.py"), "w+") as script_fd:
                script_fd.write(SIMPLE_FILE_CONTENTS.format(ap_arguments=""))

            assert 0 == run_setup_py(["build"])
            if version.parse(setuptools.__version__) >= version.parse("62.2.0"):
                with open("some-file.1") as script_fd:
                    output = script_fd.read()
                    assert output == SIMPLE_OUTPUT.format(name=name, version=" 0.0.0",
                                                          NAME=name.upper(), DATE=DATE)
            else:
                warnings.warn("setuptools >= 62.2.0 required to generate man pages with pyprojects.toml")
