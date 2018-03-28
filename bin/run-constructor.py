#!/usr/bin/env python3

import sys
import argparse
from contextlib import contextmanager
from tempfile import mkdtemp
from shutil import rmtree


@contextmanager
def instantiate(filename):
    temp_dir = mkdtemp(prefix='run_constructor')
    yield ...
    rmtree(temp_dir)


def get_params(filename):
    pass


def main():
    parser = argparse.ArgumentParser(description='Runs constructor as if it\'s being run by smartz platform.')

    parser.add_argument('filename', type=str, nargs=1,
                        help='constructor file name')
    parser.add_argument('method', type=str, choices=('get_params', 'construct', 'post_construct'),
                        help='method of the constructor to run')

    args = parser.parse_args()

    filename = args.filename[0]
    method = args.method

    if 'get_params' == method:
        get_params(filename)
    elif 'construct' == method:
        pass
    elif 'post_construct' == method:
        print('Sorry, emulating post_construct is not implemented yet.', file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
