"""
Tests for the 'argparse-manpage' script.
"""

import datetime
import os
import shutil
import sys
import subprocess
import tempfile
import time

SIMPLE_FILE_CONTENTS = """
import argparse

def get_parser():
        parser = argparse.ArgumentParser({ap_arguments})
        parser.add_argument("test")
        return parser

if __name__ == "__main__":
        print("here")
        get_parser().parse_args()
"""

SIMPLE_OUTPUT = """\
.TH {NAME} "1" "{DATE}" "{name}" "Generated Python Manual"
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

.SH AUTHORS
.nf
John Doe <jdoe@example.com>
.fi
.nf
Mr. Foo <mfoo@example.com> and friends
.fi
"""

DATE = datetime.datetime.utcfromtimestamp(
           int(os.environ.get('SOURCE_DATE_EPOCH', time.time()))
       ).strftime("%Y\\-%m\\-%d")

class TestsArgparseManpageScript:
    def setup_method(self, _):
        self.workdir = tempfile.mkdtemp(prefix="argparse-manpage-tests-")
        os.environ["PYTHON"] = sys.executable

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
        assert output == SIMPLE_OUTPUT.format(name=expname,
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
        assert output == SIMPLE_OUTPUT.format(name=expname,
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
        ]
        output = subprocess.check_output(cmd).decode("utf-8")
        name="progname"
        assert output == FULL_OUTPUT.format(name=name, NAME=name.upper(),
                                            DATE=DATE)
