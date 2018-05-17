#!/usr/bin/env python
# -*- coding: utf-8 -*-

import copy
import six
from ostruct import OpenStruct

from git_deps.detector import DependencyDetector
from git_deps.gitutils import GitUtils
from git_deps.utils import abort, standard_logger
from git_explode.gitutils import GitUtils as GitExplodeUtils
from git_explode.listener import ExplodeDependencyListener
from git_explode.topics import TopicManager


class GitExploder(object):
    """Explode a linear sequence of git commits into multiple independent
    topic branches.

    """
    def __init__(self, repo, base, head, debug, context_lines):
        self.logger = standard_logger('git-explode', debug)

        self.debug = debug
        self.repo = repo
        self.base = base
        self.base_commit = GitUtils.ref_commit(repo, base)
        self.logger.debug("base commit %s is %s" %
                          (base, GitUtils.commit_summary(self.base_commit)))
        self.head = head
        self.context_lines = context_lines
        self.topic_mgr = TopicManager('topic%d', self.logger)

        # Map commits to their exploded version
        self.exploded = {}

    def run(self):
        orig_head = GitExplodeUtils.get_head()
        commits, deps_from, deps_on = self.get_dependencies()
        self.explode(commits, deps_from, deps_on)
        self.checkout(orig_head)

    def get_dependencies(self):
        """
        Detect commit dependency tree, and return a tuple of dicts mapping
        this in both directions.  Note that the dependency tree goes in
        the reverse direction to the git commit graph, in that the leaves
        of the dependency tree are the oldest commits, because newer
        commits depend on older commits

        :return: (dependencies_from, dependencies_on)
        """

        detector_args = OpenStruct({
            'recurse': True,
            'exclude_commits': [self.base],
            'debug': self.debug,
            'context_lines': self.context_lines,
        })
        detector = DependencyDetector(detector_args, self.repo)
        listener = ExplodeDependencyListener({})
        detector.add_listener(listener)

        revs = GitUtils.rev_list("%s..%s" % (self.base, self.head))
        for rev in revs:
            try:
                detector.find_dependencies(rev)
            except KeyboardInterrupt:
                pass

        return (detector.commits,
                listener.dependencies_from(),
                listener.dependencies_on())

    def explode(self, commits, deps_from, deps_on):
        """
        Walk the dependency tree breadth-first starting with the
        leaves at the bottom.

        For each commit, figure out whether it should be exploded

        :param commits: dict mapping SHA1 hashes to pygit2.Commit objects
        :param deps_from: dict mapping dependents to dependencies
        :param deps_on: dict mapping in opposite direction
        """
        todo = self.get_leaves(commits, deps_from)

        # Each time we explode a commit, we'll remove it from any
        # dict which is a value of this dict.
        unexploded_deps_from = copy.deepcopy(deps_from)

        self.logger.debug("Initial queue of leaves:")
        for commit in todo:
            self.logger.debug('  ' + GitUtils.commit_summary(commit))

        self.current_branch = None

        while todo:
            commit = todo.pop(0)
            sha = commit.hex
            self.logger.debug("Exploding %s" % GitUtils.commit_summary(commit))
            if unexploded_deps_from[sha]:
                abort("BUG: unexploded deps from %s" %
                      GitUtils.commit_summary(commit))

            deps = deps_from[sha]
            self.prepare_cherrypick_base(sha, deps, commits)
            self.cherry_pick(sha)

            self.queue_new_leaves(todo, commit, commits, deps_on,
                                  unexploded_deps_from)

    def prepare_cherrypick_base(self, sha, deps, commits):
        if not deps:
            branch = self.topic_mgr.next()
            # We don't assign the topic here, because it will get
            # assigned by cherry_pick(), and it needs to be done there
            # to also catch the case where we are cherry-picking to
            # update an existing branch.
            self.checkout_new(branch, self.base)
            return

        deps = deps.keys()
        assert len(deps) >= 1
        self.logger.debug("  deps: %s" % ' '.join([d[:8] for d in deps]))

        existing_branch = self.topic_mgr.lookup(*deps)
        if len(deps) == 1:
            if existing_branch is None:
                self.checkout_new_dependent_topic(deps)
            else:
                branch = existing_branch
                self.checkout(branch)
        elif len(deps) > 1:
            # We'll need to base the cherry-pick on a merge commit
            if existing_branch is None:
                self.checkout_new_dependent_topic(deps)
                to_merge = (self.exploded[dep] for dep in deps[1:])
                GitExplodeUtils.git('merge', *to_merge)
            else:
                # Can reuse existing merge commit, but
                # create a new branch at the same point
                self.checkout_new(branch, existing_branch)

    def queue_new_leaves(self, todo, exploded_commit, commits, deps_on,
                         unexploded_deps_from):
        """When a commit is exploded, there may be other commits in the
        dependency tree which only had a single dependency on this
        commit.  In that case they have effectively become leaves on
        the dependency tree of unexploded commits, so they should be
        added to the explode queue.

        """
        sha1 = exploded_commit.hex
        for dependent in deps_on[sha1]:
            del unexploded_deps_from[dependent][sha1]
            if not unexploded_deps_from[dependent]:
                new = commits[dependent]
                self.logger.debug("+ pushed to queue: %s" %
                                  GitUtils.commit_summary(new))
                todo.insert(0, new)

    def get_leaves(self, commits, deps_from):
        """
        Return all the leaves of the dependency tree, i.e. commits with
        no child dependencies
        """
        leaves = []
        for sha, dependencies in six.iteritems(deps_from):
            if len(dependencies) == 0:
                leaves.append(commits[sha])
        return leaves

    def checkout(self, branch):
        if self.current_branch == branch:
            return
        # self.logger.debug("checkout %s" % branch)
        GitExplodeUtils.checkout(branch)
        self.current_branch = branch

    def checkout_new(self, branch, at):
        assert self.current_branch != branch
        # self.logger.debug("checkout -b %s %s" % (branch, at))
        GitExplodeUtils.checkout_new(branch, at)
        self.current_branch = branch

    def checkout_new_dependent_topic(self, deps):
        branch = self.topic_mgr.register(*deps)
        base = self.exploded[deps[0]]
        self.checkout_new(branch, base)

    def cherry_pick(self, sha):
        GitExplodeUtils.git('cherry-pick', sha)
        self.update_current_topic(sha)
        head = GitExplodeUtils.get_head_sha1()
        self.exploded[sha] = head
        commit = GitUtils.ref_commit(self.repo, sha)
        self.logger.debug("- cherry-picked %s as %s (%s)" %
                          (sha[:8], self.exploded[sha][:8],
                           GitUtils.oneline(commit)))

    def update_current_topic(self, *commits):
        self.topic_mgr.assign(self.current_branch, *commits)
