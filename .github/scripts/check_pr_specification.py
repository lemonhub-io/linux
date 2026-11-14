#!/usr/bin/env python3
"""Close a pull request that is not a proposal or lacks a DCO sign-off."""

import json
import os
import re
import sys
import urllib.error
import urllib.request

HEADING = re.compile(r"^(#{1,6})[ \t]+(.*?)[ \t]*$")
SIGN_OFF = re.compile(
    r"^Signed-off-by:[ \t]+(.+?)[ \t]+<([^>\s]+)>[ \t]*$",
    re.MULTILINE,
)
API = "https://api.github.com"


def normalize(text):
    text = text or ""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)


def headings(text):
    found = []
    current = None
    for line in normalize(text).split("\n"):
        match = HEADING.match(line)
        if match:
            if current:
                found.append(current)
            current = [len(match.group(1)), match.group(2).strip(), []]
        elif current:
            current[2].append(line)
    if current:
        found.append(current)
    return [(level, title, "\n".join(body).strip()) for level, title, body in found]


def proposal_failures(body):
    parsed = headings(body)
    proposal_at = next(
        (i for i, (level, title, _) in enumerate(parsed) if level == 2 and title == "Proposal"),
        None,
    )
    if proposal_at is None:
        return ["The description is missing the heading `## Proposal`."]
    inside = []
    for level, title, content in parsed[proposal_at + 1 :]:
        if level <= 2:
            break
        inside.append((level, title, content))
    changes = [item for item in inside if item[0] == 3 and item[1] == "Changes"]
    reasons = [item for item in inside if item[0] == 3 and item[1] == "Reasons"]
    failures = []
    if not changes:
        failures.append("The proposal is missing the heading `### Changes`.")
    if not reasons:
        failures.append("The proposal is missing the heading `### Reasons`.")
    if changes and reasons:
        change_at = inside.index(changes[0])
        reason_at = inside.index(reasons[0])
        if change_at > reason_at:
            failures.append("`### Changes` must come before `### Reasons`.")
    if changes and not changes[0][2]:
        failures.append("`### Changes` does not state what the pull request changes.")
    if reasons and not reasons[0][2]:
        failures.append("`### Reasons` does not state why the change is needed.")
    return failures


def dco_failures(commits):
    failures = []
    missing = 0
    shown = 0
    for commit in commits:
        if commit["parents"] > 1:
            continue
        name = commit["name"]
        email = commit["email"]
        signed = any(
            match.group(1) == name and match.group(2) == email
            for match in SIGN_OFF.finditer(commit["message"])
        )
        if signed:
            continue
        missing += 1
        if shown < 30:
            who = f"{name} <{email}>" if name and email else "its author"
            failures.append(f"`{commit['sha'][:12]}` has no DCO sign-off for {who}.")
            shown += 1
    if missing > shown:
        failures.append(f"{missing - shown} more commits have no DCO sign-off.")
    return failures


def github(method, url, payload=None):
    token = os.environ["GITHUB_TOKEN"]
    data = None if payload is None else json.dumps(payload).encode()
    request = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "pr-specification",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(request) as response:
            raw = response.read().decode()
            return response.status, json.loads(raw) if raw else None
    except urllib.error.HTTPError as error:
        detail = error.read().decode()
        raise SystemExit(f"GitHub API {method} {url} failed: {error.code} {detail}")


def commit_pages(repo, number):
    commits = []
    url = f"{API}/repos/{repo}/pulls/{number}/commits?per_page=100"
    while url:
        token = os.environ["GITHUB_TOKEN"]
        request = urllib.request.Request(
            url,
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
                "User-Agent": "pr-specification",
            },
        )
        try:
            with urllib.request.urlopen(request) as response:
                page = json.loads(response.read().decode())
                link = response.headers.get("Link", "")
        except urllib.error.HTTPError as error:
            detail = error.read().decode()
            raise SystemExit(f"GitHub API GET commits failed: {error.code} {detail}")
        for item in page:
            author = item["commit"]["author"] or {}
            commits.append(
                {
                    "sha": item["sha"],
                    "message": item["commit"]["message"] or "",
                    "name": author.get("name") or "",
                    "email": author.get("email") or "",
                    "parents": len(item["parents"]),
                }
            )
        url = None
        for part in link.split(","):
            if 'rel="next"' in part:
                url = part[part.find("<") + 1 : part.find(">")]
    return commits


def main():
    event = json.load(open(os.environ["GITHUB_EVENT_PATH"]))
    pull = event.get("pull_request")
    if not pull:
        return 0
    failures = proposal_failures(pull.get("body") or "")
    commits = commit_pages(os.environ["GITHUB_REPOSITORY"], pull["number"])
    failures.extend(dco_failures(commits))
    if not failures:
        return 0
    if pull.get("state") != "open":
        return 1
    text = "\n".join(
        [
            "This pull request is closed because it does not meet the PR specification.",
            "",
            *[f"- {item}" for item in failures],
            "",
            "The specification is in CONTRIBUTING.md.",
        ]
    )
    repo = os.environ["GITHUB_REPOSITORY"]
    number = pull["number"]
    github(
        "POST",
        f"{API}/repos/{repo}/issues/{number}/comments",
        {"body": text},
    )
    github("PATCH", f"{API}/repos/{repo}/pulls/{number}", {"state": "closed"})
    return 1


if __name__ == "__main__":
    sys.exit(main())
