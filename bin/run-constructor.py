#!/usr/bin/env python3

import sys
import os
import argparse
import importlib
from contextlib import contextmanager
from tempfile import mkdtemp
from shutil import rmtree
from pprint import pprint
import json

api_dir = os.path.realpath(os.path.join(os.path.dirname(__file__), '..', 'api'))
sys.path.append(api_dir)

from smartz.api.constructor_engine import ConstructorInstance


def die(message, *args):
    print(message.format(*args), file=sys.stderr)
    sys.exit(1)


@contextmanager
def instantiate(filename):
    temp_dir = mkdtemp(prefix='run_constructor')
    os.link(filename, os.path.join(temp_dir, 'constructor.py'))

    sys.path.append(temp_dir)
    try:
        module = importlib.import_module('constructor')
    except ImportError as exc:
        die('Failed to import file {} as a module: {}', filename, exc)

    if not hasattr(module, 'Constructor') or not isinstance(module.Constructor, type):
        die('Constructor class in not found in the file {}', filename)

    constructor_object = module.Constructor()
    if not isinstance(constructor_object, ConstructorInstance):
        die('Constructor is not an instance of the type ConstructorInstance')

    yield constructor_object

    rmtree(temp_dir)


def get_params(args):
    filename = args.filename[0]
    with instantiate(filename) as constructor_object:
        pprint(constructor_object.get_params(), width=120)


def construct(args):
    filename = args.filename[0]
    if getattr(args, 'fields_file'):
        with open(args.fields_file) as fh:
            fields = json.load(fh)
    else:
        fields = json.loads(args.fields_json)

    with instantiate(filename) as constructor_object:
        result = constructor_object.construct(fields)
        if result['result'] == 'error':
            pprint(result, width=120)
        else:
            print(result['source'])


def main():
    parser = argparse.ArgumentParser(description='Runs constructor as if it\'s being run by smartz platform.')

    subparsers = parser.add_subparsers()

    parser_get_params = subparsers.add_parser('get_params')
    parser_get_params.set_defaults(func=get_params)
    parser_get_params.add_argument('filename', type=str, nargs=1,
                        help='constructor file name')

    parser_construct = subparsers.add_parser('construct')
    parser_construct.set_defaults(func=construct)
    parser_construct.add_argument('filename', type=str, nargs=1,
                        help='constructor file name')
    group = parser_construct.add_mutually_exclusive_group(required=True)
    group.add_argument('--fields-json', type=str,
                        help='Json-encoded fields provided to construct() by user')
    group.add_argument('--fields-file', type=str,
                        help='Json file which provides fields to construct() by user')

    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
