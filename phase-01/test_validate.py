#!/usr/bin/env python3
"""Executable adversarial corpus for Phase 01 archive validation."""

from __future__ import annotations

import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("validate.py")
SPEC = importlib.util.spec_from_file_location("archive_phase01_validate", MODULE_PATH)
assert SPEC and SPEC.loader
validate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validate)


def current_json(name: str) -> dict[str, object]:
    return validate.load_json(validate.PHASE / name)


class ArchivePhase01ValidationTests(unittest.TestCase):
    def validate_extracted(self, text: str) -> list[dict[str, str]]:
        source = validate.ROOT / "README.md"
        records = validate.extract_link_destinations(source, text)
        for record in records:
            validate.validate_link_destination(source, record["destination"])
        return records

    def test_current_link_inventory_is_exact(self) -> None:
        self.assertGreater(validate.validate_links(), 20)

    def test_reference_style_local_link_is_checked(self) -> None:
        records = self.validate_extracted(
            "See [the closeout][close].\n\n[close]: docs/migration/CLOSEOUT.md\n"
        )
        self.assertEqual(
            records,
            [{"syntax": "reference-definition", "destination": "docs/migration/CLOSEOUT.md"}],
        )

    def test_html_local_link_is_checked(self) -> None:
        records = self.validate_extracted(
            '<a href="docs/migration/CLOSEOUT.md">closeout</a>\n'
        )
        self.assertEqual(
            records,
            [{"syntax": "html", "destination": "docs/migration/CLOSEOUT.md"}],
        )

    def test_code_spans_and_fences_are_ignored(self) -> None:
        records = validate.extract_link_destinations(
            validate.ROOT / "README.md",
            "`[bad](missing.md)` and `<a href=\"missing.md\">bad</a>`\n"
            "```md\n[bad][ref]\n[ref]: missing.md\n<a href=\"missing.md\">bad</a>\n```\n",
        )
        self.assertEqual(records, [])

    def test_historical_evidence_is_exact_and_fail_closed(self) -> None:
        validate.validate_historical_build()

    def test_issue_form_is_exact_archive_scope(self) -> None:
        validate.validate_issue_form()

    def test_exact_phase00_boundary_is_preserved(self) -> None:
        validate.validate_source_boundary(False)

    def test_nested_bracket_inline_link_is_checked(self) -> None:
        records = self.validate_extracted(
            "[outer [inner]](docs/migration/CLOSEOUT.md)\n"
        )
        self.assertEqual(
            records,
            [{"syntax": "inline", "destination": "docs/migration/CLOSEOUT.md"}],
        )

    def test_escaped_bracket_inline_link_is_checked(self) -> None:
        records = self.validate_extracted(
            r"[outer \] bracket](docs/migration/CLOSEOUT.md)" + "\n"
        )
        self.assertEqual(
            records,
            [{"syntax": "inline", "destination": "docs/migration/CLOSEOUT.md"}],
        )

    def test_nested_bracket_image_link_is_checked(self) -> None:
        records = self.validate_extracted(
            "![outer [inner]](docs/migration/CLOSEOUT.md)\n"
        )
        self.assertEqual(
            records,
            [{"syntax": "inline", "destination": "docs/migration/CLOSEOUT.md"}],
        )

    def test_missing_inline_link_is_rejected(self) -> None:
        with self.assertRaisesRegex(AssertionError, "target missing"):
            self.validate_extracted("[broken](docs/migration/DOES_NOT_EXIST.md)\n")

    def test_missing_reference_link_is_rejected(self) -> None:
        with self.assertRaisesRegex(AssertionError, "target missing"):
            self.validate_extracted(
                "[broken][missing]\n\n[missing]: docs/migration/DOES_NOT_EXIST.md\n"
            )

    def test_missing_html_link_is_rejected(self) -> None:
        with self.assertRaisesRegex(AssertionError, "target missing"):
            self.validate_extracted(
                '<a href="docs/migration/DOES_NOT_EXIST.md">broken</a>\n'
            )

    def test_missing_heading_fragment_is_rejected(self) -> None:
        with self.assertRaisesRegex(AssertionError, "missing Markdown heading fragment"):
            validate.validate_link_destination(
                validate.ROOT / "README.md",
                "docs/migration/CLOSEOUT.md#does-not-exist",
            )

    def test_unsafe_local_link_variants_are_rejected(self) -> None:
        source = validate.ROOT / "README.md"
        cases = (
            "../outside.md",
            "%2e%2e/outside.md",
            "/etc/passwd",
            "docs\\migration\\CLOSEOUT.md",
            "//evil.example/path",
            "http://example.com",
            "docs/migration/CLOSEOUT.md?activate=true",
            "docs/migration/CLOSEOUT.md%00tail",
        )
        for destination in cases:
            with self.subTest(destination=destination):
                with self.assertRaises(AssertionError):
                    validate.validate_link_destination(source, destination)

    def test_symlink_link_target_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory(dir=validate.ROOT) as directory:
            root = Path(directory)
            source = root / "source.md"
            source.write_text("source\n", encoding="utf-8")
            (root / "linked.md").symlink_to(validate.ROOT / "README.md")
            with self.assertRaisesRegex(AssertionError, "symlinked"):
                validate.validate_link_destination(source, "linked.md")

    def test_duplicate_json_key_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "duplicate.json"
            path.write_text('{"effect":"NONE","effect":"ACTIVATE"}\n', encoding="utf-8")
            with self.assertRaisesRegex(AssertionError, "duplicate JSON key"):
                validate.load_json(path)

    def test_nonfinite_json_number_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            for value in ("NaN", "Infinity", "-Infinity"):
                path = Path(directory) / "nonfinite.json"
                path.write_text('{"effects":' + value + '}\n', encoding="utf-8")
                with self.subTest(value=value):
                    with self.assertRaisesRegex(AssertionError, "non-finite JSON"):
                        validate.load_json(path)

    def test_status_deployment_inflation_is_rejected(self) -> None:
        status = copy.deepcopy(current_json("status.v1.json"))
        status["deployment"] = "LIVE"
        with self.assertRaises(AssertionError):
            validate.validate_status_document(status)

    def test_status_activation_inflation_is_rejected(self) -> None:
        status = copy.deepcopy(current_json("status.v1.json"))
        status["activation"] = "ACTIVE"
        status["work_items"][3]["status"] = "ACTIVE"
        with self.assertRaises(AssertionError):
            validate.validate_status_document(status)

    def test_status_authority_and_qualification_inflation_is_rejected(self) -> None:
        status = copy.deepcopy(current_json("status.v1.json"))
        status["qualification"] = "QUALIFIED"
        status["authority_movement"] = {
            "authorized": True,
            "performed": True,
            "effect": "CURRENT_AUTHORITY",
        }
        with self.assertRaises(AssertionError):
            validate.validate_status_document(status)

    def test_manifest_signed_publishable_inflation_is_rejected(self) -> None:
        for key in ("signed", "publishable"):
            manifest = copy.deepcopy(current_json("artifact-manifest.v1.json"))
            manifest[key] = True
            with self.subTest(key=key):
                with self.assertRaises(AssertionError):
                    validate.validate_manifest_document(manifest, verify_files=False)

    def test_manifest_source_identity_drift_is_rejected(self) -> None:
        manifest = copy.deepcopy(current_json("artifact-manifest.v1.json"))
        manifest["source_commit"] = "0" * 40
        with self.assertRaisesRegex(AssertionError, "not exact candidate source parent"):
            validate.validate_manifest_document(manifest, verify_files=False)

    def test_manifest_absolute_and_traversal_paths_are_rejected(self) -> None:
        for path in ("/etc/hosts", "../outside", "phase-01/../README.md"):
            manifest = copy.deepcopy(current_json("artifact-manifest.v1.json"))
            manifest["entries"][0]["path"] = path
            with self.subTest(path=path):
                with self.assertRaisesRegex(AssertionError, "repository-relative path"):
                    validate.validate_manifest_document(manifest, verify_files=False)

    def test_manifest_symlink_path_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory(dir=validate.ROOT) as directory:
            root = Path(directory)
            link = root / "artifact"
            link.symlink_to(validate.ROOT / "README.md")
            manifest = copy.deepcopy(current_json("artifact-manifest.v1.json"))
            manifest["entries"][0]["path"] = link.relative_to(validate.ROOT).as_posix()
            with self.assertRaisesRegex(AssertionError, "symlink"):
                validate.validate_manifest_document(manifest, verify_files=False)

    def test_issue_form_feature_option_is_rejected(self) -> None:
        form = copy.deepcopy(validate.load_yaml(validate.ROOT / ".github/ISSUE_TEMPLATE/archive-record.yml"))
        config = validate.load_yaml(validate.ROOT / ".github/ISSUE_TEMPLATE/config.yml")
        form["body"][0]["attributes"]["options"].append("Feature request")
        with self.assertRaises(AssertionError):
            validate.validate_issue_form_document(form, config)

    def test_issue_form_optional_attestation_is_rejected(self) -> None:
        form = copy.deepcopy(validate.load_yaml(validate.ROOT / ".github/ISSUE_TEMPLATE/archive-record.yml"))
        config = validate.load_yaml(validate.ROOT / ".github/ISSUE_TEMPLATE/config.yml")
        form["body"][3]["attributes"]["options"][0]["required"] = False
        with self.assertRaises(AssertionError):
            validate.validate_issue_form_document(form, config)

    def test_runtime_or_package_path_addition_is_rejected(self) -> None:
        expected = validate.tree_paths(validate.PHASE00_HEAD) | validate.ALL_PHASE_PATHS
        actual = expected | {"src/runtime.py"}
        with self.assertRaisesRegex(AssertionError, "source boundary drift"):
            validate.validate_source_path_set(actual, expected)

    def test_workflow_write_permission_is_rejected(self) -> None:
        path = validate.ROOT / ".github/workflows/ci.yml"
        raw = path.read_text(encoding="utf-8")
        workflow = copy.deepcopy(validate.load_yaml_text(raw))
        workflow["permissions"] = {"contents": "write"}
        with self.assertRaises(AssertionError):
            validate.validate_workflow_document(workflow, raw)

    def test_duplicate_yaml_key_is_rejected(self) -> None:
        with self.assertRaisesRegex(AssertionError, "duplicate YAML key"):
            validate.load_yaml_text("name: archive\nname: feature\n")

    def test_closeout_activation_authority_mutation_is_rejected(self) -> None:
        closeout = copy.deepcopy(current_json("closeout.v1.json"))
        manifest = current_json("artifact-manifest.v1.json")
        closeout["work_items"][3]["status"] = "ACTIVE"
        closeout["authority_movement"] = {
            "authorized": True,
            "performed": True,
            "effect": "CURRENT_AUTHORITY",
        }
        with self.assertRaises(AssertionError):
            validate.validate_closeout_document(closeout, manifest, verify_files=False)

    def test_nested_bracket_missing_link_is_rejected(self) -> None:
        with self.assertRaisesRegex(AssertionError, "target missing"):
            self.validate_extracted(
                "[outer [inner]](docs/migration/DOES_NOT_EXIST.md)\n"
            )

    def test_escaped_bracket_missing_link_is_rejected(self) -> None:
        with self.assertRaisesRegex(AssertionError, "target missing"):
            self.validate_extracted(
                r"[outer \] bracket](docs/migration/DOES_NOT_EXIST.md)" + "\n"
            )

    def test_nested_bracket_traversal_is_rejected(self) -> None:
        with self.assertRaisesRegex(AssertionError, "escapes repository"):
            self.validate_extracted("[outer [inner]](../outside.md)\n")

    def test_escaped_bracket_traversal_is_rejected(self) -> None:
        with self.assertRaisesRegex(AssertionError, "encoded traversal"):
            self.validate_extracted(r"[outer \] bracket](%2e%2e/outside.md)" + "\n")

    def test_multiline_inline_link_is_typed_rejection(self) -> None:
        with self.assertRaises(validate.MarkdownSyntaxError) as caught:
            validate.extract_link_destinations(
                validate.ROOT / "README.md",
                "[outer\ninner](docs/migration/CLOSEOUT.md)\n",
            )
        self.assertEqual(caught.exception.code, "MARKDOWN_UNSUPPORTED_MULTILINE_LINK_LABEL")

    def test_link_bracket_depth_limit_is_typed_rejection(self) -> None:
        text = "[" * 34 + "label" + "]" * 34 + "(docs/migration/CLOSEOUT.md)\n"
        with self.assertRaises(validate.MarkdownSyntaxError) as caught:
            validate.extract_link_destinations(validate.ROOT / "README.md", text)
        self.assertEqual(caught.exception.code, "MARKDOWN_LINK_BRACKET_DEPTH_EXCEEDED")

    def test_unterminated_inline_destination_is_typed_rejection(self) -> None:
        with self.assertRaises(validate.MarkdownSyntaxError) as caught:
            validate.extract_link_destinations(
                validate.ROOT / "README.md",
                "[link](docs/migration/CLOSEOUT.md\n",
            )
        self.assertEqual(caught.exception.code, "MARKDOWN_UNTERMINATED_INLINE_DESTINATION")

    def closeout_fixture(self) -> tuple[dict[str, object], dict[str, object]]:
        return (
            copy.deepcopy(current_json("closeout.v1.json")),
            current_json("artifact-manifest.v1.json"),
        )

    def assert_closeout_rejected(self, closeout: dict[str, object], manifest: dict[str, object]) -> None:
        with self.assertRaises(AssertionError):
            validate.validate_closeout_document(closeout, manifest, verify_files=False)

    def test_closeout_nonclaims_replacement_is_rejected(self) -> None:
        closeout, manifest = self.closeout_fixture()
        closeout["non_claims"] = ["Deployment LIVE and CurrentAuthority ACTIVE."]
        self.assert_closeout_rejected(closeout, manifest)

    def test_closeout_known_limitations_replacement_is_rejected(self) -> None:
        closeout, manifest = self.closeout_fixture()
        closeout["known_limitations"] = ["Production is live and qualified."]
        self.assert_closeout_rejected(closeout, manifest)

    def test_closeout_command_result_replacement_is_rejected(self) -> None:
        closeout, manifest = self.closeout_fixture()
        closeout["commands"][0]["result"] = "PASS; deployment live; authority selected"
        self.assert_closeout_rejected(closeout, manifest)

    def test_closeout_blocker_replacement_is_rejected(self) -> None:
        closeout, manifest = self.closeout_fixture()
        closeout["unresolved_blockers"][0]["blocker"] = "None; all qualified."
        self.assert_closeout_rejected(closeout, manifest)

    def test_closeout_rollback_permutation_is_rejected(self) -> None:
        closeout, manifest = self.closeout_fixture()
        rows = closeout["rollback"]["revert_order"]
        rows[1], rows[2] = rows[2], rows[1]
        self.assert_closeout_rejected(closeout, manifest)

    def test_closeout_rollback_omission_is_rejected(self) -> None:
        closeout, manifest = self.closeout_fixture()
        closeout["rollback"]["revert_order"].pop(3)
        self.assert_closeout_rejected(closeout, manifest)

    def test_closeout_rollback_fake_identity_is_rejected(self) -> None:
        closeout, manifest = self.closeout_fixture()
        closeout["rollback"]["revert_order"][1]["identity"] = "0" * 40
        self.assert_closeout_rejected(closeout, manifest)

    def test_closeout_rollback_target_drift_is_rejected(self) -> None:
        closeout, manifest = self.closeout_fixture()
        closeout["rollback"]["target"]["head"] = "0" * 40
        closeout["rollback"]["target"]["tree"] = "0" * 40
        self.assert_closeout_rejected(closeout, manifest)

    def test_closeout_semantic_negation_variants_are_rejected(self) -> None:
        variants = (
            ("non_claims", 0, "Runtime was not not added."),
            ("known_limitations", 0, "The archive setting is no longer blocked."),
            ("non_claims", 5, "Qualification and authority transitions did occur."),
        )
        for field, index, replacement in variants:
            closeout, manifest = self.closeout_fixture()
            closeout[field][index] = replacement
            with self.subTest(field=field, replacement=replacement):
                self.assert_closeout_rejected(closeout, manifest)

    def test_closeout_unblocks_inflation_is_rejected(self) -> None:
        closeout, manifest = self.closeout_fixture()
        closeout["unblocks"] = ["Deployment, activation, qualification, and authority are unblocked."]
        self.assert_closeout_rejected(closeout, manifest)

    def test_fault_corpus_label_drift_is_rejected(self) -> None:
        corpus = copy.deepcopy(current_json("test-fault-corpus.v1.json"))
        corpus["negative_cases"][0]["test"] = "arbitrary-label"
        with self.assertRaises(AssertionError):
            validate.validate_corpus_document(corpus)
        declared = {
            row["test"]
            for row in validate.POSITIVE_CORPUS + validate.NEGATIVE_CORPUS
        }
        available = {
            name for name in dir(self.__class__) if name.startswith("test_")
        }
        self.assertEqual(declared, available)


if __name__ == "__main__":
    unittest.main(verbosity=2)
