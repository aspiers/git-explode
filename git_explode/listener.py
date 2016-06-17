from git_deps.listener.base import DependencyListener


class ExplodeDependencyListener(DependencyListener):
    """Dependency listener for use when building a dependency tree to be
    used for exploding the commits into multiple topic branches.
    """

    def __init__(self, options):
        super(ExplodeDependencyListener, self).__init__(options)

        # Map each commit to a dict whose keys are the dependencies of
        # that commit which haven't yet been exploded into a topic
        # branch.
        self._dependencies_from = {}
        self._dependencies_on = {}

    def new_commit(self, commit):
        """Adds the commit if it doesn't already exist.
        """
        sha1 = commit.hex
        for d in (self._dependencies_from, self._dependencies_on):
            if sha1 not in d:
                d[sha1] = {}

    def new_dependency(self, dependee, dependency, path, line_num):
        src = dependee.hex
        dst = dependency.hex

        cause = "%s:%d" % (path, line_num)
        self._dependencies_from[src][dst] = cause
        self._dependencies_on[dst][src] = cause

    def dependencies_from(self):
        return self._dependencies_from

    def dependencies_on(self):
        return self._dependencies_on
