# Project

This repository is a community Linux fork. It tracks a snapshot of Linux 7.4.0-rc2 and keeps its own history. There is no maintainer queue and no required review. A change enters `main` when its author publishes a proposal, signs the Developer Certificate of Origin, and the public CI accepts the tree. The same rules close or merge every pull request.

The upstream snapshot is `97d73c8251226cf27cc6656b4c542869bb8c69fa`. The tree matches that snapshot, including `arch/`, `drivers/`, and `sound/`.

## How a change lands

1. Open a pull request against `main`.
2. The description is a proposal. It states what changes and why.
3. Every non-merge commit carries the author's DCO sign-off.
4. The specification check runs from the workflow on `main`. A miss closes the pull request.
5. CI compiles `vmlinux`. A build failure closes the pull request.
6. CI runs the kernel tests that cover the changed files. A test failure closes the pull request. A diff with no matching suite passes this step.
7. When the proposal, the sign-off, the build, and the tests have all passed, the pull request is merged into `main` with a merge commit.

Nobody has to approve the pull request. The proposal, the sign-off, and the CI are the gate.

## The tree

The build is the upstream Linux 7.4.0-rc2 build. `Kbuild` descends into `drivers/` and `sound/` along with the rest of the tree. `make defconfig` followed by `make vmlinux` is what CI compiles.

## The proposal

The pull request description is the community record of the change. It uses these headings, in this order:

```
## Proposal

### Changes

### Reasons
```

`### Changes` says what the pull request changes. `### Reasons` says why that change is needed. Both sections must contain that text. An empty section, or the template left unfilled, does not qualify. The check strips HTML comments before it reads the sections, so a comment is not a proposal.

The template inserted for a new pull request is `.github/PULL_REQUEST_TEMPLATE.md`. The normative rules are in `CONTRIBUTING.md`.

## The Developer Certificate of Origin

Each commit's author certifies Developer Certificate of Origin 1.1 by adding a trailer that matches the commit author exactly:

```
Signed-off-by: Author Name <author@example.com>
```

`git commit -s` writes that trailer from the configured author name and email. The name and the email must be identical to the author recorded in the commit. A merge commit does not need a sign-off. The full certificate is in `CONTRIBUTING.md`.

## The checks run from main

A pull request cannot replace the gate that judges it.

The specification workflow is `.github/workflows/pr-specification.yml`. It runs on `pull_request_target`, so the workflow and the checker come from the default branch. The checker reads the pull request body and the commit list through the GitHub API. It does not run the pull request's code. If the proposal or a sign-off is missing and the pull request is still open, it comments with the misses and closes the pull request.

`.github/workflows/kernel-ci.yml` starts only after that workflow completes successfully, and only for an open pull request whose base branch is `main`. Compilation checks out the pull request and runs `make defconfig` then `make vmlinux`. The test step checks out the test runner from `main` and the tree from the pull request, then runs `.github/scripts/run-kernel-tests.sh` from `main`. The script selects suites from the diff. The commands are not taken from the pull request.

## Tests

The test step maps changed paths to in-tree host tests:

| Changed paths | Suite |
| --- | --- |
| `lib/radix-tree.c`, `lib/xarray.c`, `lib/maple_tree.c`, `lib/idr.c`, `lib/test_xarray.c`, `lib/test_ida.c`, the matching headers, `tools/testing/radix-tree/` | `tools/testing/radix-tree` |
| `lib/rbtree.c`, `lib/interval_tree.c`, the matching headers, `tools/testing/rbtree/` | `tools/testing/rbtree` |
| `mm/vma*`, `tools/testing/vma/` | `tools/testing/vma` |
| `mm/memblock.c`, `include/linux/memblock.h`, `tools/testing/memblock/` | `tools/testing/memblock` |

Each selected suite is built and its test binaries are run. If the diff matches none of these paths, the step reports that no relevant test applies and succeeds. A failure of a selected suite closes the pull request. Compilation has already finished by then. Tests do not run when the build failed.

## main

`main` accepts changes through pull requests. The `PR specification` check must pass. Force-pushes and deletion of `main` are refused. Repository admins can bypass those branch rules. The CI jobs do not exempt an admin's pull request: a proposal, sign-off, build, or test failure still closes it, and a pass still merges it.

## What a merge means

A merge means the description was a proposal, every non-merge commit was signed by its author, `vmlinux` built from `defconfig`, and every selected host test passed. It does not mean a person reviewed the design. It does not boot the kernel.
