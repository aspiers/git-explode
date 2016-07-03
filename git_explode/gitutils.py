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

import subprocess


class GitUtils(object):
    @classmethod
    def git(cls, *args):
        cmd_words = ['git'] + list(args)
        print(' '.join(cmd_words))
        return cls.quiet_git(*args)

    @classmethod
    def quiet_git(cls, *args):
        cmd_words = ['git'] + list(args)
        output = subprocess.check_output(cmd_words)
        return output.rstrip()

    @classmethod
    def get_head(cls):
        """Retrieve the branch or reference to the current HEAD.
        """
        try:
            return cls.quiet_git('symbolic-ref', '--short', '-q', 'HEAD')
        except subprocess.CalledProcessError:
            return cls.quiet_git('rev-parse', 'HEAD')

    @classmethod
    def checkout(cls, branch):
        cls.git('checkout', '-q', branch)

    @classmethod
    def checkout_new(cls, branch, at):
        cls.git('checkout', '-q', '-b', branch, at)
