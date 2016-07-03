#!/usr/bin/env python
# -*- coding: utf-8 -*-

import copy
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

    def run(self):
        orig_head = GitExplodeUtils.get_head()
        commits, deps_from, deps_on = self.get_dependencies()
        self.explode(commits, deps_from, deps_on)
        print("checkout %s" % orig_head)

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

        self.logger.debug("queue:")
        for commit in todo:
            self.logger.debug('  ' + GitUtils.commit_summary(commit))

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
                base_desc = GitUtils.commit_summary(self.base_commit)
                branch = topic_mgr.register(sha)
                print("checkout %s on base %s" % (branch, base_desc))
                current = branch
            else:
                deps = deps.keys()
                self.logger.debug("deps: %r" % deps)
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

            self.queue_new_leaves(todo, commit, commits, deps_on,
                                  unexploded_deps_from)

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
                self.logger.debug("pushed to queue: %s" %
                                  GitUtils.commit_summary(new))
                todo.insert(0, new)

    def get_leaves(self, commits, deps_from):
        """
        Return all the leaves of the dependency tree, i.e. commits with
        no child dependencies
        """
        leaves = []
        for sha, dependencies in deps_from.iteritems():
            if len(dependencies) == 0:
                leaves.append(commits[sha])
        return leaves
