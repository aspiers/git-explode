#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
        output = subprocess.check_output(cmd_words, universal_newlines=True)
        return output.rstrip()

    @classmethod
    def get_head(cls):
        """Retrieve the branch or reference to the current HEAD.
        """
        try:
            return cls.quiet_git('symbolic-ref', '--short', '-q', 'HEAD')
        except subprocess.CalledProcessError:
            return cls.get_head_sha1()

    @classmethod
    def get_head_sha1(cls):
        return cls.quiet_git('rev-parse', 'HEAD')

    @classmethod
    def checkout(cls, branch):
        cls.git('checkout', '-q', branch)

    @classmethod
    def checkout_new(cls, branch, at):
        cls.git('checkout', '-q', '-b', branch, at)
