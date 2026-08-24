#!/usr/bin/env python3
"""Strict offline validation for the historical-usability archive candidate."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

import yaml


ROOT = Path(__file__).resolve().parents[1]
PHASE = ROOT / "phase-01"
ARCHITECTURE = "2026-08-23-final-phased-prompts.3"
PHASE00_HEAD = "9554180db2b73b426a87128e10fbe12c097ee786"
PHASE00_TREE = "e0a9e141f14bdfd3b90131ff0ec55551393777a8"
SAMPLE_HEAD = "069c2448ee3c5e7c352d096494d15e8f120cf433"
SAMPLE_TREE = "dcc70bd212ff8d1499aa5f2141a429629bf066a5"
SAMPLE_ARCHIVE_SHA256 = "e9667fd5da1f20aa933b0503ff2249fc7b6c42f66e94f4c671658085592a9197"
SAMPLE_MANIFEST_SHA256 = "5aed9828ef4b8069eea0eb53ccf04a58373208ad66fd8d0d191f3e6aedc3e2b4"
WORK_CLASSES = [
    "implementation",
    "artifact",
    "deployment",
    "activation",
    "authority",
    "qualification",
    "observation",
]
MODIFIED_PATHS = {
    ".github/workflows/ci.yml",
    "CONTRIBUTING.md",
    "README.md",
}
CORE_ADDITIONS = {
    ".github/ISSUE_TEMPLATE/archive-record.yml",
    ".github/ISSUE_TEMPLATE/config.yml",
    "docs/archive/HISTORICAL_BUILD.md",
    "phase-01/README.md",
    "phase-01/repository-phase-closeout.schema.json",
    "phase-01/status.v1.json",
    "phase-01/test-fault-corpus.v1.json",
    "phase-01/test_validate.py",
    "phase-01/validate.py",
}
SEAL_ADDITIONS = {
    "phase-01/artifact-manifest.v1.json",
    "phase-01/closeout.v1.json",
    "phase-01/closeout.sha256",
}
FORBIDDEN_ADDITIONS = {
    "Cargo.toml",
    "Dockerfile",
    "package.json",
    "pyproject.toml",
    "wrangler.json",
    "wrangler.jsonc",
    "wrangler.toml",
    "src",
    "schemas",
    "operations",
    "packs",
    "profile",
}
MARKDOWN_LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)", re.DOTALL)
HEADING = re.compile(r"^#{1,6}\s+(.+?)\s*#*\s*$", re.MULTILINE)
SHA256 = re.compile(r"^[0-9a-f]{64}$")
SHA1 = re.compile(r"^[0-9a-f]{40}$")


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


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            fail(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load_json(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_object)
    if not isinstance(value, dict):
        fail(f"JSON root must be an object: {path}")
    return value


def tree_paths(treeish: str) -> set[str]:
    return set(run("git", "ls-tree", "-r", "--name-only", treeish).decode().splitlines())


def current_paths() -> set[str]:
    tracked = set(run("git", "ls-files").decode().splitlines())
    untracked = set(
        run("git", "ls-files", "--others", "--exclude-standard").decode().splitlines()
    )
    return tracked | untracked


def validate_source_boundary(preseal: bool) -> None:
    if run("git", "rev-parse", f"{PHASE00_HEAD}^{{tree}}").decode().strip() != PHASE00_TREE:
        fail("Phase 00 source tree drift")
    base_paths = tree_paths(PHASE00_HEAD)
    additions = CORE_ADDITIONS if preseal else CORE_ADDITIONS | SEAL_ADDITIONS
    expected = base_paths | additions
    actual = current_paths()
    if actual != expected:
        fail(
            "exact archive source boundary drift: "
            f"missing={sorted(expected - actual)} extra={sorted(actual - expected)}"
        )

    allowed_changes = MODIFIED_PATHS | additions
    changed = set(run("git", "diff", "--name-only", PHASE00_HEAD).decode().splitlines())
    changed |= set(run("git", "ls-files", "--others", "--exclude-standard").decode().splitlines())
    if not changed <= allowed_changes:
        fail(f"Phase 00 path changed outside Phase 01 boundary: {sorted(changed - allowed_changes)}")

    for relative in sorted(base_paths - MODIFIED_PATHS):
        path = ROOT / relative
        if path.is_symlink():
            fail(f"symlink not permitted in archive source boundary: {relative}")
        expected_bytes = run("git", "show", f"{PHASE00_HEAD}:{relative}")
        if path.read_bytes() != expected_bytes:
            fail(f"Phase 00-owned bytes changed: {relative}")
    for relative in additions:
        path = ROOT / relative
        if path.is_symlink() or not path.is_file():
            fail(f"Phase 01 path missing or symlinked: {relative}")
    for forbidden in FORBIDDEN_ADDITIONS:
        if forbidden in additions or any(item.startswith(f"{forbidden}/") for item in additions):
            fail(f"runtime/package path added: {forbidden}")


def github_anchor(value: str) -> str:
    value = re.sub(r"[`*_~]", "", value.strip().casefold())
    value = re.sub(r"[^\w\- ]", "", value)
    value = re.sub(r"\s+", "-", value)
    return re.sub(r"-+", "-", value).strip("-")


def heading_anchors(path: Path) -> set[str]:
    text = path.read_text(encoding="utf-8")
    anchors: set[str] = set()
    counts: dict[str, int] = {}
    for heading in HEADING.findall(text):
        base = github_anchor(heading)
        count = counts.get(base, 0)
        counts[base] = count + 1
        anchors.add(base if count == 0 else f"{base}-{count}")
    return anchors


def validate_link_destination(source: Path, destination: str) -> None:
    destination = destination.strip()
    if destination.startswith("<") and destination.endswith(">"):
        destination = destination[1:-1]
    parsed = urlsplit(destination)
    if parsed.scheme:
        if parsed.scheme != "https" or not parsed.netloc:
            fail(f"unsupported external link in {source}: {destination}")
        return
    if parsed.netloc:
        fail(f"protocol-relative link in {source}: {destination}")
    raw_path = unquote(parsed.path)
    if (
        "\0" in raw_path
        or "\\" in raw_path
        or raw_path.startswith("/")
        or parsed.query
    ):
        fail(f"unsafe local link in {source}: {destination}")
    parts = [part for part in raw_path.split("/") if part]
    encoded_parts = [part for part in parsed.path.split("/") if part]
    if any(
        unquote(part) in {".", ".."} and part not in {".", ".."}
        for part in encoded_parts
    ):
        fail(f"encoded traversal in local link: {source}: {destination}")

    target = source if raw_path == "" else source.parent.joinpath(*parts)
    root = ROOT.resolve()
    resolved = target.resolve()
    try:
        resolved.relative_to(root)
    except ValueError:
        fail(f"local link escapes repository: {destination}")
    if not target.exists() or target.is_symlink():
        fail(f"local link target missing or symlinked: {source}: {destination}")
    if target.is_dir():
        target = target / "README.md"
        if not target.is_file() or target.is_symlink():
            fail(f"linked directory lacks README.md: {destination}")
    if parsed.fragment:
        if target.suffix.casefold() != ".md":
            fail(f"heading fragment targets non-Markdown file: {destination}")
        fragment = unquote(parsed.fragment).casefold()
        if fragment not in heading_anchors(target):
            fail(f"missing Markdown heading fragment: {source}: {destination}")


def validate_links() -> int:
    markdown_paths = sorted(path for path in current_paths() if path.endswith(".md"))
    if len(markdown_paths) > 128:
        fail("Markdown file count exceeds fixed archive limit")
    checked = 0
    for relative in markdown_paths:
        source = ROOT / relative
        text = source.read_text(encoding="utf-8")
        if len(text.encode()) > 1_048_576:
            fail(f"Markdown file exceeds fixed byte limit: {relative}")
        for destination in MARKDOWN_LINK.findall(text):
            validate_link_destination(source, destination)
            checked += 1
    if checked == 0:
        fail("link checker exercised no links")
    return checked


def validate_historical_build() -> None:
    if run("git", "rev-parse", f"{SAMPLE_HEAD}^{{tree}}").decode().strip() != SAMPLE_TREE:
        fail("historical sample tree drift")
    archive = run("git", "archive", "--format=tar", SAMPLE_HEAD)
    if sha256(archive) != SAMPLE_ARCHIVE_SHA256:
        fail("historical sample archive digest drift")
    manifest = ROOT / "docs/archive/placeholder/V1_SAMPLE_MANIFEST.sha256"
    if sha256(manifest.read_bytes()) != SAMPLE_MANIFEST_SHA256:
        fail("historical sample manifest digest drift")
    note = (ROOT / "docs/archive/HISTORICAL_BUILD.md").read_text(encoding="utf-8")
    for identity in (SAMPLE_HEAD, SAMPLE_TREE, SAMPLE_ARCHIVE_SHA256, SAMPLE_MANIFEST_SHA256):
        if identity not in note:
            fail(f"historical build note omits identity {identity}")
    for command in ("git archive --format=tar", "npm test", "npm run check", "cargo test"):
        if command not in note:
            fail(f"historical build note omits command {command}")
    if "could not complete the Rust command" not in re.sub(r"\s+", " ", note):
        fail("historical build note hides retained Rust limitation")


def validate_issue_form_document(form: dict[str, object], config: dict[str, object]) -> None:
    if set(form) != {"name", "description", "title", "labels", "assignees", "body"}:
        fail("issue form root field drift")
    if form.get("labels") != [] or form.get("assignees") != []:
        fail("issue form invents repository labels or assignees")
    description = form.get("description")
    if not isinstance(description, str) or "Feature and runtime requests are not accepted." not in description:
        fail("issue form admits feature/runtime work")
    body = form.get("body")
    if not isinstance(body, list):
        fail("issue form body missing")
    ids = [item.get("id") for item in body if isinstance(item, dict)]
    if ids != ["record_type", "identity", "evidence", "attestations"]:
        fail("issue form exact field sequence drift")
    serialized = json.dumps(form, sort_keys=True)
    for phrase in ("Archive-safety issue", "Do not include a credential", "does not accept feature"):
        if phrase not in serialized:
            fail(f"issue form missing archive boundary phrase: {phrase}")
    if config != {"blank_issues_enabled": False, "contact_links": []}:
        fail("issue template configuration must disable blank issues and external contacts")


def validate_issue_form() -> None:
    form = yaml.safe_load((ROOT / ".github/ISSUE_TEMPLATE/archive-record.yml").read_text())
    config = yaml.safe_load((ROOT / ".github/ISSUE_TEMPLATE/config.yml").read_text())
    if not isinstance(form, dict) or not isinstance(config, dict):
        fail("issue template YAML root must be an object")
    validate_issue_form_document(form, config)


def validate_workflow() -> None:
    workflow_path = ROOT / ".github/workflows/ci.yml"
    workflow = yaml.safe_load(workflow_path.read_text(encoding="utf-8"))
    if workflow.get("permissions") != {"contents": "read"}:
        fail("workflow permissions must be exactly contents: read")
    if set(workflow.get("jobs", {})) != {"validate"}:
        fail("archive must retain one validation-only job")
    text = workflow_path.read_text(encoding="utf-8").casefold()
    for forbidden in ("curl ", "wget ", "gh api", "secrets.", "contents: write", "id-token: write"):
        if forbidden in text:
            fail(f"mutable or secret-bearing workflow token: {forbidden}")
    for identity in (PHASE00_HEAD, "PyYAML==6.0.3", "phase-01/validate.py"):
        if identity not in workflow_path.read_text(encoding="utf-8"):
            fail(f"workflow omits exact validation identity {identity}")


def validate_status() -> None:
    status = load_json(PHASE / "status.v1.json")
    if status.get("architecture_binding") != ARCHITECTURE:
        fail("status architecture drift")
    if status.get("phase_disposition") != "IMPLEMENTED_NOT_QUALIFIED":
        fail("status qualification inflation")
    if status.get("canonical_capability_status") != "UNKNOWN":
        fail("archive claims runtime capability status")
    if status.get("archive_artifact_status") != "REFERENCE":
        fail("archive historical artifact status drift")
    if status.get("activation") != "BLOCKED" or status.get("accepts_feature_work") is not False:
        fail("archive activation or feature boundary drift")
    if status.get("runtime_dependencies") != [] or status.get("active_consumers_observed") != []:
        fail("archive invents active dependency or consumer")
    if status.get("active_dependency_inventory_complete") is not False:
        fail("archive overclaims dependency inventory completeness")
    movement = status.get("authority_movement")
    if movement != {"authorized": False, "performed": False, "effect": "NONE"}:
        fail("archive authority movement")
    items = status.get("work_items")
    if not isinstance(items, list) or [item.get("class") for item in items] != WORK_CLASSES:
        fail("status seven-class sequence drift")
    lifecycle = status.get("data_collection")
    if not isinstance(lifecycle, dict) or set(lifecycle.values()) != {"none", "not-applicable"}:
        fail("archive data lifecycle drift")
    limits = status.get("limits")
    expected = {
        "max_markdown_files": 128,
        "max_markdown_bytes_each": 1_048_576,
        "external_fetches": 0,
        "writes": 0,
        "effects": 0,
    }
    if limits != expected:
        fail("archive fixed validation limits drift")


def validate_corpus() -> None:
    corpus = load_json(PHASE / "test-fault-corpus.v1.json")
    if corpus.get("architecture_binding") != ARCHITECTURE:
        fail("fault corpus architecture drift")
    positive = corpus.get("positive_cases")
    negative = corpus.get("negative_cases")
    if not isinstance(positive, list) or len(positive) < 5:
        fail("fault corpus positive coverage incomplete")
    if not isinstance(negative, list) or len(negative) < 12:
        fail("fault corpus negative coverage incomplete")
    durable = corpus.get("durable_state")
    if not isinstance(durable, dict) or durable.get("writes") != 0 or durable.get("effects") != 0:
        fail("fault corpus invents durable archive state")


def validate_closeout(preseal: bool) -> None:
    if preseal:
        return
    manifest = load_json(PHASE / "artifact-manifest.v1.json")
    if manifest.get("architecture_binding") != ARCHITECTURE:
        fail("manifest architecture drift")
    entries = manifest.get("entries")
    if not isinstance(entries, list) or len(entries) < 10:
        fail("manifest source boundary incomplete")
    paths: set[str] = set()
    for entry in entries:
        if not isinstance(entry, dict) or set(entry) != {"path", "sha256"}:
            fail("manifest entry shape drift")
        path = entry.get("path")
        expected = entry.get("sha256")
        if not isinstance(path, str) or not isinstance(expected, str) or not SHA256.fullmatch(expected):
            fail("manifest entry identity malformed")
        if path in paths:
            fail(f"duplicate manifest path: {path}")
        paths.add(path)
        target = ROOT / path
        if not target.is_file() or target.is_symlink() or sha256(target.read_bytes()) != expected:
            fail(f"manifest digest drift: {path}")
    required_manifest = (MODIFIED_PATHS | CORE_ADDITIONS) - {"phase-01/test_validate.py"}
    if not required_manifest <= paths:
        fail(f"manifest missing Phase 01 source: {sorted(required_manifest - paths)}")

    closeout = load_json(PHASE / "closeout.v1.json")
    schema = load_json(PHASE / "repository-phase-closeout.schema.json")
    required = schema.get("required")
    properties = schema.get("properties")
    if not isinstance(required, list) or not isinstance(properties, dict):
        fail("local closeout schema malformed")
    if set(closeout) != set(required) or set(closeout) != set(properties):
        fail("closeout does not match exact local schema root")
    constants = {
        key: rule["const"]
        for key, rule in properties.items()
        if isinstance(rule, dict) and "const" in rule
    }
    for key, expected in constants.items():
        if closeout.get(key) != expected:
            fail(f"closeout schema constant drift: {key}")
    commits = closeout.get("change_commits")
    if not isinstance(commits, list) or not commits or any(not isinstance(item, str) or not SHA1.fullmatch(item) for item in commits):
        fail("closeout change commit identity malformed")
    for commit in commits:
        run("git", "cat-file", "-e", f"{commit}^{{commit}}")
    work_items = closeout.get("work_items")
    if not isinstance(work_items, list) or [item.get("class") for item in work_items] != WORK_CLASSES:
        fail("closeout seven-class sequence drift")
    for artifact in closeout.get("artifacts", []):
        if not isinstance(artifact, dict):
            fail("closeout artifact malformed")
        path = artifact.get("path")
        digest = artifact.get("digest")
        if not isinstance(path, str) or not isinstance(digest, str) or not digest.startswith("sha256:"):
            fail("closeout artifact identity malformed")
        if sha256((ROOT / path).read_bytes()) != digest.removeprefix("sha256:"):
            fail(f"closeout artifact digest drift: {path}")
    sidecar = (PHASE / "closeout.sha256").read_text(encoding="utf-8").strip()
    expected_sidecar = f"{sha256((PHASE / 'closeout.v1.json').read_bytes())}  phase-01/closeout.v1.json"
    if sidecar != expected_sidecar:
        fail("closeout sidecar digest drift")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preseal", action="store_true")
    args = parser.parse_args()
    validate_source_boundary(args.preseal)
    link_count = validate_links()
    validate_historical_build()
    validate_issue_form()
    validate_workflow()
    validate_status()
    validate_corpus()
    validate_closeout(args.preseal)
    print(
        f"PASS: {link_count} local links/fragments; exact historical archive; "
        "archive-only issue intake; Phase 00 bytes preserved; activation BLOCKED; authority NONE"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AssertionError, KeyError, TypeError, ValueError, yaml.YAMLError, subprocess.CalledProcessError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
