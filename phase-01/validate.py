#!/usr/bin/env python3
"""Fail-closed offline validation for the Phase 01 historical archive candidate."""

from __future__ import annotations

import argparse
import hashlib
from html.parser import HTMLParser
from importlib.metadata import PackageNotFoundError, version as package_version
import json
import re
import subprocess
import sys
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlsplit

from markdown_it import MarkdownIt
from markdown_it.common.utils import isStrSpace
from markdown_it.rules_block.reference import reference as commonmark_reference_rule
import yaml


ROOT = Path(__file__).resolve().parents[1]
PHASE = ROOT / "phase-01"
ARCHITECTURE = "2026-08-23-final-phased-prompts.3"
REPOSITORY = "NegativeNine/SteamCloud-bootstrap-archive"
PHASE00_HEAD = "9554180db2b73b426a87128e10fbe12c097ee786"
PHASE00_TREE = "e0a9e141f14bdfd3b90131ff0ec55551393777a8"
PHASE01_CANDIDATE_HEAD = "4ec31555d6b94d5f2a51638c37be11575d3a1740"
PREVIOUS_IMPLEMENTATION = "ea40b838a474d0b7e4ea4d4b77a8c5d066ea8cc5"
PREVIOUS_IMPLEMENTATION_TREE = "b801be4af80b65aeeae49e1628ec70a3dc557917"
PREVIOUS_SEAL = "9c307777d8555cf2ead5ecaef8faeb5b03ccf337"
PREVIOUS_SEAL_TREE = "f4a23b0eef2562be2991c766e0246e757d052877"
PREVIOUS_REMEDIATION = "1606b618d50ddcd3d3c8a2b95147596e06bcb7ca"
PREVIOUS_REMEDIATION_TREE = "c44252c8868a6422dcc12d7925a5be459c11c6a6"
PREVIOUS_REMEDIATION_SEAL = "39b1bcefed30d0a7247fbbc259b192686657344f"
PREVIOUS_REMEDIATION_SEAL_TREE = "735dfc52254e8a8727aa7427dbd2b6e43e3b7318"
PREVIOUS_RESIDUAL_REMEDIATION = "be729cb07276c01d614e56b4848a218b88f1a4a5"
PREVIOUS_RESIDUAL_REMEDIATION_TREE = "7b7442a24d54c2627dc1abce276c55bd534e860c"
PREVIOUS_RESIDUAL_REMEDIATION_SEAL = "d32437abc20b16884a76587aa145b1bea152cdc5"
PREVIOUS_RESIDUAL_REMEDIATION_SEAL_TREE = "669d240fd205e78f5dceac117ce2cc6219da8540"
PREVIOUS_COMMONMARK_REMEDIATION = "9859982e4e6c8ff677e7e7cc8289dd042b6e4e9b"
PREVIOUS_COMMONMARK_REMEDIATION_TREE = "a09454b85dec130725e891a1f11d103f8c105037"
PREVIOUS_COMMONMARK_REMEDIATION_SEAL = "f68dba1c5b0b016db4321db6e84fdcdb827c93c2"
PREVIOUS_COMMONMARK_REMEDIATION_SEAL_TREE = "455c5b2c2f027809e370e75b7f6ea3e21ea47a4b"
BLOCKING_REVIEW_PATH = (
    "coordinator-dag-execution-2026-08-24/reviews/steamcloud-bootstrap-archive/"
    "phase-01.independent-review.json"
)
BLOCKING_REVIEW_SHA256 = "ce1a9936b879c7d5e1e59ab723b727afb2d683afed7dff1a336129ff0b2e46f8"
RESIDUAL_REVIEW_PATH = (
    "coordinator-dag-execution-2026-08-24/reviews/steamcloud-bootstrap-archive/"
    "phase-01.remediated-final-head-independent-review.json"
)
RESIDUAL_REVIEW_SHA256 = "65ef9897ea328295bab7c96137c396586b7d39b3d15f96ebd1ec386d9f3db0b6"
R09_REVIEW_PATH = (
    "coordinator-dag-execution-2026-08-24/reviews/steamcloud-bootstrap-archive/"
    "phase-01.residual-remediation-exact-head-independent-review.json"
)
R09_REVIEW_SHA256 = "6915198c342339184cb10b049f03beb7f26170f1f9b692f4fd906e8cc24fac91"
R10_REVIEW_PATH = (
    "coordinator-dag-execution-2026-08-24/reviews/steamcloud-bootstrap-archive/"
    "phase-01.commonmark-container-final-head-independent-review.json"
)
R10_REVIEW_SHA256 = "4a67512b056c1afbac15fd3d7af73877c2a7968cd1f15e26042bda066301c0cf"
SAMPLE_HEAD = "069c2448ee3c5e7c352d096494d15e8f120cf433"
SAMPLE_TREE = "dcc70bd212ff8d1499aa5f2141a429629bf066a5"
SAMPLE_ARCHIVE_SHA256 = "e9667fd5da1f20aa933b0503ff2249fc7b6c42f66e94f4c671658085592a9197"
SAMPLE_MANIFEST_SHA256 = "5aed9828ef4b8069eea0eb53ccf04a58373208ad66fd8d0d191f3e6aedc3e2b4"
SAMPLE_ROOT_CARGO_SHA256 = "7ee324692ee2e6ae7b844289759f6680716ed200db62b2c97ef11f79c71c6521"
SAMPLE_CRATE_CARGO_SHA256 = "519b4ad939cea2cc618d6b4fa7826b863ff96e6456916e16537a381d5c877734"
SAMPLE_WORKFLOW_SHA256 = "d2a52a12b15b01aa4af1ece3a59d5e549ddc37c0e93c204ba8cda1eed41edf76"
EXPECTED_LINK_INVENTORY_SHA256 = "baa51740046c5d7c1c606efd48200a91748c9bfebf5f9e22cabb1fe18a46ee50"
EXPECTED_CLOSEOUT_SCHEMA_CANONICAL_SHA256 = "7550d1873b7ce664970772f4a2d430c250095113b9e3fb1c94156a18cb3472fc"

WORK_CLASSES = [
    "implementation",
    "artifact",
    "deployment",
    "activation",
    "authority",
    "qualification",
    "observation",
]
STATUS_WORK_ITEMS = [
    {"class": "implementation", "status": "IMPLEMENTED_ARCHIVE_ONLY"},
    {"class": "artifact", "status": "UNSIGNED_HISTORICAL_REFERENCE"},
    {"class": "deployment", "status": "NOT_APPLICABLE_NOT_PERFORMED"},
    {"class": "activation", "status": "BLOCKED_NOT_AUTHORIZED_NOT_PERFORMED"},
    {"class": "authority", "status": "NONE_NOT_AUTHORIZED_NOT_PERFORMED"},
    {"class": "qualification", "status": "NOT_OBSERVED_NOT_ESTABLISHED"},
    {"class": "observation", "status": "REPOSITORY_LOCAL_ONLY_FRESH_EXACT_HEAD_REVIEW_REQUIRED"},
]
CLOSEOUT_WORK_ITEMS = [
    {"class": "implementation", "status": "IMPLEMENTED_ARCHIVE_ONLY"},
    {"class": "artifact", "status": "UNSIGNED_HISTORICAL_REFERENCE_NOT_ADMITTED"},
    {"class": "deployment", "status": "BLOCKED_NOT_AUTHORIZED_NOT_PERFORMED"},
    {"class": "activation", "status": "BLOCKED_NOT_AUTHORIZED_NOT_PERFORMED"},
    {"class": "authority", "status": "NONE_NOT_AUTHORIZED_NOT_PERFORMED"},
    {"class": "qualification", "status": "BLOCKED_NOT_ESTABLISHED"},
    {"class": "observation", "status": "LOCAL_SOURCE_EVIDENCE_ONLY_FRESH_EXACT_HEAD_REVIEW_REQUIRED"},
]
AUTHORITY_NONE = {"authorized": False, "performed": False, "effect": "NONE"}
REVIEW_GATE = {
    "remediation_chain": [
        {
            "path": BLOCKING_REVIEW_PATH,
            "sha256": BLOCKING_REVIEW_SHA256,
            "finding_ids": [f"ARCHIVE-P1-R0{index}" for index in range(1, 7)],
        },
        {
            "path": RESIDUAL_REVIEW_PATH,
            "sha256": RESIDUAL_REVIEW_SHA256,
            "finding_ids": ["ARCHIVE-P1-R07", "ARCHIVE-P1-R08"],
        },
        {
            "path": R09_REVIEW_PATH,
            "sha256": R09_REVIEW_SHA256,
            "finding_ids": ["ARCHIVE-P1-R09"],
        },
        {
            "path": R10_REVIEW_PATH,
            "sha256": R10_REVIEW_SHA256,
            "finding_ids": ["ARCHIVE-P1-R10"],
        },
    ],
    "fresh_exact_head_review": "REQUIRED_NOT_YET_OBSERVED",
    "signed_acceptance": "NOT_OBSERVED",
    "qualification_effect": "NONE",
    "authority_effect": "NONE",
}

MODIFIED_PATHS = {".github/workflows/ci.yml", "CONTRIBUTING.md", "README.md"}
CORE_ADDITIONS = {
    ".github/ISSUE_TEMPLATE/archive-record.yml",
    ".github/ISSUE_TEMPLATE/config.yml",
    "docs/archive/HISTORICAL_BUILD.md",
    "phase-01/README.md",
    "phase-01/historical-build-evidence.v1.json",
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
SOURCE_ENTRY_PATHS = MODIFIED_PATHS | CORE_ADDITIONS
ALL_PHASE_PATHS = SOURCE_ENTRY_PATHS | SEAL_ADDITIONS
POST_PHASE_ADDITIONS = {
    "docs/ARCHIVE-NOTICE.md",
    "docs/PROVENANCE.md",
    "docs/SOURCE-MANIFEST.md",
    "docs/STATUS.md",
    "docs/refactoring/D0-DOCUMENT-INVENTORY.json",
    "docs/refactoring/D0-DOCUMENT-INVENTORY.md",
}
POST_PHASE_MODIFIED_PATHS = {
    "scripts/test_validate_placeholder.py",
    "scripts/validate_placeholder.py",
}
CURRENT_ALLOWED_CHANGED_PATHS = ALL_PHASE_PATHS | POST_PHASE_ADDITIONS | POST_PHASE_MODIFIED_PATHS
FORBIDDEN_PREFIXES = (
    "Cargo.toml", "Dockerfile", "package.json", "pyproject.toml", "wrangler.json",
    "wrangler.jsonc", "wrangler.toml", "src/", "schemas/", "operations/", "packs/", "profile/",
)
SHA256 = re.compile(r"^[0-9a-f]{64}$")
SHA1 = re.compile(r"^[0-9a-f]{40}$")
HEADING = re.compile(r"^#{1,6}[ \t]+(.+?)[ \t]*#*[ \t]*$", re.MULTILINE)
FENCE = re.compile(r"^[ \t]{0,3}(`{3,}|~{3,})(?:[^\n]*)$")
MAX_LINK_LABEL_CHARS = 4096
MAX_LINK_BRACKET_DEPTH = 32
MAX_LINK_DESTINATION_CHARS = 8192
MAX_LINK_PAREN_DEPTH = 32
MARKDOWN_ESCAPABLE = frozenset(r'!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~')
MARKDOWN_IT_PACKAGE_VERSION = "3.0.0"
MDURL_PACKAGE_VERSION = "0.1.2"


def fail(message: str) -> None:
    raise AssertionError(message)


class MarkdownSyntaxError(AssertionError):
    """Deterministic typed rejection for malformed or deliberately bounded Markdown."""

    def __init__(
        self,
        code: str,
        source: Path,
        offset: int,
        *,
        line: int | None = None,
        column: int | None = None,
    ) -> None:
        self.code = code
        self.source = source
        self.offset = offset
        self.line = line
        self.column = column
        location = f"{source}:{line}:{column}" if line is not None and column is not None else f"{source}:{offset}"
        super().__init__(f"{code}: {location}")


def run(*args: str, input_bytes: bytes | None = None) -> bytes:
    return subprocess.run(args, cwd=ROOT, input=input_bytes, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def assert_exact(actual: object, expected: object, path: str = "$") -> None:
    if type(actual) is not type(expected):
        fail(f"{path} type drift: expected {type(expected).__name__}, got {type(actual).__name__}")
    if isinstance(expected, dict):
        if set(actual) != set(expected):  # type: ignore[arg-type]
            fail(f"{path} field drift: missing={sorted(set(expected) - set(actual))} extra={sorted(set(actual) - set(expected))}")  # type: ignore[arg-type]
        for key, value in expected.items():
            assert_exact(actual[key], value, f"{path}.{key}")  # type: ignore[index]
    elif isinstance(expected, list):
        if len(actual) != len(expected):  # type: ignore[arg-type]
            fail(f"{path} length drift")
        for index, value in enumerate(expected):
            assert_exact(actual[index], value, f"{path}[{index}]")  # type: ignore[index]
    elif actual != expected:
        fail(f"{path} value drift: expected {expected!r}, got {actual!r}")


def unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            fail(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def reject_json_constant(value: str) -> object:
    fail(f"non-finite JSON number: {value}")


def load_json(path: Path) -> dict[str, object]:
    raw = path.read_bytes()
    if len(raw) > 1_048_576:
        fail(f"JSON document exceeds fixed byte limit: {path}")
    value = json.loads(raw.decode("utf-8"), object_pairs_hook=unique_object, parse_constant=reject_json_constant)
    if not isinstance(value, dict):
        fail(f"JSON root must be an object: {path}")
    return value


class StrictYamlLoader(yaml.SafeLoader):
    """YAML 1.2 booleans plus duplicate mapping-key rejection."""


StrictYamlLoader.yaml_implicit_resolvers = {key: list(value) for key, value in yaml.SafeLoader.yaml_implicit_resolvers.items()}
for resolver_key, resolvers in list(StrictYamlLoader.yaml_implicit_resolvers.items()):
    StrictYamlLoader.yaml_implicit_resolvers[resolver_key] = [item for item in resolvers if item[0] != "tag:yaml.org,2002:bool"]
StrictYamlLoader.add_implicit_resolver("tag:yaml.org,2002:bool", re.compile(r"^(?:true|false)$", re.IGNORECASE), list("tTfF"))


def construct_unique_yaml_mapping(loader: StrictYamlLoader, node: yaml.MappingNode, deep: bool = False) -> dict[object, object]:
    loader.flatten_mapping(node)
    result: dict[object, object] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in result:
            fail(f"duplicate YAML key: {key}")
        result[key] = loader.construct_object(value_node, deep=deep)
    return result


StrictYamlLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, construct_unique_yaml_mapping)


def load_yaml_text(raw: str) -> dict[str, object]:
    if len(raw.encode("utf-8")) > 262_144:
        fail("YAML document exceeds fixed byte limit")
    value = yaml.load(raw, Loader=StrictYamlLoader)
    if not isinstance(value, dict):
        fail("YAML root must be an object")
    return value


def load_yaml(path: Path) -> dict[str, object]:
    return load_yaml_text(path.read_text(encoding="utf-8"))


def tree_paths(treeish: str) -> set[str]:
    return set(run("git", "ls-tree", "-r", "--name-only", treeish).decode().splitlines())


def current_paths() -> set[str]:
    tracked = set(run("git", "ls-files").decode().splitlines())
    untracked = set(run("git", "ls-files", "--others", "--exclude-standard").decode().splitlines())
    return tracked | untracked


def candidate_head() -> str:
    """Return the sealed historical Phase 01 candidate, independent of later docs."""
    if run("git", "rev-parse", PHASE01_CANDIDATE_HEAD).decode().strip() != PHASE01_CANDIDATE_HEAD:
        fail("sealed Phase 01 candidate is unavailable")
    return PHASE01_CANDIDATE_HEAD


def candidate_source_commit() -> str:
    return run("git", "rev-parse", f"{candidate_head()}^").decode().strip()


def validate_source_path_set(actual: set[str], expected: set[str]) -> None:
    if actual != expected:
        fail(f"exact archive source boundary drift: missing={sorted(expected - actual)} extra={sorted(actual - expected)}")
    phase_only = actual - tree_paths(PHASE00_HEAD)
    for relative in phase_only:
        if relative in FORBIDDEN_PREFIXES or relative.startswith(FORBIDDEN_PREFIXES):
            fail(f"runtime/package path added: {relative}")


def repository_file(relative: str, *, must_exist: bool = True) -> Path:
    if not isinstance(relative, str) or not relative or "\\" in relative or "\0" in relative:
        fail(f"unsafe repository-relative path: {relative!r}")
    pure = PurePosixPath(relative)
    if pure.is_absolute() or any(part in {"", ".", ".."} for part in pure.parts):
        fail(f"unsafe repository-relative path: {relative!r}")
    if pure.as_posix() != relative:
        fail(f"non-normalized repository-relative path: {relative!r}")
    target = ROOT
    for part in pure.parts:
        target = target / part
        if target.is_symlink():
            fail(f"symlink not permitted in repository path: {relative}")
    try:
        target.resolve().relative_to(ROOT.resolve())
    except ValueError:
        fail(f"repository path escapes root: {relative}")
    if must_exist and not target.is_file():
        fail(f"repository file missing: {relative}")
    return target


def validate_source_boundary(_preseal: bool) -> None:
    if run("git", "rev-parse", f"{PHASE00_HEAD}^{{tree}}").decode().strip() != PHASE00_TREE:
        fail("Phase 00 source tree drift")
    base_paths = tree_paths(PHASE00_HEAD)
    validate_source_path_set(current_paths(), base_paths | POST_PHASE_ADDITIONS | ALL_PHASE_PATHS)
    changed = set(run("git", "diff", "--name-only", PHASE00_HEAD).decode().splitlines())
    changed |= set(run("git", "ls-files", "--others", "--exclude-standard").decode().splitlines())
    if changed != CURRENT_ALLOWED_CHANGED_PATHS:
        fail(f"exact archive changed-path boundary drift: missing={sorted(CURRENT_ALLOWED_CHANGED_PATHS - changed)} extra={sorted(changed - CURRENT_ALLOWED_CHANGED_PATHS)}")
    for relative in sorted(base_paths - MODIFIED_PATHS - POST_PHASE_MODIFIED_PATHS):
        path = repository_file(relative)
        if path.read_bytes() != run("git", "show", f"{PHASE00_HEAD}:{relative}"):
            fail(f"Phase 00-owned bytes changed: {relative}")
    for relative in ALL_PHASE_PATHS | POST_PHASE_ADDITIONS | POST_PHASE_MODIFIED_PATHS:
        repository_file(relative)


def mask_markdown_code(text: str) -> str:
    output: list[str] = []
    active_fence: tuple[str, int] | None = None
    for line in text.splitlines(keepends=True):
        body = line.rstrip("\r\n")
        ending = line[len(body):]
        match = FENCE.match(body)
        if active_fence is not None:
            if match and match.group(1)[0] == active_fence[0] and len(match.group(1)) >= active_fence[1]:
                active_fence = None
            output.append(" " * len(body) + ending)
            continue
        if match:
            active_fence = (match.group(1)[0], len(match.group(1)))
            output.append(" " * len(body) + ending)
            continue
        if body.startswith("    ") or body.startswith("\t"):
            output.append(" " * len(body) + ending)
            continue
        chars = list(body)
        index = 0
        while index < len(body):
            if body[index] != "`":
                index += 1
                continue
            run_length = 1
            while index + run_length < len(body) and body[index + run_length] == "`":
                run_length += 1
            delimiter = "`" * run_length
            closing = body.find(delimiter, index + run_length)
            if closing == -1:
                index += run_length
                continue
            for masked in range(index, closing + run_length):
                chars[masked] = " "
            index = closing + run_length
        output.append("".join(chars) + ending)
    if active_fence is not None:
        fail("unterminated fenced code block")
    return "".join(output)


def github_anchor(value: str) -> str:
    value = re.sub(r"[`*_~]", "", value.strip().casefold())
    value = re.sub(r"[^\w\- ]", "", value)
    value = re.sub(r"\s+", "-", value)
    return re.sub(r"-+", "-", value).strip("-")


def heading_anchors(path: Path) -> set[str]:
    text = mask_markdown_code(path.read_text(encoding="utf-8"))
    anchors: set[str] = set()
    counts: dict[str, int] = {}
    for heading in HEADING.findall(text):
        base = github_anchor(heading)
        count = counts.get(base, 0)
        counts[base] = count + 1
        anchors.add(base if count == 0 else f"{base}-{count}")
    return anchors


def normalize_reference_label(value: str) -> str:
    return re.sub(r"\s+", " ", unescape_markdown(value).strip()).casefold()


def unescape_markdown(value: str) -> str:
    output: list[str] = []
    index = 0
    while index < len(value):
        if (
            value[index] == "\\"
            and index + 1 < len(value)
            and value[index + 1] in MARKDOWN_ESCAPABLE
        ):
            output.append(value[index + 1])
            index += 2
            continue
        output.append(value[index])
        index += 1
    return "".join(output)


def is_markdown_escaped(text: str, index: int) -> bool:
    backslashes = 0
    index -= 1
    while index >= 0 and text[index] == "\\":
        backslashes += 1
        index -= 1
    return backslashes % 2 == 1


def markdown_error(
    code: str,
    source: Path,
    text: str,
    offset: int,
    base_line: int,
) -> MarkdownSyntaxError:
    line_breaks = list(re.finditer(r"\r\n?|\n", text[:offset]))
    line = base_line + len(line_breaks)
    line_start = line_breaks[-1].end() if line_breaks else 0
    column = offset - line_start + 1
    return MarkdownSyntaxError(code, source, offset, line=line, column=column)


def validate_markdown_parser_identity() -> None:
    identities = {
        "markdown-it-py": MARKDOWN_IT_PACKAGE_VERSION,
        "mdurl": MDURL_PACKAGE_VERSION,
    }
    for package, expected in identities.items():
        try:
            actual = package_version(package)
        except PackageNotFoundError:
            fail(f"Markdown parser dependency missing: {package}=={expected}")
        if actual != expected:
            fail(f"Markdown parser dependency drift: {package} expected {expected}, got {actual}")


def mask_inline_code_and_html(text: str) -> str:
    """Mask inactive inline code and raw-HTML tag bytes without changing offsets."""

    chars = list(text)

    def mask_range(start: int, end: int) -> None:
        for masked in range(start, end):
            if chars[masked] not in "\r\n":
                chars[masked] = " "

    index = 0
    while index < len(text):
        if text[index] == "`":
            run_length = 1
            while index + run_length < len(text) and text[index + run_length] == "`":
                run_length += 1
            delimiter = "`" * run_length
            closing = text.find(delimiter, index + run_length)
            if closing != -1:
                mask_range(index, closing + run_length)
                index = closing + run_length
                continue
        special = next(
            (
                (opening, closing)
                for opening, closing in (
                    ("<!--", "-->"),
                    ("<![CDATA[", "]]>") ,
                    ("<?", "?>"),
                )
                if text.startswith(opening, index)
            ),
            None,
        )
        if special is not None:
            opening, terminator = special
            closing = text.find(terminator, index + len(opening))
            if closing != -1:
                closing += len(terminator)
                mask_range(index, closing)
                index = closing
                continue
        declaration = re.match(r"<![A-Z][^>]*>", text[index:])
        if declaration:
            closing = index + len(declaration.group(0))
            mask_range(index, closing)
            index = closing
            continue
        tag = re.match(r"</?[A-Za-z][A-Za-z0-9-]*(?=[\t\n\f />])", text[index:])
        if tag:
            cursor = index + len(tag.group(0))
            quote: str | None = None
            while cursor < len(text):
                char = text[cursor]
                if quote is not None:
                    if char == quote:
                        quote = None
                elif char in {'"', "'"}:
                    quote = char
                elif char == ">":
                    cursor += 1
                    mask_range(index, cursor)
                    index = cursor
                    break
                cursor += 1
            else:
                index += 1
            continue
        index += 1
    return "".join(chars)


def audit_inline_destination(
    source: Path,
    text: str,
    open_index: int,
    base_line: int,
) -> int:
    """Validate one link-like ``](...)`` tail; the AST alone decides activity."""

    def reject(code: str, at: int = open_index) -> None:
        raise markdown_error(code, source, text, at, base_line)

    index = open_index + 1
    while index < len(text) and text[index] in " \t":
        index += 1
    if index >= len(text):
        reject("MARKDOWN_UNTERMINATED_INLINE_DESTINATION")
    if text[index] in "\r\n":
        reject("MARKDOWN_UNSUPPORTED_MULTILINE_INLINE_DESTINATION", index)

    if text[index] == "<":
        angle_open = index
        index += 1
        while index < len(text):
            if index - open_index > MAX_LINK_DESTINATION_CHARS:
                reject("MARKDOWN_LINK_DESTINATION_LIMIT_EXCEEDED")
            char = text[index]
            if char in "\r\n":
                reject("MARKDOWN_UNSUPPORTED_MULTILINE_INLINE_DESTINATION", index)
            if char == "\\" and not is_markdown_escaped(text, index):
                index += 2
                continue
            if char == ">" and not is_markdown_escaped(text, index):
                index += 1
                break
            if char == "<" and not is_markdown_escaped(text, index):
                reject("MARKDOWN_MALFORMED_ANGLE_DESTINATION", index)
            index += 1
        else:
            reject("MARKDOWN_UNTERMINATED_ANGLE_DESTINATION", angle_open)
    else:
        depth = 0
        while index < len(text):
            if index - open_index > MAX_LINK_DESTINATION_CHARS:
                reject("MARKDOWN_LINK_DESTINATION_LIMIT_EXCEEDED")
            char = text[index]
            if char in "\r\n":
                reject("MARKDOWN_UNSUPPORTED_MULTILINE_INLINE_DESTINATION", index)
            if char == "\\" and not is_markdown_escaped(text, index):
                index += 2
                continue
            if char == "<" and not is_markdown_escaped(text, index):
                reject("MARKDOWN_MALFORMED_INLINE_DESTINATION", index)
            if char == "(" and not is_markdown_escaped(text, index):
                depth += 1
                if depth > MAX_LINK_PAREN_DEPTH:
                    reject("MARKDOWN_LINK_PAREN_DEPTH_EXCEEDED")
            elif char == ")" and not is_markdown_escaped(text, index):
                if depth == 0:
                    return index
                depth -= 1
            elif char in " \t" and depth == 0:
                break
            index += 1
        else:
            reject("MARKDOWN_UNTERMINATED_INLINE_DESTINATION")

    while index < len(text) and text[index] in " \t":
        index += 1
    if index >= len(text):
        reject("MARKDOWN_UNTERMINATED_INLINE_DESTINATION")
    if text[index] in "\r\n":
        reject("MARKDOWN_UNSUPPORTED_MULTILINE_INLINE_DESTINATION", index)
    if text[index] == ")":
        return index

    delimiter = text[index]
    if delimiter not in {'"', "'", "("}:
        reject("MARKDOWN_MALFORMED_INLINE_TITLE", index)
    title_open = index
    title_close = ")" if delimiter == "(" else delimiter
    index += 1
    while index < len(text):
        if index - open_index > MAX_LINK_DESTINATION_CHARS:
            reject("MARKDOWN_LINK_DESTINATION_LIMIT_EXCEEDED")
        char = text[index]
        if char in "\r\n":
            reject("MARKDOWN_UNSUPPORTED_MULTILINE_INLINE_TITLE", index)
        if char == "\\" and not is_markdown_escaped(text, index):
            index += 2
            continue
        if char == title_close and not is_markdown_escaped(text, index):
            index += 1
            break
        index += 1
    else:
        code = (
            "MARKDOWN_UNTERMINATED_PARENTHESIZED_TITLE"
            if delimiter == "("
            else "MARKDOWN_UNTERMINATED_QUOTED_TITLE"
        )
        reject(code, title_open)

    while index < len(text) and text[index] in " \t":
        index += 1
    if index >= len(text):
        reject("MARKDOWN_UNTERMINATED_INLINE_DESTINATION")
    if text[index] in "\r\n":
        reject("MARKDOWN_UNSUPPORTED_MULTILINE_INLINE_TITLE", index)
    if text[index] != ")":
        reject("MARKDOWN_MALFORMED_INLINE_TAIL", index)
    return index


def audit_inline_syntax(source: Path, text: str, base_line: int) -> None:
    """Bound link-like syntax while deferring active-link precedence to CommonMark."""

    masked = mask_inline_code_and_html(text)
    bracket_stack: list[int] = []
    index = 0
    while index < len(masked):
        char = masked[index]
        if char == "\\" and not is_markdown_escaped(masked, index):
            index += 2
            continue
        if char == "[" and not is_markdown_escaped(masked, index):
            bracket_stack.append(index)
            if len(bracket_stack) > MAX_LINK_BRACKET_DEPTH:
                raise markdown_error(
                    "MARKDOWN_LINK_BRACKET_DEPTH_EXCEEDED",
                    source,
                    text,
                    bracket_stack[0],
                    base_line,
                )
        elif char == "]" and not is_markdown_escaped(masked, index):
            label_open = bracket_stack.pop() if bracket_stack else None
            if label_open is not None and index - label_open > MAX_LINK_LABEL_CHARS:
                raise markdown_error(
                    "MARKDOWN_LINK_LABEL_LIMIT_EXCEEDED",
                    source,
                    text,
                    label_open,
                    base_line,
                )
            if index + 1 < len(masked) and masked[index + 1] == "(":
                if label_open is not None and any(
                    newline in text[label_open:index] for newline in ("\r", "\n")
                ):
                    raise markdown_error(
                        "MARKDOWN_UNSUPPORTED_MULTILINE_LINK_LABEL",
                        source,
                        text,
                        label_open,
                        base_line,
                    )
                index = audit_inline_destination(source, text, index + 1, base_line)
            elif index + 1 < len(masked) and masked[index + 1] == "[":
                reference_end = index + 2
                while reference_end < len(masked):
                    if masked[reference_end] in "\r\n":
                        raise markdown_error(
                            "MARKDOWN_UNSUPPORTED_MULTILINE_REFERENCE_LABEL",
                            source,
                            text,
                            index + 1,
                            base_line,
                        )
                    if masked[reference_end] == "\\" and not is_markdown_escaped(masked, reference_end):
                        reference_end += 2
                        continue
                    if masked[reference_end] == "]" and not is_markdown_escaped(masked, reference_end):
                        break
                    reference_end += 1
                else:
                    raise markdown_error(
                        "MARKDOWN_UNTERMINATED_REFERENCE_LABEL",
                        source,
                        text,
                        index + 1,
                        base_line,
                    )
        index += 1


def normalized_source_boundary_map(text: str) -> tuple[str, list[int]]:
    """Mirror markdown-it core normalization and retain normalized-to-raw boundaries."""

    normalized: list[str] = []
    boundaries = [0]
    cursor = 0
    while cursor < len(text):
        char = text[cursor]
        if char == "\r":
            cursor += 2 if cursor + 1 < len(text) and text[cursor + 1] == "\n" else 1
            normalized.append("\n")
        else:
            cursor += 1
            normalized.append("\ufffd" if char == "\0" else char)
        boundaries.append(cursor)
    return "".join(normalized), boundaries


def mapped_parser_lines(
    state: object,
    begin: int,
    end: int,
    indent: int,
    normalized_to_raw: list[int],
) -> tuple[str, list[int]]:
    """Mirror StateBlock.getLines while retaining an output-to-source offset map."""

    output: list[str] = []
    source_map: list[int] = []
    for line in range(begin, end):
        line_indent = 0
        line_start = first = state.bMarks[line]  # type: ignore[attr-defined]
        last = state.eMarks[line] + (1 if line + 1 < end else 0)  # type: ignore[attr-defined]
        while first < last and line_indent < indent:
            char = state.src[first]  # type: ignore[attr-defined]
            if isStrSpace(char):
                if char == "\t":
                    line_indent += 4 - (line_indent + state.bsCount[line]) % 4  # type: ignore[attr-defined]
                else:
                    line_indent += 1
            elif first - line_start < state.tShift[line]:  # type: ignore[attr-defined]
                line_indent += 1
            else:
                break
            first += 1
        if line_indent > indent:
            virtual = " " * (line_indent - indent)
            output.append(virtual)
            source_map.extend([normalized_to_raw[first]] * len(virtual))
        segment = state.src[first:last]  # type: ignore[attr-defined]
        output.append(segment)
        source_map.extend(normalized_to_raw[index] for index in range(first, last))
    logical = "".join(output)
    left = 0
    right = len(logical)
    while left < right and logical[left].isspace():
        left += 1
    while right > left and logical[right - 1].isspace():
        right -= 1
    return logical[left:right], source_map[left:right]


def reference_candidate_context(
    state: object,
    start_line: int,
    normalized_to_raw: list[int],
) -> dict[str, object] | None:
    """Return a parser-state-backed definition candidate and its physical source start."""

    if state.is_code_block(start_line):  # type: ignore[attr-defined]
        return None
    normalized_start_offset = state.bMarks[start_line] + state.tShift[start_line]  # type: ignore[attr-defined]
    line_end = state.eMarks[start_line]  # type: ignore[attr-defined]
    if normalized_start_offset >= line_end or state.src[normalized_start_offset] != "[":  # type: ignore[attr-defined]
        return None
    start_offset = normalized_to_raw[normalized_start_offset]

    next_line = start_line + 1
    old_parent_type = state.parentType  # type: ignore[attr-defined]
    state.parentType = "reference"  # type: ignore[attr-defined]
    try:
        terminator_rules = state.md.block.ruler.getRules("reference")  # type: ignore[attr-defined]
        while next_line < state.lineMax and not state.isEmpty(next_line):  # type: ignore[attr-defined]
            if state.sCount[next_line] - state.blkIndent > 3:  # type: ignore[attr-defined]
                next_line += 1
                continue
            if state.sCount[next_line] < 0:  # type: ignore[attr-defined]
                next_line += 1
                continue
            if any(rule(state, next_line, state.lineMax, True) for rule in terminator_rules):  # type: ignore[attr-defined]
                break
            next_line += 1
    finally:
        state.parentType = old_parent_type  # type: ignore[attr-defined]

    logical, source_map = mapped_parser_lines(
        state,
        start_line,
        next_line,
        state.blkIndent,  # type: ignore[attr-defined]
        normalized_to_raw,
    )
    if not source_map or source_map[0] != start_offset:
        fail("parser-backed reference source map start drift")
    cursor = 1
    while cursor < len(logical):
        if logical[cursor] == "\\" and not is_markdown_escaped(logical, cursor):
            cursor += 2
            continue
        if logical[cursor] == "]" and not is_markdown_escaped(logical, cursor):
            if cursor + 1 < len(logical) and logical[cursor + 1] == ":":
                break
            return None
        cursor += 1
    else:
        return None
    return {
        "text": logical,
        "source_map": source_map,
        "start_line": start_line,
        "candidate_offset": start_offset,
        "paragraph_end_line": next_line,
    }


def analyze_reference_candidate(
    source: Path,
    raw_text: str,
    state: object,
    context: dict[str, object],
) -> dict[str, str]:
    """Apply bounded definition policy using the pinned parser's destination/title helpers."""

    candidate = context["text"]
    candidate_offset = context["candidate_offset"]
    source_map = context["source_map"]
    if (
        not isinstance(candidate, str)
        or not isinstance(candidate_offset, int)
        or not isinstance(source_map, list)
        or len(source_map) != len(candidate)
    ):
        fail("reference candidate context type drift")

    def reject(code: str, logical_offset: int = 0) -> None:
        physical_offset = (
            source_map[logical_offset]
            if 0 <= logical_offset < len(source_map)
            else candidate_offset
        )
        raise markdown_error(code, source, raw_text, physical_offset, 1)

    maximum = len(candidate)
    label_end: int | None = None
    cursor = 1
    while cursor < maximum:
        char = candidate[cursor]
        if char == "\\":
            cursor += 2
            continue
        if char == "[":
            reject("MARKDOWN_MALFORMED_REFERENCE_LABEL", cursor)
        if char == "]":
            label_end = cursor
            break
        cursor += 1
    if label_end is None:
        reject("MARKDOWN_UNTERMINATED_REFERENCE_LABEL")
    if label_end > MAX_LINK_LABEL_CHARS:
        reject("MARKDOWN_LINK_LABEL_LIMIT_EXCEEDED")
    if label_end + 1 >= maximum or candidate[label_end + 1] != ":":
        reject("MARKDOWN_MALFORMED_REFERENCE_LABEL", label_end)
    raw_label = candidate[1:label_end]
    if not normalize_reference_label(raw_label):
        reject("MARKDOWN_EMPTY_REFERENCE_LABEL")

    cursor = label_end + 2
    while cursor < maximum and candidate[cursor].isspace():
        cursor += 1
    if cursor >= maximum:
        reject("MARKDOWN_MISSING_REFERENCE_DESTINATION", label_end + 1)
    destination_start = cursor

    if candidate[cursor] == "<":
        scan = cursor + 1
        while scan < maximum:
            if scan - destination_start > MAX_LINK_DESTINATION_CHARS:
                reject("MARKDOWN_LINK_DESTINATION_LIMIT_EXCEEDED", destination_start)
            char = candidate[scan]
            if char == "\\":
                scan += 2
                continue
            if char == "<":
                reject("MARKDOWN_MALFORMED_ANGLE_DESTINATION", scan)
            if char == ">":
                break
            if char in "\r\n":
                reject("MARKDOWN_UNTERMINATED_ANGLE_DESTINATION", destination_start)
            scan += 1
        else:
            reject("MARKDOWN_UNTERMINATED_ANGLE_DESTINATION", destination_start)
    else:
        scan = cursor
        depth = 0
        while scan < maximum:
            if scan - destination_start > MAX_LINK_DESTINATION_CHARS:
                reject("MARKDOWN_LINK_DESTINATION_LIMIT_EXCEEDED", destination_start)
            char = candidate[scan]
            if char == "\\" and scan + 1 < maximum:
                scan += 2
                continue
            if char.isspace() or ord(char) < 0x20 or ord(char) == 0x7F:
                break
            if char == "(":
                depth += 1
                if depth > MAX_LINK_PAREN_DEPTH:
                    reject("MARKDOWN_LINK_PAREN_DEPTH_EXCEEDED", scan)
            elif char == ")":
                if depth == 0:
                    break
                depth -= 1
            scan += 1
        if depth:
            reject("MARKDOWN_MALFORMED_REFERENCE_DESTINATION", destination_start)

    destination_result = state.md.helpers.parseLinkDestination(candidate, cursor, maximum)  # type: ignore[attr-defined]
    if not destination_result.ok:
        reject("MARKDOWN_MALFORMED_REFERENCE_DESTINATION", destination_start)
    if destination_result.pos - destination_start > MAX_LINK_DESTINATION_CHARS:
        reject("MARKDOWN_LINK_DESTINATION_LIMIT_EXCEEDED", destination_start)
    href = state.md.normalizeLink(destination_result.str)  # type: ignore[attr-defined]
    if not state.md.validateLink(href):  # type: ignore[attr-defined]
        reject("MARKDOWN_UNSUPPORTED_REFERENCE_DESTINATION", destination_start)

    destination_end = destination_result.pos
    cursor = destination_end
    while cursor < maximum and candidate[cursor].isspace():
        cursor += 1
    separator = candidate[destination_end:cursor]
    title = ""
    title_result = state.md.helpers.parseLinkTitle(candidate, cursor, maximum)  # type: ignore[attr-defined]
    if cursor < maximum and separator and candidate[cursor] in {'"', "'", "("}:
        if title_result.ok:
            title = title_result.str
            cursor = title_result.pos
            if cursor - destination_start > MAX_LINK_DESTINATION_CHARS:
                reject("MARKDOWN_LINK_DESTINATION_LIMIT_EXCEEDED", destination_start)
        elif "\n" not in separator and "\r" not in separator:
            code = (
                "MARKDOWN_UNTERMINATED_PARENTHESIZED_TITLE"
                if candidate[cursor] == "("
                else "MARKDOWN_UNTERMINATED_QUOTED_TITLE"
            )
            if candidate[cursor] == "(" and "(" in candidate[cursor + 1 :]:
                code = "MARKDOWN_MALFORMED_REFERENCE_TITLE"
            reject(code, cursor)
        else:
            cursor = destination_end
    else:
        cursor = destination_end

    while cursor < maximum and candidate[cursor] in " \t":
        cursor += 1
    if cursor < maximum and candidate[cursor] not in "\r\n" and title:
        title = ""
        cursor = destination_end
        while cursor < maximum and candidate[cursor] in " \t":
            cursor += 1
    if cursor < maximum and candidate[cursor] not in "\r\n":
        code = (
            "MARKDOWN_MALFORMED_REFERENCE_TITLE"
            if candidate[cursor] not in {'"', "'", "("}
            else "MARKDOWN_MALFORMED_REFERENCE_TAIL"
        )
        reject(code, cursor)
    return {"label": raw_label, "destination": href, "title": title}


def parse_commonmark_document(
    source: Path,
    text: str,
) -> tuple[list[object], list[dict[str, object]]]:
    """Parse once with an audited reference rule and exact definition source maps."""

    validate_markdown_parser_identity()
    mask_markdown_code(text)
    parser = MarkdownIt(
        "commonmark",
        {
            "html": True,
            "inline_definitions": True,
            "maxNesting": MAX_LINK_BRACKET_DEPTH * 2,
        },
    )
    definitions: list[dict[str, object]] = []
    seen_labels: set[str] = set()
    normalized_text, normalized_to_raw = normalized_source_boundary_map(text)
    line_starts = [0] + [match.end() for match in re.finditer(r"\r\n?|\n", text)]

    def audited_reference_rule(
        state: object,
        start_line: int,
        end_line: int,
        silent: bool,
    ) -> bool:
        if silent:
            return commonmark_reference_rule(state, start_line, end_line, True)
        if state.src != normalized_text:  # type: ignore[attr-defined]
            fail("markdown-it normalization identity drift")
        context = reference_candidate_context(state, start_line, normalized_to_raw)
        if context is None:
            return commonmark_reference_rule(state, start_line, end_line, False)
        analyzed = analyze_reference_candidate(source, text, state, context)
        token_count = len(state.tokens)  # type: ignore[attr-defined]
        if not commonmark_reference_rule(state, start_line, end_line, False):
            raise markdown_error(
                "MARKDOWN_REFERENCE_PARSER_DIVERGENCE",
                source,
                text,
                int(context["candidate_offset"]),
                1,
            )
        new_definition_tokens = [
            token
            for token in state.tokens[token_count:]  # type: ignore[attr-defined]
            if token.type == "definition"
        ]
        if len(new_definition_tokens) != 1:
            fail("CommonMark reference rule did not emit exactly one definition token")
        token = new_definition_tokens[0]
        if token.map is None or not isinstance(token.meta, dict):
            fail("CommonMark definition token lacks source map or metadata")
        normalized_label = token.meta.get("id")
        if not isinstance(normalized_label, str):
            fail("CommonMark definition token lacks normalized label")
        candidate_offset = int(context["candidate_offset"])
        if normalized_label in seen_labels:
            raise markdown_error(
                "MARKDOWN_DUPLICATE_REFERENCE_DEFINITION",
                source,
                text,
                candidate_offset,
                1,
            )
        seen_labels.add(normalized_label)
        if (
            token.meta.get("label") != analyzed["label"]
            or token.meta.get("url") != analyzed["destination"]
            or token.meta.get("title") != analyzed["title"]
        ):
            fail("audited reference definition diverges from CommonMark token")
        last_line = token.map[1] - 1
        physical_line_start = line_starts[token.map[0]]
        last_physical_line_start = line_starts[last_line]
        end_offset = normalized_to_raw[state.eMarks[last_line]]  # type: ignore[attr-defined]
        definitions.append(
            {
                "occurrence": len(definitions) + 1,
                "line_start": token.map[0] + 1,
                "line_end": token.map[1],
                "column_start": candidate_offset - physical_line_start + 1,
                "column_end": end_offset - last_physical_line_start + 1,
                "offset_start": candidate_offset,
                "offset_end": end_offset,
                "label": analyzed["label"],
                "normalized_label": normalized_label,
                "destination": analyzed["destination"],
                "title": analyzed["title"],
            }
        )
        return True

    parser.block.ruler.at("reference", audited_reference_rule)
    environment: dict[str, object] = {}
    tokens = parser.parse(text, environment)
    definition_tokens = [token for token in tokens if token.type == "definition"]
    if len(definition_tokens) != len(definitions):
        fail("CommonMark definition token inventory cardinality drift")
    if environment.get("duplicate_refs"):
        fail("CommonMark duplicate reference escaped audited definition rejection")
    return tokens, definitions


def extract_reference_definitions(source: Path, text: str) -> list[dict[str, object]]:
    return parse_commonmark_document(source, text)[1]


class LocalHtmlDestinationCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.destinations: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        seen: set[str] = set()
        for key, value in attrs:
            key = key.casefold()
            if key in seen:
                fail(f"duplicate HTML attribute: {tag}.{key}")
            seen.add(key)
            if key in {"href", "src"}:
                if value is None:
                    fail(f"empty HTML destination: {tag}.{key}")
                self.destinations.append(value)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)


def extract_link_destinations(source: Path, text: str) -> list[dict[str, object]]:
    """Return every active CommonMark/HTML destination as an occurrence, never a set."""

    tokens, _definitions = parse_commonmark_document(source, text)

    records: list[dict[str, object]] = []

    def emit(syntax: str, destination: str, line_start: int, line_end: int) -> None:
        records.append(
            {
                "occurrence": len(records) + 1,
                "line_start": line_start,
                "line_end": line_end,
                "syntax": syntax,
                "destination": destination,
            }
        )

    def collect_html(content: str, line_start: int, line_end: int) -> None:
        collector = LocalHtmlDestinationCollector()
        collector.feed(content)
        collector.close()
        for destination in collector.destinations:
            emit("html", destination, line_start, line_end)

    def walk_children(children: list[object], line_start: int, line_end: int) -> None:
        for child in children:
            child_type = getattr(child, "type", "")
            attrs = getattr(child, "attrs", {})
            if child_type == "link_open":
                destination = attrs.get("href")
                if not isinstance(destination, str):
                    fail("CommonMark link token lacks a string href")
                syntax = "autolink" if getattr(child, "markup", "") == "autolink" else "link"
                emit(syntax, destination, line_start, line_end)
            elif child_type == "image":
                destination = attrs.get("src")
                if not isinstance(destination, str):
                    fail("CommonMark image token lacks a string src")
                emit("image", destination, line_start, line_end)
            elif child_type == "html_inline":
                collect_html(getattr(child, "content", ""), line_start, line_end)
            nested = getattr(child, "children", None)
            if nested:
                walk_children(nested, line_start, line_end)

    for token in tokens:
        token_type = token.type
        token_map = token.map
        if token_type == "inline":
            if token_map is None:
                fail("CommonMark inline token lacks a source line map")
            line_start, line_end = token_map[0] + 1, token_map[1]
            audit_inline_syntax(source, token.content, line_start)
            walk_children(token.children or [], line_start, line_end)
        elif token_type == "html_block":
            if token_map is None:
                fail("CommonMark HTML block token lacks a source line map")
            collect_html(token.content, token_map[0] + 1, token_map[1])
    return records


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
    if "\0" in raw_path or "\\" in raw_path or raw_path.startswith("/") or parsed.query:
        fail(f"unsafe local link in {source}: {destination}")
    encoded_parts = [part for part in parsed.path.split("/") if part]
    if any(unquote(part) in {".", ".."} and part not in {".", ".."} for part in encoded_parts):
        fail(f"encoded traversal in local link: {source}: {destination}")
    parts = [part for part in raw_path.split("/") if part]
    target = source if raw_path == "" else source.parent.joinpath(*parts)
    try:
        target.resolve().relative_to(ROOT.resolve())
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


def link_inventory() -> list[dict[str, object]]:
    markdown_paths = sorted(path for path in current_paths() if path.endswith(".md"))
    if len(markdown_paths) > 128:
        fail("Markdown file count exceeds fixed archive limit")
    inventory: list[dict[str, object]] = []
    for relative in markdown_paths:
        source = repository_file(relative)
        text = source.read_text(encoding="utf-8")
        if len(text.encode("utf-8")) > 1_048_576:
            fail(f"Markdown file exceeds fixed byte limit: {relative}")
        records = extract_link_destinations(source, text)
        if [record["occurrence"] for record in records] != list(range(1, len(records) + 1)):
            fail(f"non-contiguous link occurrence identities: {relative}")
        for record in records:
            destination = record["destination"]
            if not isinstance(destination, str):
                fail(f"non-string link destination: {relative}")
            validate_link_destination(source, destination)
            inventory.append({"source": relative, **record})
    # Occurrences are intentionally not deduplicated: repeated destinations are
    # distinct active parser events with stable document-local identities.
    return sorted(inventory, key=lambda item: (str(item["source"]), int(item["occurrence"])))


def validate_links() -> int:
    inventory = link_inventory()
    if not inventory:
        fail("link checker exercised no links")
    digest = sha256(json.dumps(inventory, sort_keys=True, separators=(",", ":")).encode())
    if digest != EXPECTED_LINK_INVENTORY_SHA256:
        fail(f"exact link inventory drift: count={len(inventory)} sha256={digest}")
    return len(inventory)


EXPECTED_HISTORICAL_EVIDENCE = {
    "schema": "steamcloud.archive.phase-01-historical-build-evidence/v1",
    "architecture_binding": ARCHITECTURE, "repository": REPOSITORY, "phase": "01",
    "sample_source": {"commit": SAMPLE_HEAD, "tree": SAMPLE_TREE, "git_archive_sha256": SAMPLE_ARCHIVE_SHA256, "content_manifest_sha256": SAMPLE_MANIFEST_SHA256, "recovery_status": "REPRODUCIBLE_EXACT_SOURCE_BYTES_ONLY"},
    "node_observation": {"status": "OBSERVED_PASS_NOT_TOOLCHAIN_REPRODUCIBILITY", "node_version": "v22.18.0", "dependency_count": 0, "test_count": 20, "test_exit_code": 0, "check_exit_code": 0},
    "rust_observation": {
        "status": "NOT_REPRODUCIBLE_STRUCTURALLY_UNPINNED", "cargo_lock_present": False,
        "root_cargo_toml_sha256": SAMPLE_ROOT_CARGO_SHA256, "crate_cargo_toml_sha256": SAMPLE_CRATE_CARGO_SHA256,
        "historical_toolchain_selector": "stable", "historical_workflow_sha256": SAMPLE_WORKFLOW_SHA256,
        "dependency_constraints": ["async-trait=0.1", "serde=1"],
        "attempted_cargo_version": "cargo 1.97.1 (c980f4866 2026-06-30)",
        "attempted_command": "cargo test --manifest-path <exact sample>/Cargo.toml --workspace --all-targets --offline",
        "attempt_exit_code": 101, "attempt_result": "CC_LINKER_NOT_FOUND_BEFORE_TEST_EXECUTION",
        "target_triple": "UNKNOWN_NOT_RECORDED", "environment_identity": "LOCAL_COORDINATOR_HOST_NOT_IMMUTABLE",
        "passing_result_claimed": False,
    },
    "scope": "REFERENCE_SOURCE_RECOVERY_AND_PARTIAL_EXECUTION_OBSERVATION_ONLY",
    "publishable": False, "qualified": False, "activation": "BLOCKED", "authority_effect": "NONE",
}


def git_object_exists(spec: str) -> bool:
    return subprocess.run(["git", "cat-file", "-e", spec], cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0


def validate_historical_build() -> None:
    if run("git", "rev-parse", f"{SAMPLE_HEAD}^{{tree}}").decode().strip() != SAMPLE_TREE:
        fail("historical sample tree drift")
    if sha256(run("git", "archive", "--format=tar", SAMPLE_HEAD)) != SAMPLE_ARCHIVE_SHA256:
        fail("historical sample archive digest drift")
    if sha256(repository_file("docs/archive/placeholder/V1_SAMPLE_MANIFEST.sha256").read_bytes()) != SAMPLE_MANIFEST_SHA256:
        fail("historical sample manifest digest drift")
    if "Cargo.lock" in tree_paths(SAMPLE_HEAD) or git_object_exists(f"{SAMPLE_HEAD}:Cargo.lock"):
        fail("historical sample unexpectedly acquired Cargo.lock")
    historical_objects = {"Cargo.toml": SAMPLE_ROOT_CARGO_SHA256, "crates/steamcloud-agent/Cargo.toml": SAMPLE_CRATE_CARGO_SHA256, ".github/workflows/ci.yml": SAMPLE_WORKFLOW_SHA256}
    for path, digest in historical_objects.items():
        if sha256(run("git", "show", f"{SAMPLE_HEAD}:{path}")) != digest:
            fail(f"historical build input drift: {path}")
    assert_exact(load_json(PHASE / "historical-build-evidence.v1.json"), EXPECTED_HISTORICAL_EVIDENCE)
    note = repository_file("docs/archive/HISTORICAL_BUILD.md").read_text(encoding="utf-8")
    for value in (SAMPLE_HEAD, SAMPLE_TREE, SAMPLE_ARCHIVE_SHA256, SAMPLE_MANIFEST_SHA256, "no `Cargo.lock`", "`stable`", "NOT_REPRODUCIBLE_STRUCTURALLY_UNPINNED", "No passing Rust result is claimed"):
        if value not in note:
            fail(f"historical build note omits fail-closed evidence: {value}")


EXPECTED_ISSUE_FORM = {
    "name": "Archive record correction",
    "description": "Report a broken historical link, provenance error, or archive-safety issue. Feature and runtime requests are not accepted.",
    "title": "[archive] ", "labels": [], "assignees": [],
    "body": [
        {"type": "dropdown", "id": "record_type", "attributes": {"label": "Record type", "options": ["Broken documentation link", "Historical provenance correction", "Archive-safety issue"]}, "validations": {"required": True}},
        {"type": "input", "id": "identity", "attributes": {"label": "Exact historical identity", "description": "Provide the commit, tree, path, or manifest line. Do not include a credential, token, production datum, or private history.", "placeholder": "commit/path or manifest identity"}, "validations": {"required": True}},
        {"type": "textarea", "id": "evidence", "attributes": {"label": "Evidence and reproduction", "description": "Explain the correction and give bounded, read-only reproduction steps. Do not propose runtime or feature work."}, "validations": {"required": True}},
        {"type": "checkboxes", "id": "attestations", "attributes": {"label": "Archive boundary", "options": [
            {"label": "This report is limited to historical accuracy, documentation links, provenance, or archive safety.", "required": True},
            {"label": "I have not included secrets, credentials, personal data, private source, or production data.", "required": True},
            {"label": "I understand this archive does not accept feature, runtime, package, deployment, or authority requests.", "required": True},
        ]}},
    ],
}
EXPECTED_ISSUE_CONFIG = {"blank_issues_enabled": False, "contact_links": []}


def validate_issue_form_document(form: dict[str, object], config: dict[str, object]) -> None:
    assert_exact(form, EXPECTED_ISSUE_FORM, "$.issue_form")
    assert_exact(config, EXPECTED_ISSUE_CONFIG, "$.issue_config")


def validate_issue_form() -> None:
    validate_issue_form_document(load_yaml(ROOT / ".github/ISSUE_TEMPLATE/archive-record.yml"), load_yaml(ROOT / ".github/ISSUE_TEMPLATE/config.yml"))


EXPECTED_WORKFLOW_COMMANDS = [
    None,
    "python3 -m pip install --disable-pip-version-check markdown-it-py==3.0.0 mdurl==0.1.2 PyYAML==6.0.3",
    "python3 scripts/validate_placeholder.py\npython3 scripts/test_validate_placeholder.py\n",
    "phase00_worktree=\"$(mktemp -d /tmp/steamcloud-archive-phase00.XXXXXX)\"\ntrap 'git worktree remove --force \"$phase00_worktree\" 2>/dev/null || true' EXIT\ngit worktree add --detach \"$phase00_worktree\" 9554180db2b73b426a87128e10fbe12c097ee786\n(\n  cd \"$phase00_worktree\"\n  python3 scripts/validate_placeholder.py\n  python3 scripts/test_validate_placeholder.py\n  python3 phase-00/validate.py\n  python3 phase-00/test_validate.py\n)\ngit worktree remove --force \"$phase00_worktree\"\ntrap - EXIT\n",
    "phase01_worktree=\"$(mktemp -d /tmp/steamcloud-archive-phase01.XXXXXX)\"\ntrap 'git worktree remove --force \"$phase01_worktree\" 2>/dev/null || true' EXIT\ngit worktree add --detach \"$phase01_worktree\" 4ec31555d6b94d5f2a51638c37be11575d3a1740\n(\n  cd \"$phase01_worktree\"\n  python3 phase-01/validate.py\n  python3 phase-01/test_validate.py\n)\ngit worktree remove --force \"$phase01_worktree\"\ntrap - EXIT\n",
    "git diff --check HEAD^ HEAD",
    "git fsck --full",
]
EXPECTED_WORKFLOW_STEP_NAMES = {
    2: "Verify the integrated historical archive",
    3: "Verify the exact Phase 00 candidate",
    4: "Verify the exact historical Phase 01 seal",
}


def validate_workflow_document(workflow: dict[str, object], raw: str) -> None:
    if set(workflow) != {"name", "on", "permissions", "jobs"}:
        fail("workflow root field drift")
    assert_exact(workflow["name"], "placeholder-archive-validation", "$.workflow.name")
    assert_exact(workflow["on"], {"push": None, "pull_request": None}, "$.workflow.on")
    assert_exact(workflow["permissions"], {"contents": "read"}, "$.workflow.permissions")
    jobs = workflow["jobs"]
    if not isinstance(jobs, dict) or set(jobs) != {"validate"}:
        fail("archive must retain one validation-only job")
    job = jobs["validate"]
    if not isinstance(job, dict) or set(job) != {"runs-on", "steps"} or job["runs-on"] != "ubuntu-latest":
        fail("workflow validation job shape drift")
    steps = job["steps"]
    if not isinstance(steps, list) or len(steps) != 7:
        fail("workflow step boundary drift")
    assert_exact(steps[0], {"uses": "actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683", "with": {"fetch-depth": 0, "persist-credentials": False}}, "$.workflow.jobs.validate.steps[0]")
    for index, expected_command in enumerate(EXPECTED_WORKFLOW_COMMANDS[1:], start=1):
        step = steps[index]
        if not isinstance(step, dict) or set(step) not in ({"run"}, {"name", "run"}):
            fail(f"workflow step {index} shape drift")
        if step.get("run") != expected_command:
            fail(f"workflow step {index} command drift")
        if index in EXPECTED_WORKFLOW_STEP_NAMES and step.get("name") != EXPECTED_WORKFLOW_STEP_NAMES[index]:
            fail(f"workflow step {index} name drift")
        if index not in EXPECTED_WORKFLOW_STEP_NAMES and "name" in step:
            fail(f"unexpected workflow step name at {index}")
    folded = raw.casefold()
    for forbidden in ("curl ", "wget ", "gh api", "secrets.", "contents: write", "id-token: write"):
        if forbidden in folded:
            fail(f"mutable or secret-bearing workflow token: {forbidden}")


def validate_workflow() -> None:
    path = ROOT / ".github/workflows/ci.yml"
    raw = path.read_text(encoding="utf-8")
    validate_workflow_document(load_yaml_text(raw), raw)


EXPECTED_STATUS = {
    "schema": "steamcloud.archive.phase-01-status/v1", "architecture_binding": ARCHITECTURE,
    "repository": REPOSITORY, "phase": "01", "phase_disposition": "IMPLEMENTED_NOT_QUALIFIED",
    "canonical_capability_status": "UNKNOWN", "archive_artifact_status": "REFERENCE",
    "deployment": "BLOCKED_NOT_AUTHORIZED_NOT_PERFORMED", "activation": "BLOCKED",
    "qualification": "NOT_OBSERVED_NOT_ESTABLISHED", "accepts_feature_work": False,
    "runtime_dependencies": [], "active_consumers_observed": [], "active_dependency_inventory_complete": False,
    "data_collection": {"identity": "none", "classification": "none", "retention": "none", "residency": "none", "erasure": "not-applicable", "export": "not-applicable", "restore": "not-applicable"},
    "limits": {"max_markdown_files": 128, "max_markdown_bytes_each": 1_048_576, "external_fetches": 0, "writes": 0, "effects": 0},
    "work_items": STATUS_WORK_ITEMS, "authority_movement": AUTHORITY_NONE, "review_gate": REVIEW_GATE,
}


def validate_status_document(status: dict[str, object]) -> None:
    assert_exact(status, EXPECTED_STATUS, "$.status")


def validate_status() -> None:
    validate_status_document(load_json(PHASE / "status.v1.json"))


POSITIVE_CORPUS = [
    {"id": "ARCHIVE-P1-P01", "test": "test_current_link_inventory_is_exact", "expected": "PASS"},
    {"id": "ARCHIVE-P1-P02", "test": "test_reference_style_local_link_is_checked", "expected": "PASS"},
    {"id": "ARCHIVE-P1-P03", "test": "test_html_local_link_is_checked", "expected": "PASS"},
    {"id": "ARCHIVE-P1-P04", "test": "test_code_spans_and_fences_are_ignored", "expected": "PASS"},
    {"id": "ARCHIVE-P1-P05", "test": "test_historical_evidence_is_exact_and_fail_closed", "expected": "PASS"},
    {"id": "ARCHIVE-P1-P06", "test": "test_issue_form_is_exact_archive_scope", "expected": "PASS"},
    {"id": "ARCHIVE-P1-P07", "test": "test_exact_phase00_boundary_is_preserved", "expected": "PASS"},
    {"id": "ARCHIVE-P1-P08", "test": "test_nested_bracket_inline_link_is_checked", "expected": "PASS"},
    {"id": "ARCHIVE-P1-P09", "test": "test_escaped_bracket_inline_link_is_checked", "expected": "PASS"},
    {"id": "ARCHIVE-P1-P10", "test": "test_nested_bracket_image_link_is_checked", "expected": "PASS"},
    {"id": "ARCHIVE-P1-P11", "test": "test_nested_image_inside_link_inventories_both", "expected": "PASS"},
    {"id": "ARCHIVE-P1-P12", "test": "test_recursive_image_children_inventory_every_active_destination", "expected": "PASS"},
    {"id": "ARCHIVE-P1-P13", "test": "test_inner_link_inside_nonlink_outer_uses_commonmark_precedence", "expected": "PASS"},
    {"id": "ARCHIVE-P1-P14", "test": "test_quoted_titles_with_unbalanced_parentheses_are_valid", "expected": "PASS"},
    {"id": "ARCHIVE-P1-P15", "test": "test_angle_and_parenthesized_titles_are_valid", "expected": "PASS"},
    {"id": "ARCHIVE-P1-P16", "test": "test_reference_variants_inventory_each_active_use", "expected": "PASS"},
    {"id": "ARCHIVE-P1-P17", "test": "test_duplicate_destinations_preserve_occurrence_and_line_identity", "expected": "PASS"},
    {"id": "ARCHIVE-P1-P18", "test": "test_autolink_inline_html_and_markdown_boundaries_are_exact", "expected": "PASS"},
    {"id": "ARCHIVE-P1-P19", "test": "test_raw_html_blocks_do_not_activate_markdown_syntax", "expected": "PASS"},
    {"id": "ARCHIVE-P1-P20", "test": "test_inline_raw_html_special_forms_do_not_hide_or_invent_links", "expected": "PASS"},
    {"id": "ARCHIVE-P1-P21", "test": "test_parser_dependency_identity_is_exact", "expected": "PASS"},
    {"id": "ARCHIVE-P1-P22", "test": "test_container_reference_existing_matrix_and_source_spans", "expected": "PASS"},
    {"id": "ARCHIVE-P1-P23", "test": "test_container_reference_multiline_titles_and_escapes_are_valid", "expected": "PASS"},
    {"id": "ARCHIVE-P1-P24", "test": "test_reference_definition_order_and_multiplicity_are_exact", "expected": "PASS"},
]
NEGATIVE_CORPUS = [
    {"id": "ARCHIVE-P1-N01", "test": "test_missing_inline_link_is_rejected", "expected": "REJECT"},
    {"id": "ARCHIVE-P1-N02", "test": "test_missing_reference_link_is_rejected", "expected": "REJECT"},
    {"id": "ARCHIVE-P1-N03", "test": "test_missing_html_link_is_rejected", "expected": "REJECT"},
    {"id": "ARCHIVE-P1-N04", "test": "test_missing_heading_fragment_is_rejected", "expected": "REJECT"},
    {"id": "ARCHIVE-P1-N05", "test": "test_unsafe_local_link_variants_are_rejected", "expected": "REJECT"},
    {"id": "ARCHIVE-P1-N06", "test": "test_symlink_link_target_is_rejected", "expected": "REJECT"},
    {"id": "ARCHIVE-P1-N07", "test": "test_duplicate_json_key_is_rejected", "expected": "REJECT"},
    {"id": "ARCHIVE-P1-N08", "test": "test_nonfinite_json_number_is_rejected", "expected": "REJECT"},
    {"id": "ARCHIVE-P1-N09", "test": "test_status_deployment_inflation_is_rejected", "expected": "REJECT"},
    {"id": "ARCHIVE-P1-N10", "test": "test_status_activation_inflation_is_rejected", "expected": "REJECT"},
    {"id": "ARCHIVE-P1-N11", "test": "test_status_authority_and_qualification_inflation_is_rejected", "expected": "REJECT"},
    {"id": "ARCHIVE-P1-N12", "test": "test_manifest_signed_publishable_inflation_is_rejected", "expected": "REJECT"},
    {"id": "ARCHIVE-P1-N13", "test": "test_manifest_source_identity_drift_is_rejected", "expected": "REJECT"},
    {"id": "ARCHIVE-P1-N14", "test": "test_manifest_absolute_and_traversal_paths_are_rejected", "expected": "REJECT"},
    {"id": "ARCHIVE-P1-N15", "test": "test_manifest_symlink_path_is_rejected", "expected": "REJECT"},
    {"id": "ARCHIVE-P1-N16", "test": "test_issue_form_feature_option_is_rejected", "expected": "REJECT"},
    {"id": "ARCHIVE-P1-N17", "test": "test_issue_form_optional_attestation_is_rejected", "expected": "REJECT"},
    {"id": "ARCHIVE-P1-N18", "test": "test_runtime_or_package_path_addition_is_rejected", "expected": "REJECT"},
    {"id": "ARCHIVE-P1-N19", "test": "test_workflow_write_permission_is_rejected", "expected": "REJECT"},
    {"id": "ARCHIVE-P1-N20", "test": "test_duplicate_yaml_key_is_rejected", "expected": "REJECT"},
    {"id": "ARCHIVE-P1-N21", "test": "test_closeout_activation_authority_mutation_is_rejected", "expected": "REJECT"},
    {"id": "ARCHIVE-P1-N22", "test": "test_fault_corpus_label_drift_is_rejected", "expected": "REJECT"},
    {"id": "ARCHIVE-P1-N23", "test": "test_nested_bracket_missing_link_is_rejected", "expected": "REJECT"},
    {"id": "ARCHIVE-P1-N24", "test": "test_escaped_bracket_missing_link_is_rejected", "expected": "REJECT"},
    {"id": "ARCHIVE-P1-N25", "test": "test_nested_bracket_traversal_is_rejected", "expected": "REJECT"},
    {"id": "ARCHIVE-P1-N26", "test": "test_escaped_bracket_traversal_is_rejected", "expected": "REJECT"},
    {"id": "ARCHIVE-P1-N27", "test": "test_multiline_inline_link_is_typed_rejection", "expected": "REJECT"},
    {"id": "ARCHIVE-P1-N28", "test": "test_link_bracket_depth_limit_is_typed_rejection", "expected": "REJECT"},
    {"id": "ARCHIVE-P1-N29", "test": "test_unterminated_inline_destination_is_typed_rejection", "expected": "REJECT"},
    {"id": "ARCHIVE-P1-N30", "test": "test_closeout_nonclaims_replacement_is_rejected", "expected": "REJECT"},
    {"id": "ARCHIVE-P1-N31", "test": "test_closeout_known_limitations_replacement_is_rejected", "expected": "REJECT"},
    {"id": "ARCHIVE-P1-N32", "test": "test_closeout_command_result_replacement_is_rejected", "expected": "REJECT"},
    {"id": "ARCHIVE-P1-N33", "test": "test_closeout_blocker_replacement_is_rejected", "expected": "REJECT"},
    {"id": "ARCHIVE-P1-N34", "test": "test_closeout_rollback_permutation_is_rejected", "expected": "REJECT"},
    {"id": "ARCHIVE-P1-N35", "test": "test_closeout_rollback_omission_is_rejected", "expected": "REJECT"},
    {"id": "ARCHIVE-P1-N36", "test": "test_closeout_rollback_fake_identity_is_rejected", "expected": "REJECT"},
    {"id": "ARCHIVE-P1-N37", "test": "test_closeout_rollback_target_drift_is_rejected", "expected": "REJECT"},
    {"id": "ARCHIVE-P1-N38", "test": "test_closeout_semantic_negation_variants_are_rejected", "expected": "REJECT"},
    {"id": "ARCHIVE-P1-N39", "test": "test_closeout_unblocks_inflation_is_rejected", "expected": "REJECT"},
    {"id": "ARCHIVE-P1-N40", "test": "test_nested_image_inside_link_missing_inner_is_rejected", "expected": "REJECT"},
    {"id": "ARCHIVE-P1-N41", "test": "test_inner_link_inside_nonlink_outer_missing_is_rejected", "expected": "REJECT"},
    {"id": "ARCHIVE-P1-N42", "test": "test_unterminated_angle_destinations_are_typed_rejections", "expected": "REJECT"},
    {"id": "ARCHIVE-P1-N43", "test": "test_malformed_angle_destination_is_typed_rejection", "expected": "REJECT"},
    {"id": "ARCHIVE-P1-N44", "test": "test_unterminated_quoted_titles_are_typed_rejections", "expected": "REJECT"},
    {"id": "ARCHIVE-P1-N45", "test": "test_unterminated_parenthesized_title_is_typed_rejection", "expected": "REJECT"},
    {"id": "ARCHIVE-P1-N46", "test": "test_malformed_inline_title_and_tail_are_typed_rejections", "expected": "REJECT"},
    {"id": "ARCHIVE-P1-N47", "test": "test_multiline_title_is_typed_rejection", "expected": "REJECT"},
    {"id": "ARCHIVE-P1-N48", "test": "test_destination_depth_and_size_limits_are_typed", "expected": "REJECT"},
    {"id": "ARCHIVE-P1-N49", "test": "test_reference_definition_malformed_forms_are_typed", "expected": "REJECT"},
    {"id": "ARCHIVE-P1-N50", "test": "test_duplicate_reference_definitions_are_typed_rejection", "expected": "REJECT"},
    {"id": "ARCHIVE-P1-N51", "test": "test_nested_active_traversal_and_query_vectors_are_rejected", "expected": "REJECT"},
    {"id": "ARCHIVE-P1-N52", "test": "test_inline_html_wrapping_missing_markdown_is_rejected", "expected": "REJECT"},
    {"id": "ARCHIVE-P1-N53", "test": "test_r10_exact_container_unterminated_angle_fixtures_are_typed", "expected": "REJECT"},
    {"id": "ARCHIVE-P1-N54", "test": "test_r10_exact_container_unterminated_title_fixtures_are_typed", "expected": "REJECT"},
    {"id": "ARCHIVE-P1-N55", "test": "test_r10_exact_container_duplicate_fixtures_are_typed", "expected": "REJECT"},
    {"id": "ARCHIVE-P1-N56", "test": "test_container_reference_missing_and_unsafe_destinations_are_rejected", "expected": "REJECT"},
    {"id": "ARCHIVE-P1-N57", "test": "test_container_reference_malformed_depth_and_size_forms_are_typed", "expected": "REJECT"},
    {"id": "ARCHIVE-P1-N58", "test": "test_cross_container_duplicate_definition_is_typed_rejection", "expected": "REJECT"},
]
EXPECTED_CORPUS = {
    "schema": "steamcloud.archive.phase-01-test-fault-corpus/v2", "architecture_binding": ARCHITECTURE,
    "seed": "5eed0001", "runner": "python3 phase-01/test_validate.py",
    "positive_cases": POSITIVE_CORPUS, "negative_cases": NEGATIVE_CORPUS,
    "durable_state": {"writes": 0, "effects": 0, "idempotency": "pure-offline-validation-is-repeatable", "duplicates": "duplicate-json-yaml-manifest-and-html-keys-rejected", "crash": "not-applicable-no-durable-write", "lost_response": "not-applicable-no-external-call", "restore": "revert-phase01-commits-newest-first-to-exact-phase00-tree", "rollback": "source-only-newest-first"},
    "qualification_non_claim": "Executable archive-boundary regressions only; not security, restore, deployment, runtime, qualification, or authority evidence.",
}


def validate_corpus_document(corpus: dict[str, object]) -> None:
    assert_exact(corpus, EXPECTED_CORPUS, "$.fault_corpus")
    ids = [item["id"] for item in POSITIVE_CORPUS + NEGATIVE_CORPUS]
    tests = [item["test"] for item in POSITIVE_CORPUS + NEGATIVE_CORPUS]
    if len(ids) != len(set(ids)) or len(tests) != len(set(tests)):
        fail("fault corpus ids and executable test identities must be unique")


def validate_corpus() -> None:
    validate_corpus_document(load_json(PHASE / "test-fault-corpus.v1.json"))


MANIFEST_ROOT_KEYS = {"schema", "architecture_binding", "repository", "phase", "source_head", "source_tree", "source_commit", "signed", "publishable", "entries", "non_claim"}


def validate_manifest_document(manifest: dict[str, object], *, verify_files: bool = True) -> None:
    if set(manifest) != MANIFEST_ROOT_KEYS:
        fail("manifest root field drift")
    constants = {
        "schema": "steamcloud.archive.phase-01-artifact-manifest/v2", "architecture_binding": ARCHITECTURE,
        "repository": REPOSITORY, "phase": "01", "source_head": PHASE00_HEAD, "signed": False,
        "publishable": False,
        "non_claim": "Unsigned repository-contained source manifest only; not release, deployment, qualification, observed-live, activation, or authority evidence.",
    }
    for key, expected in constants.items():
        assert_exact(manifest[key], expected, f"$.manifest.{key}")
    source_commit = manifest["source_commit"]
    source_tree = manifest["source_tree"]
    if type(source_commit) is not str or not SHA1.fullmatch(source_commit):
        fail("manifest source commit malformed")
    if type(source_tree) is not str or not SHA1.fullmatch(source_tree):
        fail("manifest source tree malformed")
    if source_commit != candidate_source_commit():
        fail("manifest source commit is not exact candidate source parent")
    if run("git", "rev-parse", f"{source_commit}^{{tree}}").decode().strip() != source_tree:
        fail("manifest source tree does not match source commit")
    entries = manifest["entries"]
    if not isinstance(entries, list):
        fail("manifest entries must be an array")
    paths: set[str] = set()
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict) or set(entry) != {"path", "sha256"}:
            fail(f"manifest entry {index} shape drift")
        path = entry["path"]
        digest = entry["sha256"]
        if type(path) is not str or type(digest) is not str or not SHA256.fullmatch(digest):
            fail(f"manifest entry {index} identity malformed")
        target = repository_file(path, must_exist=verify_files)
        if path in paths:
            fail(f"duplicate manifest path: {path}")
        paths.add(path)
        if verify_files:
            source_bytes = run("git", "show", f"{source_commit}:{path}")
            if sha256(source_bytes) != digest:
                fail(f"manifest source digest drift: {path}")
    if paths != SOURCE_ENTRY_PATHS:
        fail(f"manifest exact source entry boundary drift: missing={sorted(SOURCE_ENTRY_PATHS - paths)} extra={sorted(paths - SOURCE_ENTRY_PATHS)}")
    if [entry["path"] for entry in entries] != sorted(paths):
        fail("manifest entries must be lexically ordered")


CLOSEOUT_ROOT_KEYS = {"schema", "architecture_version", "repository", "phase", "source_head", "source_tree", "change_commits", "commands", "command_evidence_classification", "artifacts", "capability_status", "known_limitations", "rollback", "non_claims", "unresolved_blockers", "unblocks", "work_items", "authority_movement", "review_gate"}
EXPECTED_ARTIFACT_PATHS = {"phase-01/artifact-manifest.v1.json", "phase-01/status.v1.json", "phase-01/test-fault-corpus.v1.json", "phase-01/historical-build-evidence.v1.json", "docs/archive/HISTORICAL_BUILD.md", ".github/ISSUE_TEMPLATE/archive-record.yml"}

EXPECTED_COMMAND_ROWS = [
    {
        "command": "git fetch --prune origin",
        "exit_code": 0,
        "result": "PASS; refreshed main remained f395c6c922124c716d216d80fee42dba7d3547d2 and Phase 00 candidate remained 9554180db2b73b426a87128e10fbe12c097ee786",
    },
    {
        "command": "read-only GitHub release, deployment, secret-count, and variable-count metadata",
        "exit_code": 0,
        "result": "OBSERVED: releases 0, deployments 0, repository Actions secret metadata count 0, variable metadata count 0; scoped metadata only, not provider, administrator, secret-custodian, or organization-wide absence evidence",
    },
    {
        "command": "python3 phase-01/validate.py --preseal",
        "exit_code": 0,
        "result": "PASS; exact 26-occurrence pinned CommonMark inventory plus parser-position-backed container definition order, source spans, duplicates, and typed malformed-syntax rejection; exact source recovery; Rust unpinned/no pass claimed; closed issue/status/corpus/narrative gates; exact Phase 00 bytes; activation blocked; authority none",
    },
    {
        "command": "exact detached Phase 00 validation at " + PHASE00_HEAD,
        "exit_code": 0,
        "result": "PASS; original placeholder validator and 23 tests plus Phase 00 validator and eight tests",
    },
    {
        "command": "npm test --prefix <exact historical sample temp directory>",
        "exit_code": 0,
        "result": "OBSERVED PASS; exact sample commit 069c2448ee3c5e7c352d096494d15e8f120cf433 executed 20 Node tests under Node v22.18.0; not cross-toolchain qualification",
    },
    {
        "command": "npm run check --prefix <exact historical sample temp directory>",
        "exit_code": 0,
        "result": "OBSERVED PASS; JavaScript syntax and historical repository validator under Node v22.18.0; bounded observation only",
    },
    {
        "command": "cargo test --manifest-path <exact historical sample temp directory>/Cargo.toml --workspace --all-targets --offline",
        "exit_code": 101,
        "result": "BLOCKED; the historical tree has no Cargo.lock, uses moving stable and broad dependency constraints, selected eight latest-compatible packages, and the host lacks cc. No passing Rust result is claimed; status is NOT_REPRODUCIBLE_STRUCTURALLY_UNPINNED.",
    },
    {
        "command": "python3 phase-01/validate.py; python3 phase-01/test_validate.py; git diff --check",
        "exit_code": 0,
        "result": "PASS after exact source manifest and closeout seal; 82 retained tests execute all 24 positive and 58 negative corpus identities",
    },
]

EXPECTED_KNOWN_LIMITATIONS = [
    "The GitHub Archived setting remains observed false and this implementation-only phase does not authorize changing it.",
    "The default branch and open Phase 00 candidate are unprotected and no controlled-merge equivalent or signed provenance is evidenced.",
    "The historical freeze tag, source manifest, build evidence, and closeout are unsigned and are not release or qualification evidence.",
    "Repository-local content has no runtime dependency and no active consumer was observed, but no signed complete portfolio consumer inventory exists.",
    "Only exact historical source recovery is reproducible; Node execution is a bounded observation and Rust is NOT_REPRODUCIBLE_STRUCTURALLY_UNPINNED with no passing result.",
    "Findings ARCHIVE-P1-R01 through ARCHIVE-P1-R10 are source-remediated, but the new exact head still requires a fresh independent review and no signed accountable reviewer acceptance is observed.",
    "No signed secret-history review spans deleted history, forks, caches, provider state, or inaccessible scopes.",
    "No observation window binds an accepted archive release, restore, settings state, and accountable owner identities.",
]

EXPECTED_NON_CLAIMS = [
    "No feature, runtime, schema, contract, package, profile, provider adapter, deployment configuration, active dependency, telemetry, data collection, write, effect, or authority role was added.",
    "No repository setting, visibility, archive flag, branch protection, ruleset, release, tag, deployment, environment, provider, DNS, secret, credential, traffic, or authority was changed.",
    "Scoped GitHub metadata observations do not prove provider, administrator, organization-wide, deleted-history, fork, cache, or inaccessible-scope absence.",
    "The historical sample remains reference material. Exact source identities and bounded Node observations do not make it a current protocol, package, runtime, reproducible Rust build, or qualified capability.",
    "The issue template is archive intake only and does not authorize an administrator, security, feature, deployment, product, or CurrentAuthority action.",
    "No merge, signed release, independent qualification, live observation, activation, retirement, or CurrentAuthority transition occurred.",
]

EXPECTED_BLOCKERS = [
    {
        "blocker": "Protected main or an evidenced equivalent controlled-merge policy and signed provenance are absent.",
        "owner": "repository source-governance, release-root, signer-set, provenance, and rollback owners; exact signed identities NOT_OBSERVED",
    },
    {
        "blocker": "GitHub Archived remains false and this phase has no administrator authorization to change it.",
        "owner": "repository administrator and archive-disposition owner; exact signed identities NOT_OBSERVED",
    },
    {
        "blocker": "A complete signed inventory proving no active dependency or consumer points to the archive is absent.",
        "owner": "SteamCloud product, portfolio dependency-inventory, package, documentation, and migration owners; exact signed identities NOT_OBSERVED",
    },
    {
        "blocker": "Independent restore, history/secret review, new exact-head source-boundary acceptance, and rollback acceptance are absent.",
        "owner": "archive rollback, secret-custody, security, and independent-review owners; exact signed identities NOT_OBSERVED",
    },
    {
        "blocker": "No signed immutable archive release/tag or observation window is bound to exact settings, source, and owner identities.",
        "owner": "archive release signer, observation, qualification, and owner authorities; exact signed identities NOT_OBSERVED",
    },
]

EXPECTED_UNBLOCKS = [
    "Fresh technical review of exact archive links, historical source recovery, provenance correction intake, fail-closed limitations, and exact source rollback.",
    "Archive-safety and documentation corrections that remain within the same exact no-runtime boundary.",
    "No feature, runtime, package, schema, deployment, setting, activation, qualification, retirement, or authority action is unblocked.",
]


def expected_rollback(source_commit: str, source_tree: str) -> dict[str, object]:
    return {
        "strategy": "GIT_REVERT_SOURCE_ONLY_NEWEST_FIRST",
        "revert_order": [
            {
                "ordinal": 1,
                "identity": "CURRENT_CANDIDATE_HEAD",
                "resolution": "VALIDATOR_RESOLVES_EXACT_CURRENT_CANDIDATE_COMMIT",
                "required_parent": source_commit,
                "expected_tree_after": source_tree,
            },
            {
                "ordinal": 2,
                "identity": source_commit,
                "expected_tree_after": PREVIOUS_COMMONMARK_REMEDIATION_SEAL_TREE,
            },
            {
                "ordinal": 3,
                "identity": PREVIOUS_COMMONMARK_REMEDIATION_SEAL,
                "expected_tree_after": PREVIOUS_COMMONMARK_REMEDIATION_TREE,
            },
            {
                "ordinal": 4,
                "identity": PREVIOUS_COMMONMARK_REMEDIATION,
                "expected_tree_after": PREVIOUS_RESIDUAL_REMEDIATION_SEAL_TREE,
            },
            {
                "ordinal": 5,
                "identity": PREVIOUS_RESIDUAL_REMEDIATION_SEAL,
                "expected_tree_after": PREVIOUS_RESIDUAL_REMEDIATION_TREE,
            },
            {
                "ordinal": 6,
                "identity": PREVIOUS_RESIDUAL_REMEDIATION,
                "expected_tree_after": PREVIOUS_REMEDIATION_SEAL_TREE,
            },
            {
                "ordinal": 7,
                "identity": PREVIOUS_REMEDIATION_SEAL,
                "expected_tree_after": PREVIOUS_REMEDIATION_TREE,
            },
            {
                "ordinal": 8,
                "identity": PREVIOUS_REMEDIATION,
                "expected_tree_after": PREVIOUS_SEAL_TREE,
            },
            {
                "ordinal": 9,
                "identity": PREVIOUS_SEAL,
                "expected_tree_after": PREVIOUS_IMPLEMENTATION_TREE,
            },
            {
                "ordinal": 10,
                "identity": PREVIOUS_IMPLEMENTATION,
                "expected_tree_after": PHASE00_TREE,
            },
        ],
        "target": {
            "head": PHASE00_HEAD,
            "tree": PHASE00_TREE,
            "phase01_path_count": 0,
            "required_validation": "ORIGINAL_23_PLUS_PHASE00_8_TESTS",
        },
        "external_reconciliation": "NONE_NO_RUNTIME_DEPLOYMENT_DURABLE_STATE_OR_AUTHORITY_EFFECT",
    }


def validate_closeout_document(closeout: dict[str, object], manifest: dict[str, object], *, verify_files: bool = True) -> None:
    if set(closeout) != CLOSEOUT_ROOT_KEYS:
        fail("closeout root field drift")
    constants = {
        "schema": "solarflare.repository-phase-closeout/v3", "architecture_version": ARCHITECTURE,
        "repository": REPOSITORY, "phase": "01", "source_head": PHASE00_HEAD, "source_tree": PHASE00_TREE,
        "command_evidence_classification": "NARRATIVE_ONLY_NOT_INDEPENDENT_EXECUTION_EVIDENCE",
        "capability_status": "IMPLEMENTED_NOT_QUALIFIED", "work_items": CLOSEOUT_WORK_ITEMS,
        "authority_movement": AUTHORITY_NONE, "review_gate": REVIEW_GATE,
    }
    for key, expected in constants.items():
        assert_exact(closeout[key], expected, f"$.closeout.{key}")
    source_commit = manifest["source_commit"]
    source_tree = manifest["source_tree"]
    if type(source_commit) is not str or type(source_tree) is not str:
        fail("closeout manifest source identity malformed")
    if run("git", "rev-parse", f"{source_commit}^").decode().strip() != PREVIOUS_COMMONMARK_REMEDIATION_SEAL:
        fail("R10 source commit does not descend from exact reviewed head")
    if run("git", "rev-parse", f"{candidate_head()}^").decode().strip() != source_commit:
        fail("current candidate seal does not have exact source parent")
    assert_exact(
        closeout["change_commits"],
        [
            source_commit,
            PREVIOUS_COMMONMARK_REMEDIATION_SEAL,
            PREVIOUS_COMMONMARK_REMEDIATION,
            PREVIOUS_RESIDUAL_REMEDIATION_SEAL,
            PREVIOUS_RESIDUAL_REMEDIATION,
            PREVIOUS_REMEDIATION_SEAL,
            PREVIOUS_REMEDIATION,
            PREVIOUS_SEAL,
            PREVIOUS_IMPLEMENTATION,
        ],
        "$.closeout.change_commits",
    )
    assert_exact(closeout["commands"], EXPECTED_COMMAND_ROWS, "$.closeout.commands")
    artifacts = closeout["artifacts"]
    if not isinstance(artifacts, list):
        fail("closeout artifacts must be an array")
    artifact_paths: set[str] = set()
    for index, artifact in enumerate(artifacts):
        if not isinstance(artifact, dict) or set(artifact) != {"path", "digest"}:
            fail(f"closeout artifact row {index} shape drift")
        path, digest = artifact["path"], artifact["digest"]
        if type(path) is not str or type(digest) is not str or not digest.startswith("sha256:"):
            fail(f"closeout artifact row {index} identity malformed")
        expected_digest = digest.removeprefix("sha256:")
        if not SHA256.fullmatch(expected_digest):
            fail(f"closeout artifact row {index} digest malformed")
        target = repository_file(path, must_exist=verify_files)
        if path in artifact_paths:
            fail(f"duplicate closeout artifact: {path}")
        artifact_paths.add(path)
        if verify_files and sha256(target.read_bytes()) != expected_digest:
            fail(f"closeout artifact digest drift: {path}")
    if artifact_paths != EXPECTED_ARTIFACT_PATHS:
        fail("closeout exact artifact set drift")
    if [artifact["path"] for artifact in artifacts] != sorted(artifact_paths):
        fail("closeout artifacts must be lexically ordered")
    assert_exact(
        closeout["known_limitations"],
        EXPECTED_KNOWN_LIMITATIONS,
        "$.closeout.known_limitations",
    )
    assert_exact(closeout["rollback"], expected_rollback(source_commit, source_tree), "$.closeout.rollback")
    assert_exact(closeout["non_claims"], EXPECTED_NON_CLAIMS, "$.closeout.non_claims")
    assert_exact(closeout["unresolved_blockers"], EXPECTED_BLOCKERS, "$.closeout.unresolved_blockers")
    assert_exact(closeout["unblocks"], EXPECTED_UNBLOCKS, "$.closeout.unblocks")


def validate_schema_document(schema: dict[str, object]) -> None:
    if set(schema) != {"$schema", "$id", "title", "type", "additionalProperties", "required", "properties"}:
        fail("local closeout schema root drift")
    if schema["type"] != "object" or schema["additionalProperties"] is not False:
        fail("local closeout schema is not closed")
    if schema["required"] != sorted(CLOSEOUT_ROOT_KEYS):
        fail("local closeout schema required-field drift")
    properties = schema["properties"]
    if not isinstance(properties, dict) or set(properties) != CLOSEOUT_ROOT_KEYS:
        fail("local closeout schema property drift")
    canonical = sha256(json.dumps(schema, sort_keys=True, separators=(",", ":")).encode())
    if canonical != EXPECTED_CLOSEOUT_SCHEMA_CANONICAL_SHA256:
        fail(f"local closeout schema semantic drift: {canonical}")


def validate_closeout(preseal: bool) -> None:
    if preseal:
        return
    manifest = load_json(PHASE / "artifact-manifest.v1.json")
    validate_manifest_document(manifest)
    closeout = load_json(PHASE / "closeout.v1.json")
    validate_closeout_document(closeout, manifest)
    validate_schema_document(load_json(PHASE / "repository-phase-closeout.schema.json"))
    sidecar = (PHASE / "closeout.sha256").read_text(encoding="utf-8").strip()
    expected = f"{sha256((PHASE / 'closeout.v1.json').read_bytes())}  phase-01/closeout.v1.json"
    if sidecar != expected:
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
    print(f"PASS: exact {link_count}-occurrence pinned CommonMark/HTML inventory; exact historical source; Rust structurally unpinned/no pass claimed; archive-only issue intake; executable fault corpus; Phase 00 bytes preserved; deployment/activation BLOCKED; authority NONE")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AssertionError, KeyError, OSError, RecursionError, TypeError, UnicodeError, ValueError, yaml.YAMLError, subprocess.CalledProcessError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
