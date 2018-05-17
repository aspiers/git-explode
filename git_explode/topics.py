#!/usr/bin/env python
# -*- coding: utf-8 -*-


class TopicManager(object):
    """Acts as a factory for topic branch names, and a registry for
    mapping both individual commits and merges of commits to topic
    branch names.

    This ensures we always know onto which topic branch to explode
    (cherry-pick) a new commit.

    """
    i = 0
    topics = {}
    commits = {}

    def __init__(self, template, logger):
        self.template = template
        self.logger = logger

    def lookup(self, *commits):
        name = self._name_for(*commits)
        return self.topics.get(name)

    def register(self, *commits):
        new = self.next()
        self.assign(new, *commits)
        return new

    def _assign(self, topic, *commits):
        name = self._name_for(*commits)
        self.topics[name] = topic
        self.commits[topic] = name
        self.logger.debug("  Assigned %s to %s" % (topic, name))

    def assign(self, topic, *commits):
        old_commits = self.commits.get(topic)
        if old_commits:
            self.unassign(topic, old_commits)
        self._assign(topic, *commits)

    def unassign(self, topic, commits):
        del self.topics[commits]
        del self.commits[topic]
        self.logger.debug("  Unassigned %s from %s" % (topic, commits))

    def _name_for(self, *commits):
        return ' '.join(sorted(commits))

    def next(self):
        self.i += 1
        return self.template % self.i
