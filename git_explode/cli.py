#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This is a skeleton file that can serve as a starting point for a Python
console script. To run this script uncomment the following line in the
entry_points section in setup.cfg:

    console_scripts =
     fibonacci = git_explode.skeleton:run

Then run `python setup.py install` which will install the command `fibonacci`
inside your current environment.
Besides console scripts, the header (i.e. until _logger...) of this file can
also be used as template for Python modules.

Note: This skeleton file can be safely removed if not needed!
"""

from __future__ import print_function, absolute_import

import argparse
import copy
import sys
import logging

from ostruct import OpenStruct

from git_deps.detector import DependencyDetector
from git_deps.gitutils import GitUtils
from git_deps.utils import abort, standard_logger
from git_explode import __version__
from git_explode.gitutils import GitUtils as GitExplodeUtils
from git_explode.listener import ExplodeDependencyListener
from git_explode.topics import TopicManager

__author__ = "Adam Spiers"
__copyright__ = "Adam Spiers"
__license__ = "GPL-2+"


def get_dependencies(repo, args):
    """
    Detect commit dependency tree, and return a tuple of dicts mapping
    this in both directions.  Note that the dependency tree goes in
    the reverse direction to the git commit graph, in that the leaves
    of the dependency tree are the oldest commits, because newer
    commits depend on older commits

    :param args: results from parse_args
    :return: (dependencies_from, dependencies_on)
    """

    detector_args = OpenStruct({
        'recurse': True,
        'exclude_commits': [args.base],
        'debug': args.debug,
        'context_lines': args.context_lines,
    })
    detector = DependencyDetector(detector_args, repo)
    listener = ExplodeDependencyListener(args)
    detector.add_listener(listener)

    revs = GitUtils.rev_list("%s..%s" % (args.base, args.head))
    for rev in revs:
        try:
            detector.find_dependencies(rev)
        except KeyboardInterrupt:
            pass

    return (detector.commits,
            listener.dependencies_from(),
            listener.dependencies_on())


def explode(logger, base, commits, deps_from, deps_on):
    """
    Walk the dependency tree breadth-first starting with the
    leaves at the bottom.

    For each commit, figure out whether it should be exploded

    :param base: sha on which to base all exploded topics
    :param deps_from: dict mapping dependents to dependencies
    :param deps_on: dict mapping in opposite direction
    """
    todo = get_leaves(commits, deps_from)

    # Each time we explode a commit, we'll remove it from any
    # dict which is a value of this dict.
    unexploded_deps_from = copy.deepcopy(deps_from)

    logger.debug("queue:")
    for commit in todo:
        logger.debug('  ' + GitUtils.commit_summary(commit))

    current = None
    topic_mgr = TopicManager('topic%d')

    while todo:
        commit = todo.pop(0)
        sha = commit.hex
        if unexploded_deps_from[sha]:
            abort("BUG: unexploded deps from %s" %
                  GitUtils.commit_summary(commit))

        deps = deps_from[sha]

        if not deps:
            base_desc = GitUtils.commit_summary(base)
            branch = topic_mgr.register(sha)
            print("checkout %s on base %s" % (branch, base_desc))
            current = branch
        else:
            deps = deps.keys()
            logger.debug("deps: %r" % deps)
            existing_branch = topic_mgr.lookup(*deps)
            if len(deps) == 1:
                assert existing_branch is not None
                branch = existing_branch
                topic_mgr.assign(branch, sha)
                if current != branch:
                    print("checkout %s" % branch)
                    current = branch
            else:
                if existing_branch is None:
                    branch = topic_mgr.register(*deps)
                    base_desc = GitUtils.commit_summary(commits[deps[0]])
                    print("checkout %s on %s" % (branch, base_desc))
                    current = branch
                    to_merge = deps[1:]
                    print("merge %s" % ' '.join(to_merge))
                else:
                    # Can reuse existing merge commit, but
                    # create a new branch at the same point
                    branch = topic_mgr.register(*deps)
                    print("checkout -b %s %s" % (branch, existing_branch))

        print("cherrypick %s" % GitUtils.commit_summary(commit))

        for dependent in deps_on[commit.hex]:
            del unexploded_deps_from[dependent][commit.hex]
            if not unexploded_deps_from[dependent]:
                new = commits[dependent]
                logger.debug("pushed to queue: %s" %
                             GitUtils.commit_summary(new))
                todo.insert(0, new)


def get_leaves(commits, deps_from):
    """
    Return all the leaves of the dependency tree, i.e. commits with
    no child dependencies
    """
    leaves = []
    for sha, dependencies in deps_from.iteritems():
        if len(dependencies) == 0:
            leaves.append(commits[sha])
    return leaves


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
        '-v', '--verbose',
        dest="loglevel",
        help="set loglevel to INFO",
        action='store_const',
        const=logging.INFO)
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
        metavar="BASE")
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
        type=str)

    return parser.parse_args(args)


def main(args):
    args = parse_args(args)
    logger = standard_logger('git-explode', args.debug)

    repo = GitUtils.get_repo()
    commits, deps_from, deps_on = get_dependencies(repo, args)
    base = GitUtils.ref_commit(repo, args.base)
    logger.debug("base commit %s is %s" %
                 (args.base, GitUtils.commit_summary(base)))
    orig_head = GitExplodeUtils.get_head()
    explode(logger, base, commits, deps_from, deps_on)
    print("checkout %s" % orig_head)


def run():
    main(sys.argv[1:])


if __name__ == "__main__":
    run()
