#!/usr/bin/env python3
"""Validate the binding-correct Phase 00 archive packet without live mutation."""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import re
import subprocess
import sys

import yaml


ROOT = pathlib.Path(__file__).resolve().parents[1]
PHASE = ROOT / "phase-00"
BASE = "f395c6c922124c716d216d80fee42dba7d3547d2"
BASE_ARCHIVE_SHA256 = "19ffd9a8d342e877d3c56baf190963a16e9339f490f467fd422f9c920ecfb843"
TAG = "placeholder-disposition-freeze-2026-08-19"
TAG_OBJECT = "2e11ce92883d6f37e651198c46634a061b314524"
TAG_TARGET = "4ebc5dabada6fa5ef95e54545d5fb8882bb213a9"
CLASSES = {
    "implementation",
    "artifact",
    "deployment",
    "activation",
    "authority",
    "qualification",
    "observation",
}
CANONICAL = {
    "SPECIFIED",
    "REFERENCE",
    "IMPLEMENTED",
    "SHADOW",
    "CANARY",
    "QUALIFIED",
    "CURRENT_AUTHORITY",
    "OBSERVED_LIVE",
    "RETIRED",
    "UNKNOWN",
}
FORBIDDEN_ROOTS = {
    "Cargo.toml",
    "Dockerfile",
    "package.json",
    "pyproject.toml",
    "wrangler.json",
    "wrangler.jsonc",
    "wrangler.toml",
}
SECRET_PATTERNS = (
    re.compile(rb"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----"),
    re.compile(rb"AKIA[0-9A-Z]{16}"),
    re.compile(rb"gh[pousr]_[A-Za-z0-9]{30,}"),
    re.compile(rb"xox[baprs]-[A-Za-z0-9-]{20,}"),
)


def fail(message: str) -> None:
    raise AssertionError(message)


def run(*args: str, input_bytes: bytes | None = None) -> bytes:
    return subprocess.run(
        args,
        cwd=ROOT,
        input=input_bytes,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ).stdout


def load(name: str) -> dict:
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                fail(f"duplicate JSON key in {name}: {key}")
            result[key] = value
        return result

    return json.loads((PHASE / name).read_text(encoding="utf-8"), object_pairs_hook=unique)


def validate_archive() -> None:
    archive = run("git", "archive", "--format=tar", BASE)
    if hashlib.sha256(archive).hexdigest() != BASE_ARCHIVE_SHA256:
        fail("base archive digest drift")
    if run("git", "rev-parse", f"refs/tags/{TAG}").decode().strip() != TAG_OBJECT:
        fail("freeze tag object drift")
    if run("git", "rev-parse", f"refs/tags/{TAG}^{{}}").decode().strip() != TAG_TARGET:
        fail("freeze tag target drift")


def validate_workflow() -> None:
    workflow_path = ROOT / ".github/workflows/ci.yml"
    workflow = yaml.safe_load(workflow_path.read_text(encoding="utf-8"))
    if workflow.get("permissions") != {"contents": "read"}:
        fail("workflow permissions must be exactly contents: read")
    if set(workflow.get("jobs", {})) != {"validate"}:
        fail("archive must have exactly one validation job")
    text = workflow_path.read_text(encoding="utf-8").casefold()
    for forbidden in ("deploy", "publish", "release", "wrangler", "cloudflare"):
        if forbidden in text:
            fail(f"mutable workflow token present: {forbidden}")
    expected = "actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683"
    if expected not in workflow_path.read_text(encoding="utf-8"):
        fail("checkout action is not pinned to the reviewed commit")


def validate_source_boundary() -> None:
    present = sorted(name for name in FORBIDDEN_ROOTS if (ROOT / name).exists())
    if present:
        fail(f"runtime/package root files present: {present}")
    tracked = run("git", "ls-files").decode().splitlines()
    workflow_paths = [path for path in tracked if path.startswith(".github/workflows/")]
    if workflow_paths != [".github/workflows/ci.yml"]:
        fail(f"unexpected workflow set: {workflow_paths}")


def validate_reachable_blob_secret_patterns() -> None:
    objects = run("git", "rev-list", "--objects", "--all").decode().splitlines()
    checked = set()
    findings = []
    for line in objects:
        oid = line.split(" ", 1)[0]
        if oid in checked:
            continue
        checked.add(oid)
        if run("git", "cat-file", "-t", oid).decode().strip() != "blob":
            continue
        blob = run("git", "cat-file", "blob", oid)
        if any(pattern.search(blob) for pattern in SECRET_PATTERNS):
            findings.append(oid)
    if findings:
        fail(f"high-confidence credential pattern in reachable blobs: {findings}")


def validate_packet(preseal: bool) -> None:
    baseline = load("archive-baseline.v1.json")
    status = load("status.v1.json")
    rollback = load("rollback.v1.json")
    corpus = load("test-fault-corpus.v1.json")
    if baseline["repository"]["refreshed_head"] != BASE:
        fail("baseline head drift")
    if baseline["source_archive"]["sha256"] != BASE_ARCHIVE_SHA256:
        fail("baseline archive digest declaration drift")
    if baseline["freeze_tag"]["signature"] != "NOT_OBSERVED":
        fail("unsigned tag promoted to signed evidence")
    if baseline["freeze_tag"]["new_tag_created_by_phase"] is not False:
        fail("phase claims a new tag")
    if baseline["github_visible_inventory"]["scope_non_claim"] == "":
        fail("GitHub inventory lacks scope non-claim")
    if status["phase_disposition"] != "IMPLEMENTED_NOT_QUALIFIED":
        fail("unsafe phase disposition")
    if status["canonical_capability_status"] not in CANONICAL:
        fail("non-canonical capability status")
    if status["canonical_capability_status"] != "UNKNOWN":
        fail("archive asserts a runtime capability status")
    if status["authority_movement"] != "NONE" or status["activation"] != "BLOCKED":
        fail("archive reports activation or authority movement")
    if {item["class"] for item in status["work_items"]} != CLASSES:
        fail("seven-class work-item coverage incomplete")
    if rollback["rollback_target"]["commit"] != BASE:
        fail("rollback target drift")
    if rollback["rollback_executed"] is not False:
        fail("rollback execution claimed")
    if corpus["qualification_non_claim"] == "":
        fail("test corpus lacks qualification non-claim")
    if not preseal:
        closeout = load("closeout.v1.json")
        if closeout["phase_disposition"] != "IMPLEMENTED_NOT_QUALIFIED":
            fail("closeout disposition drift")
        if closeout["authority_movement"] != {"authorized": False, "performed": False, "effect": "NONE"}:
            fail("closeout authority movement")
        if closeout["rollback"]["target_commit"] != BASE:
            fail("closeout rollback target drift")
        commits = closeout["change_commits"]
        if not commits or any(not re.fullmatch(r"[0-9a-f]{40}", item) for item in commits):
            fail("closeout change commits are not exact")
        for commit in commits:
            run("git", "cat-file", "-e", f"{commit}^{{commit}}")
        classes = [item["class"] for item in closeout["work_items"]]
        if set(classes) != CLASSES or len(classes) != len(CLASSES):
            fail("closeout seven-class coverage incomplete or duplicated")
        if closeout["canonical_capability_status"] != "UNKNOWN":
            fail("closeout promotes an archive capability")
        for artifact in closeout["artifacts"]:
            path = artifact["path"]
            if not path.startswith("phase-00/"):
                continue
            target = ROOT / path
            if not target.is_file():
                fail(f"closeout artifact missing: {path}")
            observed = "sha256:" + hashlib.sha256(target.read_bytes()).hexdigest()
            if observed != artifact["digest"]:
                fail(f"closeout artifact digest drift: {path}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preseal", action="store_true")
    args = parser.parse_args()
    validate_archive()
    validate_workflow()
    validate_source_boundary()
    validate_reachable_blob_secret_patterns()
    validate_packet(args.preseal)
    print(
        "PASS: exact base/archive/tag; archive-only workflow; seven classes; "
        "reachable-blob credential patterns clear; activation blocked; authority movement NONE"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AssertionError, KeyError, TypeError, ValueError, subprocess.CalledProcessError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
