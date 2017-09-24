import os, sys
import runpy
import filecmp
from contextlib import contextmanager

@contextmanager
def pushd(path):
    old_dir = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(old_dir)

@contextmanager
def change_argv(argv):
    old_argv = sys.argv
    sys.argv = argv
    try:
        yield
    finally:
        sys.argv = old_argv

@contextmanager
def on_syspath(dirpath):
    old_path = sys.path
    sys.path = [dirpath] + sys.path
    try:
        yield
    finally:
        sys.path = old_path


class TestAllExapmles(object):
    def test_old_example(self):
        with on_syspath(os.getcwd()):
            with pushd('examples/old_format'):
                with change_argv(['setup.py', 'build_manpage']):
                    try:
                        os.remove('example.1')
                    except OSError:
                        pass
                    runpy.run_path('setup.py')
                    assert (filecmp.cmp('example.1', 'expected-output.1'))
