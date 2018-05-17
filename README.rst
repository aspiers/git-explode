===========
git-explode
===========

``git-explode`` is a tool for automatically exploding a single git
branch into a number of smaller branches which are textually
independent.  It uses `git-deps
<https://github.com/aspiers/git-deps>`_ to automatically detect
textual dependencies between the commits in the branch, and calculates
the grouping and ordering of commits into independent sub-topics from
which the new branches are created.


Use case #1
===========

The most obvious use case for this tool is helping improve the
"hygiene" of branch management, so that each branch in your repository
is tightly and cleanly scoped to a single logical topic.

For example during work on feature branch, you might become aware of
an opportunity to refactor some existing code, and might decide to
take advantage of that opportunity immediately, by adding refactoring
commits to the tip of the feature branch.  And during the refactoring,
you may even spot a bug, and end up also adding a bugfix to the same
feature branch.

So now you have a feature branch which is polluted by commits which
perform refactoring and bugfixing.  If you were to submit this branch
for code review as a single `GitHub pull request
<https://help.github.com/articles/about-pull-requests/>`_ (or `GitLab
merge request
<https://docs.gitlab.com/ee/user/project/merge_requests/>`_, or
`Gerrit change topic
<https://gerrit-review.googlesource.com/Documentation/intro-user.html#topics>`_),
it would be a lot harder for your collaborators to review than if you
had separately submitted three smaller reviews, one for the bugfix,
one for the refactoring, and one for the new feature.

In this scenario, ``git-explode`` comes to the rescue!  Rather than you
having to manually separate out the commits into topic branches, it
can do all the hard work for you with a single command.


Textual vs. semantic (in)dependence
===================================

Astute readers will note that textual independence (as detected by
``git-deps`` and used by ``git-explode``) is not the same as semantic /
logical independence.  Textual independence means that the changes can
be applied in any order without incurring conflicts, but this is not a
reliable indicator of logical independence.  (This caveat is also
noted in `the README for git-deps
<https://github.com/aspiers/git-deps/blob/master/README.md#caveat>`_.)

For example a change to a function and corresponding changes to the
tests and/or documentation for that function would typically exist in
different files.  So if those changes were in separate commits within
a branch, running ``git-explode`` on the branch would place those
commits in separate branches even though they are logically related,
because changes in different files (or even in different areas of the
same files) are textually independent.

So in this case, ``git-explode`` would not behave exactly how we might
want.  And for as long as AI is an unsolved problem, it is very
unlikely that it will ever develop totally reliable behaviour.
So does that mean ``git-explode`` is useless?  Absolutely not!

Firstly, when `best practices for commit hygiene
<https://wiki.openstack.org/wiki/GitCommitMessages>`_ are adhered to,
changes which are strongly logically related should be within the same
commit anyway.  So in the example above, a change to a function and
corresponding changes to the tests and/or documentation for that
function should all be within a single commit.

Secondly, whilst textual independence does not imply logical
independence, the converse is much more commonly true: logical
independence typically implies textual independence.  So while it
might not be too uncommon for ``git-explode`` to separate
logically-related changes into different branches, it should be pretty
rare that it groups logically *unrelated* changes on the same branch.
Combining this with the fact that ``git`` makes it easier to merge
branches together than to split them apart suggests that ``git-explode``
still has plenty of potential for saving effort.

Thirdly, it is often unhelpful to allow `the quest for the perfect
become the enemy of the good
<https://en.wikipedia.org/wiki/Perfect_is_the_enemy_of_good>`_ - a
tool does not have to be perfect to be useful; it only has to be
better than performing the same task without the tool.

Further discussion on these points can be found in `an old thread from
the git mailing list
<https://public-inbox.org/git/20160528112417.GD11256@pacific.linksys.moosehall/>`_.

Ultimately though, `"the proof is in the pudding"
<https://en.wiktionary.org/wiki/the_proof_is_in_the_pudding>`_, so try
it out and see!


Other use cases
===============

As already explained above, the most obvious use case is cleaning up
the mess caused by logically independent commits all mashed together
into one branch.  However here are some further use cases.  If you
can think of others, please `submit them <CONTRIBUTING.rst>`_!


Use case #2: Decompose changes for porting
------------------------------------------

If you need to backport or forward-port changes between two branches,
``git-explode`` could be used to first decompose the source branch into
textually independent topic branches.  Then before any porting starts,
informed decisions can be made about which topics to port and which
not to port, and in which order.  Each decomposed topic branch is
guaranteed to be textually independent from the others, so they can be
ported separately - indeed even concurrently by different people -
thereby greatly reducing the risk of conflicts when the independent
topic branches are merged together into the target branch.


Use case #3: Publishing a previously private codebase
-----------------------------------------------------

Emmet's idea about a company who needs to publish a private
codebase but needs to clean it up first.  Similar to 1. but on a
bigger scale.


Use case #4: Breaking down giant commits
----------------------------------------

Split giant commit into commits one per hunk, then regroup into
commits based on that.


Installation
============

Please see `the INSTALL.rst file <INSTALL.rst>`_.


Usage
=====

The tool is not yet documented, but usage is fairly self-explanatory
if you run ``git explode -h``.


Development / support / feedback
================================

Please see `the CONTRIBUTING.rst file <CONTRIBUTING.rst>`_.


History
=======

I first announced the intention to build this tool `on the git mailing
list in May 2016
<https://public-inbox.org/git/20160527140811.GB11256@pacific.linksys.moosehall/>`_;
however at the time I was under the mistaken impression that I could
build it out of `the git-splice and git-transplant commands
<https://github.com/git/git/compare/master...aspiers:transplant>`_
which I was working on at that time.

Thanks to SUSE's generous `Hack Week <https://hackweek.suse.com/>`_
policy, I have had the luxury of working on this as a `Hack Week project
<https://hackweek.suse.com/projects/implement-git-explode-to-untangle-linear-sequence-of-commits-into-multiple-independent-topic-branches>`_.

In May 2018 I took advantage of another Hack Week to apply more polish
and make the first release.  This was in preparation for demonstrating
the software at `a Meetup event
<https://www.meetup.com/londongit/events/248694943/>`_ of the `Git
London User Group <https://www.meetup.com/londongit/>`_.


License
=======

Released under `GPL version 2 <COPYING>`_ in order to be consistent
with `git's license
<https://github.com/git/git/blob/master/COPYING>`_, but I'm open to
the idea of dual-licensing if there's a convincing reason.
