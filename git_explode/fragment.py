#!/usr/bin/env python
# -*- coding: utf-8 -*-


class Fragment(object):
    """Tracks fragments of the git explosion, i.e. commits which
    were exploded off the source branch into smaller topic branches.

    """
    i = 0
    fragments = {}

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
