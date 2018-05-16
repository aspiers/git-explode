#!/usr/bin/env python
# -*- coding: utf-8 -*-

# import pytest

from git_explode.exploder import GitExploder
from git_deps.gitutils import GitUtils


def test_new():
    repo = GitUtils.get_repo()
    exploder = GitExploder(repo, "HEAD~5", "HEAD", False, 1)
    assert exploder is not None
