#!/usr/bin/env python3
"""Validate the public SteamCloud naming-placeholder archive."""

from __future__ import annotations

import hashlib
import io
import json
import re
import subprocess
import tarfile
from pathlib import Path
from urllib.parse import unquote

import yaml


ROOT = Path(__file__).resolve().parents[1]
BASE = "069c2448ee3c5e7c352d096494d15e8f120cf433"
ARCHIVE_HANDOFF = "541ff226a963ffa9acc1fcc6062b6878c2832592"
BASE_MANIFEST_SHA256 = (
    "5aed9828ef4b8069eea0eb53ccf04a58373208ad66fd8d0d191f3e6aedc3e2b4"
)
PACKAGE_DIGEST = "b3103485838efa9bc1e129a6ea24a0ea362ba704fc365fd783b82b3c5c41a1a9"
PACKAGE_VERSION = "2.0.0-draft"
ARCHIVED_MANIFEST = ROOT / "docs/archive/placeholder/V1_SAMPLE_MANIFEST.sha256"
ARCHITECTURE_ZIP = ROOT / "SteamCloud-SteamGraph-Refined-Architecture-v2.0.zip"
README_NOT_PRODUCTION = "It is not the production SteamCloud implementation."
NO_LIVE_AUTHORITY_SENTENCE = (
    "No live authority, remote repository, visibility, or production secret was changed."
)

STATUS_VOCABULARY = {
    "CURRENT LIVE",
    "IMPLEMENTED BUT NOT LIVE",
    "SHADOW/CANARY",
    "REFERENCE/PROTOTYPE",
    "BLOCKED/NOT QUALIFIED",
    "TARGET",
}

GOVERNING_DOCUMENTS = [
    ROOT / "README.md",
    ROOT / "docs/architecture/AUTHORITY_AND_BOUNDARIES.md",
    ROOT / "docs/architecture/OBSERVABILITY.md",
    ROOT / "docs/decisions/ADR-002-placeholder-archive-disposition.md",
    ROOT / "docs/migration/ACCEPTANCE.md",
    ROOT / "docs/migration/ADMINISTRATOR_HANDOFF.md",
    ROOT / "docs/migration/CLOSEOUT.md",
    ROOT / "docs/roadmap/MIGRATION_ROADMAP.md",
    ROOT / "docs/security/SECURITY_AND_SECRET_PLACEMENT.md",
]

REQUIRED_FILES = GOVERNING_DOCUMENTS + [
    ROOT / ".github/workflows/ci.yml",
    ROOT / ".gitignore",
    ROOT / "CONTRIBUTING.md",
    ROOT / "docs/archive/placeholder/README.md",
    ARCHIVED_MANIFEST,
    ROOT / "docs/migration/BOOTSTRAP_REPORT.md",
    ROOT / "docs/migration/NAMING_ALIASES.json",
    ROOT / "docs/migration/REPOSITORY_INVENTORY.json",
    ROOT / "docs/migration/SIBLING_DEPENDENCIES.json",
    ROOT / "docs/roadmap/PHASE_LEDGER.json",
    ROOT / "scripts/test_validate_placeholder.py",
    ROOT / "scripts/validate_placeholder.py",
]

FORBIDDEN_PATHS = [
    ".github/workflows/architecture-sample-ci.yml",
    "AGENTS.md",
    "CLAUDE.md",
    "Cargo.toml",
    "MANIFEST.sha256",
    "NEW_ROADMAP.md",
    "TARGET_ARCHITECTURE_2.md",
    "package.json",
    "crates",
    "operations",
    "packs",
    "profile",
    "review",
    "schemas",
    "scripts/validate_repository.py",
    "src",
    "test",
]

SECRET_PATTERNS = [
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}"),
    re.compile(r"github_pat_[A-Za-z0-9_]{20,}"),
    re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}"),
]

MARKDOWN_LINK = re.compile(r"\[[^]]+\]\(([^)]+)\)")


def fail(message: str) -> None:
    raise AssertionError(message)


def squashed(text: str) -> str:
    cleaned = [re.sub(r"^>\s?", "", line) for line in text.splitlines()]
    return re.sub(r"\s+", " ", "\n".join(cleaned))


def git_paths(args: list[str]) -> set[Path]:
    output = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=True,
        stdout=subprocess.PIPE,
    ).stdout
    return {Path(name.decode()) for name in output.split(b"\0") if name}


def validate_structure() -> None:
    missing = [str(path.relative_to(ROOT)) for path in REQUIRED_FILES if not path.is_file()]
    if missing:
        fail(f"missing required files: {missing}")
    if ARCHITECTURE_ZIP.exists():
        fail(f"architecture ZIP must be removed: {ARCHITECTURE_ZIP.name}")
    gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
    if "SteamCloud-SteamGraph-Refined-Architecture-*.zip" not in gitignore:
        fail(".gitignore must ignore the architecture ZIP glob")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    if README_NOT_PRODUCTION not in squashed(readme):
        fail("README must state this is not the production SteamCloud implementation")
    for relative in FORBIDDEN_PATHS:
        if (ROOT / relative).exists():
            fail(f"superseded application/sample path remains: {relative}")

    expected = {path.relative_to(ROOT) for path in REQUIRED_FILES}
    actual = git_paths(["ls-files", "-z"]) | git_paths(
        ["ls-files", "-z", "-o", "--exclude-standard"]
    )
    if actual != expected:
        fail(
            "current-tree file drift: "
            f"missing={sorted(map(str, expected - actual))} "
            f"extra={sorted(map(str, actual - expected))}"
        )


def unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            fail(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load_json(path: Path) -> dict[str, object]:
    with path.open(encoding="utf-8") as stream:
        value = json.load(stream, object_pairs_hook=unique_object)
    if not isinstance(value, dict):
        fail(f"JSON root must be an object: {path.relative_to(ROOT)}")
    return value


def validate_json() -> None:
    paths = sorted((ROOT / "docs").rglob("*.json"))
    parsed = {path.name: load_json(path) for path in paths}
    if set(parsed) != {
        "NAMING_ALIASES.json",
        "PHASE_LEDGER.json",
        "REPOSITORY_INVENTORY.json",
        "SIBLING_DEPENDENCIES.json",
    }:
        fail(f"unexpected JSON authority set: {sorted(parsed)}")

    aliases = parsed["NAMING_ALIASES.json"]
    if aliases.get("schema") != "steamcloud.placeholder.naming-aliases.v1":
        fail("naming alias schema mismatch")
    canonical = aliases.get("canonical")
    if not isinstance(canonical, dict):
        fail("canonical naming catalog missing")
    required_canonical = {
        "execution_repository",
        "execution_service_prefix",
        "execution_profile",
        "execution_environment_prefix",
        "execution_operation_prefix",
        "execution_crate_prefix",
        "execution_npm_scope",
        "semantic_repository",
        "semantic_service_prefix",
        "semantic_profile",
        "semantic_environment_prefix",
        "semantic_command_prefix",
        "semantic_crate_prefix",
        "semantic_npm_scope",
    }
    if set(canonical) != required_canonical:
        fail("canonical naming catalog field drift")

    alias_entries = aliases.get("aliases")
    if not isinstance(alias_entries, list):
        fail("alias registry must be a list")
    allowed_status = STATUS_VOCABULARY | {"UNKNOWN"}
    required_alias_fields = {
        "legacy",
        "canonical",
        "kind",
        "current_status",
        "target_status",
        "action_status",
        "first_supported_version",
        "last_supported_version",
        "version_evidence",
        "action",
        "removal_gate",
    }
    seen: set[tuple[object, object]] = set()
    for entry in alias_entries:
        if not isinstance(entry, dict):
            fail("alias entry must be an object")
        missing = required_alias_fields.difference(entry)
        if missing:
            fail(f"alias {entry.get('legacy')} missing fields: {sorted(missing)}")
        identity = (entry["kind"], entry["legacy"])
        if identity in seen:
            fail(f"duplicate alias identity: {identity}")
        seen.add(identity)
        for field in ("current_status", "target_status", "action_status"):
            if entry[field] not in allowed_status:
                fail(f"alias {entry['legacy']} has invalid {field}: {entry[field]}")

    operation_map = {
        entry["legacy"]: entry["canonical"]
        for entry in alias_entries
        if entry["kind"] == "operation_id"
    }
    expected_operations = {
        "steam.account.connect": "steamcloud.account.connect.v1",
        "steam.account.session_status": "steamcloud.account.session-status.v1",
        "steam.catalog.observe": "steamcloud.catalog.observe.v1",
        "steam.gc.self.snapshot": "steamcloud.gc.self-snapshot.v1",
        "steam.market.orderbook.observe": "steamcloud.market.orderbook-observe.v1",
        "steam.market.price.observe": "steamcloud.market.price-observe.v1",
        "steam.profile.owner.refresh": "steamcloud.profile.owner-refresh.v1",
        "steam.profile.public.refresh": "steamcloud.profile.public-refresh.v1",
        "steam.synthetic_gameplay": None,
    }
    if operation_map != expected_operations:
        fail("exact legacy operation alias coverage drift")

    expected_pack_ids = {
        "asf-account-connect",
        "asf-catalog-observe",
        "asf-market-price-observe",
        "asf-owner-sync",
        "asf-public-profile-refresh",
        "asf-session-status",
    }
    observed_pack_ids = {
        entry["legacy"] for entry in alias_entries if entry["kind"] == "pack_id"
    }
    if observed_pack_ids != expected_pack_ids:
        fail("exact legacy pack alias coverage drift")

    expected_action_kinds = {
        "asf.account.session_status",
        "asf.artifact.put",
        "asf.challenge.wait",
        "asf.credential.lease",
        "asf.hypergraph.admit_collection",
        "asf.hypergraph.publish",
        "asf.owner.edge.fetch",
        "asf.owner.edge.wait",
        "asf.resource.acquire",
        "asf.runtime.ensure",
        "asf.steam.catalog.fetch",
        "asf.steam.connect",
        "asf.steam.market.fetch",
        "asf.steam.webapi.fetch",
    }
    observed_action_kinds = {
        entry["legacy"]
        for entry in alias_entries
        if entry["kind"] == "sample_action_kind"
    }
    if observed_action_kinds != expected_action_kinds:
        fail("exact legacy sample action-kind coverage drift")
    if not any(
        entry["kind"] == "profile_id" and entry["legacy"] == "steamcloud"
        for entry in alias_entries
    ):
        fail("exact legacy profile alias is missing")
    if not any(
        entry.get("legacy_repository_id") == 1338764433 for entry in alias_entries
    ):
        fail("placeholder alias is not bound to its stable repository ID")

    dependencies = parsed["SIBLING_DEPENDENCIES.json"]
    if dependencies.get("schema") != "steamcloud.placeholder.sibling-dependencies.v1":
        fail("sibling dependency schema mismatch")
    if dependencies.get("runtime_dependencies") != []:
        fail("placeholder must have no runtime dependencies")
    dependency_entries = dependencies.get("dependencies")
    if not isinstance(dependency_entries, list):
        fail("sibling dependencies must be a list")
    expected_repositories = {
        "NegativeNine/Ember",
        "NegativeNine/Campfire",
        "NegativeNine/steam-platform",
        "NegativeNine/steam-hypergraph",
    }
    if {entry.get("repository") for entry in dependency_entries} != expected_repositories:
        fail("sibling dependency inventory drift")
    if any(
        entry.get("reviewed_sha") is not None
        or entry.get("observed_status") != "UNKNOWN"
        for entry in dependency_entries
    ):
        fail("unverified sibling state must remain unpinned and UNKNOWN")

    inventory = parsed["REPOSITORY_INVENTORY.json"]
    if inventory.get("schema") != "steamcloud.placeholder.repository-inventory.v1":
        fail("repository inventory schema mismatch")
    repository = inventory.get("repository")
    refs = inventory.get("refs")
    github_objects = inventory.get("github_objects")
    if not all(isinstance(value, dict) for value in (repository, refs, github_objects)):
        fail("repository inventory sections must be objects")
    if repository.get("github_id") != 1338764433 or repository.get("head") != BASE:
        fail("repository inventory identity drift")
    if refs.get("branches") != ["main"] or refs.get("tags") != []:
        fail("reviewed ref inventory drift")
    if not str(github_objects.get("private_or_internal_packages", "")).startswith(
        "UNKNOWN:"
    ):
        fail("unverified package state must remain UNKNOWN")
    if not str(github_objects.get("projects_v2", "")).startswith("UNKNOWN:"):
        fail("unverified Projects v2 state must remain UNKNOWN")

    handoff = inventory.get("archive_handoff")
    if not isinstance(handoff, dict):
        fail("archive_handoff observation missing")
    if handoff.get("head") != ARCHIVE_HANDOFF or handoff.get("pull_request") != 2:
        fail("archive handoff identity drift")
    if handoff.get("workflow_name") != "placeholder-archive-validation":
        fail("archive handoff workflow is not archive-validation only")

    bootstrap = inventory.get("this_bootstrap")
    if not isinstance(bootstrap, dict):
        fail("this_bootstrap observation missing")
    if bootstrap.get("pre_edit_head") != ARCHIVE_HANDOFF:
        fail("this_bootstrap pre-edit HEAD drift")
    if bootstrap.get("pages_enabled") is not False:
        fail("this_bootstrap must record that GitHub Pages is not enabled")
    if bootstrap.get("repository_webhooks") != 0:
        fail("this_bootstrap webhook inventory drift")
    if not str(bootstrap.get("private_or_internal_packages", "")).startswith("UNKNOWN:"):
        fail("this_bootstrap private package state must remain UNKNOWN")
    if not str(bootstrap.get("projects_v2", "")).startswith("UNKNOWN:"):
        fail("this_bootstrap Projects v2 state must remain UNKNOWN")

    validate_phase_ledger(parsed["PHASE_LEDGER.json"])


LEDGER_STATUSES = {
    "NOT_STARTED",
    "IN_PROGRESS",
    "IMPLEMENTED_NOT_VALIDATED",
    "VALIDATED_NOT_LIVE",
    "SHADOW",
    "CANARY",
    "BLOCKED",
    "COMPLETE",
    "PRODUCTION_QUALIFIED",
    "RETIRED",
}
TERMINAL_DONE = {"COMPLETE", "PRODUCTION_QUALIFIED", "RETIRED"}
ADMIN_OR_SIBLING_PHASES = {"phase-1", "phase-2", "phase-3", "phase-4"}
REQUIRED_PHASE_IDS = ["phase-0", "phase-1", "phase-2", "phase-3", "phase-4"]
REQUIRED_LEDGER_FIELDS = {
    "id",
    "title",
    "dependencies",
    "status",
    "implemented_scope",
    "missing_scope",
    "acceptance_criteria",
    "tests_and_evidence_required",
    "production_or_migration_risk",
    "rollback_path",
    "completing_commit",
    "date_completed",
    "remaining_blockers",
}


def validate_ledger_entry(entry: object, kind: str) -> dict[str, object]:
    if not isinstance(entry, dict):
        fail(f"{kind} entry must be an object")
    missing = REQUIRED_LEDGER_FIELDS.difference(entry)
    if missing:
        fail(f"{kind} {entry.get('id')} missing fields: {sorted(missing)}")
    status = entry["status"]
    if status not in LEDGER_STATUSES:
        fail(f"{kind} {entry['id']} has invalid status: {status}")
    if not isinstance(entry["dependencies"], list):
        fail(f"{kind} {entry['id']} dependencies must be a list")
    if not isinstance(entry["acceptance_criteria"], list):
        fail(f"{kind} {entry['id']} acceptance_criteria must be a list")
    if not isinstance(entry["tests_and_evidence_required"], list):
        fail(f"{kind} {entry['id']} tests_and_evidence_required must be a list")
    if not isinstance(entry["remaining_blockers"], list):
        fail(f"{kind} {entry['id']} remaining_blockers must be a list")
    if not entry["tests_and_evidence_required"]:
        fail(f"{kind} {entry['id']} missing evidence field")

    commit = entry["completing_commit"]
    completed = entry["date_completed"]
    if status in TERMINAL_DONE:
        if not isinstance(commit, str) or not re.fullmatch(r"[0-9a-f]{40}", commit):
            fail(f"{kind} {entry['id']} terminal status requires completing_commit")
        subprocess.run(
            ["git", "merge-base", "--is-ancestor", commit, "HEAD"],
            cwd=ROOT,
            check=True,
        )
        if not isinstance(completed, str) or not completed:
            fail(f"{kind} {entry['id']} terminal status requires date_completed")
    elif commit is not None:
        fail(f"{kind} {entry['id']} non-terminal status must not claim completing_commit")
    return entry


def validate_phase_ledger(ledger: dict[str, object]) -> None:
    if ledger.get("schema") != "steamcloud.placeholder.phase-ledger.v1":
        fail("phase ledger schema mismatch")
    vocabulary = ledger.get("status_vocabulary")
    if not isinstance(vocabulary, list) or set(vocabulary) != LEDGER_STATUSES:
        fail("phase ledger status vocabulary drift")

    phases = ledger.get("phases")
    if not isinstance(phases, list):
        fail("phase ledger phases must be a list")
    seen: list[str] = []
    for phase in phases:
        record = validate_ledger_entry(phase, "phase")
        phase_id = record["id"]
        if not isinstance(phase_id, str):
            fail("phase id must be a string")
        if phase_id in seen:
            fail(f"duplicate phase id: {phase_id}")
        seen.append(phase_id)
        if phase_id in ADMIN_OR_SIBLING_PHASES and record["status"] in TERMINAL_DONE:
            fail(f"{phase_id} must not be marked complete in this placeholder")
        if phase_id in ADMIN_OR_SIBLING_PHASES and record["status"] != "BLOCKED":
            fail(f"{phase_id} must remain BLOCKED until its external unblocking condition")
        waves = record.get("waves", [])
        if not isinstance(waves, list):
            fail(f"phase {phase_id} waves must be a list")
        wave_ids: set[str] = set()
        for wave in waves:
            wave_record = validate_ledger_entry(wave, "wave")
            wave_id = wave_record["id"]
            if not isinstance(wave_id, str):
                fail("wave id must be a string")
            if wave_id in wave_ids:
                fail(f"duplicate wave id: {wave_id}")
            wave_ids.add(wave_id)
            if (
                phase_id in ADMIN_OR_SIBLING_PHASES
                and wave_record["status"] in TERMINAL_DONE
            ):
                fail(f"{wave_id} must not be marked complete in this placeholder")
    if seen != REQUIRED_PHASE_IDS:
        fail(f"phase ledger must contain {REQUIRED_PHASE_IDS} in order; got {seen}")


def validate_yaml() -> None:
    workflow = ROOT / ".github/workflows/ci.yml"
    with workflow.open(encoding="utf-8") as stream:
        parsed = yaml.load(stream, Loader=yaml.BaseLoader)
    if not isinstance(parsed, dict) or parsed.get("name") != "placeholder-archive-validation":
        fail("archive validation workflow is not a valid workflow mapping")
    if set(parsed.get("on", {})) != {"push", "pull_request"}:
        fail("archive validation workflow trigger drift")
    if parsed.get("permissions") != {"contents": "read"}:
        fail("archive validation workflow permissions must be read-only")
    jobs = parsed.get("jobs", {})
    if set(jobs) != {"validate"}:
        fail("archive validation workflow must contain only the validate job")
    forbidden_jobs = {"deploy", "release", "publish", "production"}
    if forbidden_jobs.intersection(jobs):
        fail("archive validation workflow must not contain production jobs")
    workflow_text = workflow.read_text(encoding="utf-8")
    if "production SteamCloud implementation" in workflow_text:
        fail("archive validation workflow claims production SteamCloud identity")
    steps = parsed.get("jobs", {}).get("validate", {}).get("steps", [])
    checkout = next(
        (step for step in steps if str(step.get("uses", "")).startswith("actions/checkout@")),
        None,
    )
    if checkout is None or checkout.get("with", {}).get("persist-credentials") != "false":
        fail("checkout must disable persisted credentials")


def validate_markdown_links_and_statuses() -> None:
    markdown = [ROOT / "README.md", ROOT / "CONTRIBUTING.md"]
    markdown.extend(sorted((ROOT / "docs").rglob("*.md")))
    broken: list[str] = []
    for source in markdown:
        text = source.read_text(encoding="utf-8")
        for raw in MARKDOWN_LINK.findall(text):
            target, separator, fragment = raw.partition("#")
            if not target or "://" in target or target.startswith("mailto:"):
                resolved = source if not target else None
                if resolved is None:
                    continue
            else:
                resolved = (source.parent / target).resolve()
            if not resolved.exists():
                broken.append(f"{source.relative_to(ROOT)}: {raw}")
                continue
            if separator and resolved.suffix.lower() == ".md":
                headings = []
                for line in resolved.read_text(encoding="utf-8").splitlines():
                    match = re.match(r"^#{1,6}\s+(.+?)\s*#*$", line)
                    if not match:
                        continue
                    heading = re.sub(r"\[([^]]+)\]\([^)]+\)", r"\1", match.group(1))
                    heading = heading.replace("`", "").lower()
                    heading = re.sub(r"[^\w\- ]", "", heading)
                    headings.append(re.sub(r"\s+", "-", heading.strip()))
                if unquote(fragment).lower() not in headings:
                    broken.append(f"{source.relative_to(ROOT)}: {raw} (missing anchor)")
    if broken:
        fail(f"broken Markdown links: {broken}")

    for path in GOVERNING_DOCUMENTS:
        text = path.read_text(encoding="utf-8")
        missing = sorted(status for status in STATUS_VOCABULARY if status not in text)
        if missing:
            fail(f"{path.relative_to(ROOT)} omits status vocabulary: {missing}")


def validate_bootstrap_report() -> None:
    text = (ROOT / "docs/migration/BOOTSTRAP_REPORT.md").read_text(encoding="utf-8")
    required = [
        PACKAGE_DIGEST,
        PACKAGE_VERSION,
        ARCHIVE_HANDOFF,
        BASE,
        "NegativeNine/SteamCloud",
        "SteamCloud-bootstrap-archive",
        "CURRENT LIVE",
        "IMPLEMENTED BUT NOT LIVE",
        "SHADOW/CANARY",
        "REFERENCE/PROTOTYPE",
        "BLOCKED/NOT QUALIFIED",
        "TARGET",
        NO_LIVE_AUTHORITY_SENTENCE,
        "Ember",
        "Campfire",
        "SteamGraph",
    ]
    missing = [item for item in required if item not in text]
    if missing:
        fail(f"bootstrap report missing required evidence: {missing}")


def validate_archive_provenance() -> None:
    for commit in (BASE, ARCHIVE_HANDOFF):
        subprocess.run(
            ["git", "merge-base", "--is-ancestor", commit, "HEAD"],
            cwd=ROOT,
            check=True,
        )
    manifest_bytes = ARCHIVED_MANIFEST.read_bytes()
    archive_bytes = subprocess.run(
        ["git", "archive", "--format=tar", BASE],
        cwd=ROOT,
        check=True,
        stdout=subprocess.PIPE,
    ).stdout

    with tarfile.open(fileobj=io.BytesIO(archive_bytes), mode="r:") as archive:
        files = {
            member.name: archive.extractfile(member).read()
            for member in archive.getmembers()
            if member.isfile()
        }

    original_manifest = files.get("MANIFEST.sha256")
    if original_manifest is None:
        fail("original sample manifest is absent from the archived commit")
    if hashlib.sha256(original_manifest).hexdigest() != BASE_MANIFEST_SHA256:
        fail("original sample manifest digest changed")
    if original_manifest != manifest_bytes:
        fail("archived manifest copy differs from the original commit")

    listed: set[str] = set()
    for line in manifest_bytes.decode("utf-8").splitlines():
        digest, relative = line.split("  ", 1)
        listed.add(relative)
        content = files.get(relative)
        if content is None:
            fail(f"manifest path missing from archived commit: {relative}")
        if hashlib.sha256(content).hexdigest() != digest:
            fail(f"archived content digest mismatch: {relative}")

    expected = set(files).difference({"MANIFEST.sha256"})
    if listed != expected:
        fail(
            "archived manifest path drift: "
            f"missing={sorted(expected - listed)} extra={sorted(listed - expected)}"
        )


def validate_secret_patterns() -> None:
    findings: list[str] = []
    for path in REQUIRED_FILES:
        text = path.read_text(encoding="utf-8")
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                findings.append(f"{path.relative_to(ROOT)}: {pattern.pattern}")
    if findings:
        fail(f"high-confidence secret patterns found: {findings}")


def main() -> int:
    validate_structure()
    validate_json()
    validate_yaml()
    validate_markdown_links_and_statuses()
    validate_bootstrap_report()
    validate_archive_provenance()
    validate_secret_patterns()
    print("placeholder archive validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
