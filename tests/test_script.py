"""
Tests for the 'argparse-manpage' script.
"""

import os
import shutil
import sys
import subprocess
import tempfile

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
.TH {name} "1" Manual
.SH NAME
{name}
.SH SYNOPSIS
.B {name}
[-h] test
.TP
\\fBtest\\fR

.SH AUTHORS
.B <<UNSET \\-\\-project\\-name OPTION>>
was written by <<UNSET \\-\\-author OPTION>> <<<UNSET \\-\\-author_email OPTION>>>.
.SH DISTRIBUTION
The latest version of <<UNSET \\-\\-project\\-name OPTION>> may be downloaded from
.UR <<UNSET \\-\\-url OPTION>>
.UE
"""


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
        tested_executable = os.path.join(self.workdir, name)
        with open(tested_executable, "w+") as script_fd:
            script_fd.write(SIMPLE_FILE_CONTENTS.format(ap_arguments=""))

        cmd = [
            self._get_am_executable(),
            "--pyfile", tested_executable,
            "--function", "get_parser",
        ]
        output = subprocess.check_output(cmd).decode("utf-8")
        assert output == SIMPLE_OUTPUT.format(name=name)

    def test_filepath_prog(self):
        """
        Test --pyfile --function with prog explicitly specified in
        ArgumentParser name.
        """
        name = "some-file"
        tested_executable = os.path.join(self.workdir, name)
        with open(tested_executable, "w+") as script_fd:
            script_fd.write(SIMPLE_FILE_CONTENTS.format(ap_arguments='"progname"'))

        cmd = [
            self._get_am_executable(),
            "--pyfile", tested_executable,
            "--function", "get_parser",
        ]
        output = subprocess.check_output(cmd).decode("utf-8")
        assert output == SIMPLE_OUTPUT.format(name="progname")
