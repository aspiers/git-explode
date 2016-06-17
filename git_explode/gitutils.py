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
    def get_head(cls):
        """
        """
        try:
            return subprocess.check_output(['git', 'symbolic-ref',
                                            '--short', '-q', 'HEAD']).rstrip()
        except subprocess.CalledProcessError:
            return subprocess.check_output(['git', 'rev-parse',
                                            'HEAD']).rstrip()
