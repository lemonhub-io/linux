# Linux fork

This is a community fork of Linux 7.4.0-rc2. It keeps its own history. `drivers/` and `sound/` are not in the tree. `arch/` is.

There is no maintainer queue. A pull request enters `main` only when all of these are true:

1. The description is a proposal with the changes and the reasons.
2. Every non-merge commit has the author's DCO sign-off.
3. `make defconfig` and `make vmlinux` succeed.
4. The kernel tests that cover the changed files succeed.

A miss on any step closes the pull request. When all of them pass, CI merges it into `main`.

The mechanisms are written out in [PROJECT.md](PROJECT.md). The proposal and DCO rules are in [CONTRIBUTING.md](CONTRIBUTING.md). Kernel build notes remain in [README](README).
