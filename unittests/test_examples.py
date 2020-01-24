import os, sys
import re
import subprocess
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


def run_setup_py(args):
    with change_argv(['setup.py'] + args):
        subprocess.call([sys.executable, 'setup.py'] + args,
                        env={'PYTHONPATH': ':'.join(sys.path)})


def file_cmp(file1, file2, filter_string=None):
    with open(file1, 'r') as f1:
        with open(file2, 'r') as f2:
            a1 = f1.readlines()
            a2 = f2.readlines()
            assert len(a1) == len(a2)
            first = True
            for left, right in zip(a1, a2):
                if first:
                    left  = re.sub('[0-9]{4}\\\\-[0-9]{2}\\\\-[0-9]{2}', '!!DATE!!', left)
                    right = re.sub('[0-9]{4}\\\\-[0-9]{2}\\\\-[0-9]{2}', '!!DATE!!', right)
                    first = False

                if filter_string is not None:
                    left = filter_string(left)
                    right = filter_string(right)

                assert left == right


class TestAllExapmles(object):
    def test_old_example(self):
        with pushd('examples/old_format'):
            try:
                os.remove('example.1')
            except OSError:
                pass
            run_setup_py(['build_manpage'])
            file_cmp('example.1', 'expected-output.1')


    def test_copr(self):
        with pushd('examples/copr'):
            name = 'copr-cli.1'
            prefix = '/usr'
            try:
                os.remove(name)
            except OSError:
                pass
            idir = os.path.join(os.getcwd(), 'i')
            run_setup_py(['install', '--root', idir, '--prefix', prefix])

            def version_version_filter(string):
                return string.replace('[VERSION [VERSION ...]]',
                                      '[VERSION ...]')

            file_cmp('i/usr/share/man/man1/' + name, 'expected-output.1',
                     filter_string=version_version_filter)
            file_cmp(name, 'expected-output.1',
                     filter_string=version_version_filter)


    def test_distgen(self):
        with pushd('examples/raw-description'):
            name = 'man/dg.1'
            try:
                os.remove(name)
            except OSError:
                pass
            idir = os.path.join(os.getcwd(), 'i')
            run_setup_py (['install', '--root', idir, '--prefix', '/usr'])
            file_cmp('i/usr/share/man/man1/' + os.path.basename(name), 'expected-output.1')
            file_cmp(name, 'expected-output.1')


    def test_resalloc(self):
        with pushd('examples/resalloc'):
            prefix = '/usr'
            for name in ['man/resalloc.1', 'man/resalloc-maint.1']:
                try:
                    os.remove(name)
                except OSError:
                    pass

            idir = os.path.join(os.getcwd(), 'i')
            run_setup_py(['install', '--root', idir, '--prefix', prefix])

            for name in ['man/resalloc.1', 'man/resalloc-maint.1']:
                file_cmp('i/usr/share/man/man1/' + os.path.basename(name),
                         'expected/' + name)
                file_cmp(name, 'expected/' + name)
