#!/usr/bin/env python
# -*- coding: utf-8 -*-


class TopicManager(object):
    """Acts as a factory for topic branch names, and a registry for
    mapping both individual commits and merges of commits to topic
    branch names.

    This ensure we always know onto which topic branch to explode
    (cherry-pick) a new commit.

    """
    i = 0
    topics = {}

    def __init__(self, template):
        self.template = template

    def lookup(self, *commits):
        name = self._name_for(*commits)
        return self.topics.get(name)

    def register(self, *commits):
        new = self._next()
        self.assign(new, *commits)
        return new

    def assign(self, topic, *commits):
        name = self._name_for(*commits)
        self.topics[name] = topic

    def _name_for(self, *commits):
        return ' '.join(sorted(commits))

    def _next(self):
        self.i += 1
        return self.template % self.i
