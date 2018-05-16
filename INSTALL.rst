Installation
============

``git-explode`` requires `git-deps
<https://github.com/aspiers/git-deps/>`_, which requires `pygit2
<http://www.pygit2.org/>`_, which in return requires `libgit2
<https://libgit2.github.com/>`_.  These dependencies can potentially
make installation slightly tricky in some cases, but if you manage to
get ``git-deps`` installed and working, then it is very likely that
``git-explode`` will install on top with no extra problems.

Therefore the recommended installation procedure is to first follow
`the instructions for installing git-deps
<https://github.com/aspiers/git-deps/blob/master/INSTALL.md>`_, and
then install ``git-explode`` on top via the same technique you used to
install ``git-deps``, which is typically a standard Python module
installation technique.  So for example if you installed ``git-deps``
system-wide on Linux via::

    sudo pip install git-deps

then you should repeat that technique for ``git-explode``::

    sudo pip install git-explode

Similarly if you installed ``git-deps`` just for the current user via::

    pip install --user git-deps

then repeat that for ``git-explode``::

    pip install --user git-explode

If you encounter problems, please `report them <CONTRIBUTING.rst>`_!
