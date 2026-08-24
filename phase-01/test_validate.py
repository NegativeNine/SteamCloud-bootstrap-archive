#!/usr/bin/env python3
"""Adversarial tests for Phase 01 archive validation."""

from __future__ import annotations

import copy
import importlib.util
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("validate.py")
SPEC = importlib.util.spec_from_file_location("archive_phase01_validate", MODULE_PATH)
assert SPEC and SPEC.loader
validate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validate)


class ArchivePhase01ValidationTests(unittest.TestCase):
    def test_current_links_and_fragments_resolve(self) -> None:
        self.assertGreater(validate.validate_links(), 20)

    def test_historical_commit_tree_archive_and_manifest_are_exact(self) -> None:
        validate.validate_historical_build()

    def test_unsafe_and_missing_links_fail_closed(self) -> None:
        source = validate.ROOT / "README.md"
        cases = (
            "../outside.md",
            "%2e%2e/outside.md",
            "/etc/passwd",
            "docs\\migration\\CLOSEOUT.md",
            "docs/migration/DOES_NOT_EXIST.md",
            "docs/migration/CLOSEOUT.md#does-not-exist",
            "//evil.example/path",
            "http://example.com",
            "docs/migration/CLOSEOUT.md?activate=true",
            "docs/migration/CLOSEOUT.md%00tail",
        )
        for destination in cases:
            with self.subTest(destination=destination):
                with self.assertRaises(AssertionError):
                    validate.validate_link_destination(source, destination)

    def test_duplicate_json_keys_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "duplicate.json"
            path.write_text('{"effect":"NONE","effect":"ACTIVATE"}\n', encoding="utf-8")
            with self.assertRaisesRegex(AssertionError, "duplicate JSON key"):
                validate.load_json(path)

    def test_issue_form_refuses_feature_and_runtime_work(self) -> None:
        form = validate.yaml.safe_load(
            (validate.ROOT / ".github/ISSUE_TEMPLATE/archive-record.yml").read_text()
        )
        config = validate.yaml.safe_load(
            (validate.ROOT / ".github/ISSUE_TEMPLATE/config.yml").read_text()
        )
        validate.validate_issue_form_document(form, config)
        mutated = copy.deepcopy(form)
        mutated["description"] = "Request a new runtime feature"
        with self.assertRaisesRegex(AssertionError, "admits feature/runtime work"):
            validate.validate_issue_form_document(mutated, config)

    def test_blank_issue_or_external_contact_drift_is_rejected(self) -> None:
        form = validate.yaml.safe_load(
            (validate.ROOT / ".github/ISSUE_TEMPLATE/archive-record.yml").read_text()
        )
        with self.assertRaisesRegex(AssertionError, "template configuration"):
            validate.validate_issue_form_document(
                form,
                {"blank_issues_enabled": True, "contact_links": []},
            )

    def test_status_is_closed_and_no_effect(self) -> None:
        validate.validate_status()

    def test_exact_phase00_boundary_is_preserved_preseal(self) -> None:
        validate.validate_source_boundary(preseal=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
