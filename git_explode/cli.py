#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import

import argparse
import sys

from git_deps.gitutils import GitUtils
from git_explode import __version__
from git_explode.exploder import GitExploder


def parse_args(args):
    """
    Parse command line parameters

    :param args: command line parameters as list of strings
    :return: command line parameters as :obj:`argparse.Namespace`
    """
    parser = argparse.ArgumentParser(
        description="Explode linear sequence of commits into topic branches")
    parser.add_argument(
        '--version',
        action='version',
        version='git-explode {ver}'.format(ver=__version__))
    parser.add_argument(
        '-d', '--debug',
        dest='debug',
        action='store_true',
        help='Show debugging')
    parser.add_argument(
        '-p', '--prefix',
        dest="prefix",
        help="prefix for all created topic branches",
        type=str,
        metavar="PREFIX")
    parser.add_argument(
        '-c', '--context-lines',
        dest='context_lines',
        help='Number of lines of diff context to use [%(default)s]',
        type=int,
        metavar='NUM',
        default=1)
    parser.add_argument(
        dest="base",
        help="base of sequence to explode",
        type=str,
        metavar="BASE")
    parser.add_argument(
        dest="head",
        help="head of sequence to explode",
        type=str,
        metavar="HEAD")

    return parser.parse_args(args)


def main(args):
    args = parse_args(args)
    repo = GitUtils.get_repo()
    exploder = GitExploder(repo, args.base, args.head, args.debug,
                           args.context_lines)
    exploder.run()


def run():
    main(sys.argv[1:])


if __name__ == "__main__":
    run()
