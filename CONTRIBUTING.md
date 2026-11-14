# Pull request specification

A pull request is accepted only when it meets both rules below. One that does not is closed.

## The description is a proposal

The pull request description must be a proposal. It must contain these headings, in this order:

```
## Proposal

### Changes

### Reasons
```

`### Changes` states what the pull request changes. `### Reasons` states why that change is needed. Both sections must contain that text. An empty section, or a template left unfilled, does not meet this rule.

## Sign the Developer Certificate of Origin

Every commit must carry a Developer Certificate of Origin sign-off by its author. Create it with `git commit -s`. The trailer has to match the commit author exactly:

```
Signed-off-by: Author Name <author@example.com>
```

The name and the email in the trailer must be identical to the author name and email recorded in the commit. A merge commit does not need a sign-off.

Adding the trailer certifies Developer Certificate of Origin 1.1:

```
Developer Certificate of Origin
Version 1.1

Copyright (C) 2004, 2006 The Linux Foundation and its contributors.
1 Letterman Drive
Suite D4700
San Francisco, CA, 94129

Everyone is permitted to copy and distribute verbatim copies of this
license document, but changing it is not allowed.

Developer's Certificate of Origin 1.1

By making a contribution to this project, I certify that:

(a) The contribution was created in whole or in part by me and I
    have the right to submit it under the open source license
    indicated in the file; or

(b) The contribution is based upon previous work that, to the best
    of my knowledge, is covered under an appropriate open source
    license and I have the right under that license to submit that
    work with modifications, whether created in whole or in part
    by me, under the same open source license (unless I am
    permitted to submit under a different license), as indicated
    in the file; or

(c) The contribution was provided directly to me by some other
    person who certified (a), (b) or (c) and I have not modified
    it.

(d) I understand and agree that this project and the contribution
    are public and that a record of the contribution (including all
    personal information I submit with it, including my sign-off) is
    maintained indefinitely and may be redistributed consistent with
    this project or the open source license(s) involved.
```

## Enforcement

A pull request that fails either rule is closed. The closing note names each missed requirement. The way to land the work is to open a new pull request that meets this specification.

## Kernel CI

After the proposal and the DCO sign-off pass, CI compiles the kernel and then runs the kernel tests that cover the changed files. Compilation comes first. Tests run only after that build succeeds. A failure of either step closes the pull request.
