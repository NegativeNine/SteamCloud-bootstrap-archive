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
    def validate_extracted(self, text: str) -> list[dict[str, object]]:
        source = validate.ROOT / "README.md"
        records = validate.extract_link_destinations(source, text)
        for record in records:
            destination = record["destination"]
            self.assertIsInstance(destination, str)
            validate.validate_link_destination(source, destination)
        return records

    @staticmethod
    def semantic(records: list[dict[str, object]]) -> list[dict[str, object]]:
        return [
            {"syntax": record["syntax"], "destination": record["destination"]}
            for record in records
        ]

    def test_current_link_inventory_is_exact(self) -> None:
        self.assertEqual(validate.validate_links(), 34)

    def test_reference_style_local_link_is_checked(self) -> None:
        records = self.validate_extracted(
            "See [the closeout][close].\n\n[close]: docs/migration/CLOSEOUT.md\n"
        )
        self.assertEqual(
            self.semantic(records),
            [{"syntax": "link", "destination": "docs/migration/CLOSEOUT.md"}],
        )

    def test_html_local_link_is_checked(self) -> None:
        records = self.validate_extracted(
            '<a href="docs/migration/CLOSEOUT.md">closeout</a>\n'
        )
        self.assertEqual(
            self.semantic(records),
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
            self.semantic(records),
            [{"syntax": "link", "destination": "docs/migration/CLOSEOUT.md"}],
        )

    def test_escaped_bracket_inline_link_is_checked(self) -> None:
        records = self.validate_extracted(
            r"[outer \] bracket](docs/migration/CLOSEOUT.md)" + "\n"
        )
        self.assertEqual(
            self.semantic(records),
            [{"syntax": "link", "destination": "docs/migration/CLOSEOUT.md"}],
        )

    def test_nested_bracket_image_link_is_checked(self) -> None:
        records = self.validate_extracted(
            "![outer [inner]](docs/migration/CLOSEOUT.md)\n"
        )
        self.assertEqual(
            self.semantic(records),
            [{"syntax": "image", "destination": "docs/migration/CLOSEOUT.md"}],
        )

    def test_nested_image_inside_link_inventories_both(self) -> None:
        records = self.validate_extracted(
            "[![alt](docs/archive/HISTORICAL_BUILD.md)](docs/migration/CLOSEOUT.md)\n"
        )
        self.assertEqual(
            self.semantic(records),
            [
                {"syntax": "link", "destination": "docs/migration/CLOSEOUT.md"},
                {"syntax": "image", "destination": "docs/archive/HISTORICAL_BUILD.md"},
            ],
        )

    def test_recursive_image_children_inventory_every_active_destination(self) -> None:
        records = self.validate_extracted(
            "[![![alt](docs/migration/ACCEPTANCE.md)](docs/archive/HISTORICAL_BUILD.md)]"
            "(docs/migration/CLOSEOUT.md)\n"
        )
        self.assertEqual(
            self.semantic(records),
            [
                {"syntax": "link", "destination": "docs/migration/CLOSEOUT.md"},
                {"syntax": "image", "destination": "docs/archive/HISTORICAL_BUILD.md"},
                {"syntax": "image", "destination": "docs/migration/ACCEPTANCE.md"},
            ],
        )

    def test_inner_link_inside_nonlink_outer_uses_commonmark_precedence(self) -> None:
        records = self.validate_extracted(
            "[outer [inner](docs/migration/CLOSEOUT.md)](docs/archive/DOES_NOT_EXIST.md)\n"
        )
        self.assertEqual(
            self.semantic(records),
            [{"syntax": "link", "destination": "docs/migration/CLOSEOUT.md"}],
        )

    def test_quoted_titles_with_unbalanced_parentheses_are_valid(self) -> None:
        variants = (
            '[x](docs/migration/CLOSEOUT.md "literal ) title")',
            '[x](docs/migration/CLOSEOUT.md "literal ( title")',
            "[x](docs/migration/CLOSEOUT.md 'literal ) title')",
            "[x](docs/migration/CLOSEOUT.md 'literal ( title')",
        )
        for text in variants:
            with self.subTest(text=text):
                records = self.validate_extracted(text + "\n")
                self.assertEqual(
                    self.semantic(records),
                    [{"syntax": "link", "destination": "docs/migration/CLOSEOUT.md"}],
                )

    def test_angle_and_parenthesized_titles_are_valid(self) -> None:
        variants = (
            '[x](<docs/migration/CLOSEOUT.md> "literal ) title")',
            r"[x](docs/migration/CLOSEOUT.md (literal \) title))",
            "[x](<docs/migration/CLOSEOUT.md>)",
        )
        for text in variants:
            with self.subTest(text=text):
                records = self.validate_extracted(text + "\n")
                self.assertEqual(len(records), 1)
                self.assertEqual(records[0]["destination"], "docs/migration/CLOSEOUT.md")

    def test_reference_variants_inventory_each_active_use(self) -> None:
        records = self.validate_extracted(
            "[one][close]\n\n[close][] and [close]\n\n"
            "[close]: docs/migration/CLOSEOUT.md 'literal ) title'\n"
        )
        self.assertEqual(
            self.semantic(records),
            [
                {"syntax": "link", "destination": "docs/migration/CLOSEOUT.md"},
                {"syntax": "link", "destination": "docs/migration/CLOSEOUT.md"},
                {"syntax": "link", "destination": "docs/migration/CLOSEOUT.md"},
            ],
        )

    def test_container_reference_existing_matrix_and_source_spans(self) -> None:
        fixtures = (
            ("[x][r]\n\n[r]: docs/migration/CLOSEOUT.md\n", 3, 1),
            ("> [x][r]\n>\n> [r]: docs/migration/CLOSEOUT.md\n", 3, 3),
            ("> > [x][r]\n> >\n> > [r]: docs/migration/CLOSEOUT.md\n", 3, 5),
            ("- [x][r]\n\n  [r]: docs/migration/CLOSEOUT.md\n", 3, 3),
            ("123. [x][r]\n\n     [r]: docs/migration/CLOSEOUT.md\n", 3, 6),
            ("- outer\n  - [x][r]\n\n    [r]: docs/migration/CLOSEOUT.md\n", 4, 5),
            ("- > [x][r]\n  >\n  > [r]: docs/migration/CLOSEOUT.md\n", 3, 5),
            ("- [x][r]\n\n\t[r]: docs/migration/CLOSEOUT.md\n", 3, 2),
        )
        for text, line, column in fixtures:
            with self.subTest(text=text):
                records = self.validate_extracted(text)
                definitions = validate.extract_reference_definitions(
                    validate.ROOT / "README.md", text
                )
                self.assertEqual(
                    self.semantic(records),
                    [{"syntax": "link", "destination": "docs/migration/CLOSEOUT.md"}],
                )
                self.assertEqual(len(definitions), 1)
                self.assertEqual(definitions[0]["occurrence"], 1)
                self.assertEqual(definitions[0]["line_start"], line)
                self.assertEqual(definitions[0]["line_end"], line)
                self.assertEqual(definitions[0]["column_start"], column)
                self.assertLess(definitions[0]["offset_start"], definitions[0]["offset_end"])

    def test_container_reference_multiline_titles_and_escapes_are_valid(self) -> None:
        fixtures = (
            '> [x][r]\n>\n> [r]: docs/migration/CLOSEOUT.md "literal ) title"\n',
            "> [x][r]\n>\n> [r]: docs/migration/CLOSEOUT.md 'literal ( title'\n",
            "> [x][r]\n>\n> [r]: docs/migration/CLOSEOUT.md\n>   \"line two ) title\"\n",
            r"> [x][a\]b]" + "\n>\n> " + r"[a\]b]: <docs/migration/CLOSEOUT.md> (escaped \) title)" + "\n",
            "> [x][foo bar]\n>\n> [foo\n> bar]: docs/migration/CLOSEOUT.md\n",
            "- [x][foo bar]\n\n  [foo\n  bar]:\n   docs/migration/CLOSEOUT.md\n",
            "> [x][r]\r\n>\r\n> [r]: docs/migration/CLOSEOUT.md\r\n",
        )
        for text in fixtures:
            with self.subTest(text=text):
                records = self.validate_extracted(text)
                definitions = validate.extract_reference_definitions(
                    validate.ROOT / "README.md", text
                )
                self.assertEqual(len(records), 1)
                self.assertEqual(records[0]["destination"], "docs/migration/CLOSEOUT.md")
                self.assertEqual(len(definitions), 1)
        multiline = validate.extract_reference_definitions(
            validate.ROOT / "README.md", fixtures[2]
        )[0]
        self.assertEqual((multiline["line_start"], multiline["line_end"]), (3, 4))
        self.assertEqual(multiline["title"], "line two ) title")
        multiline_label = validate.extract_reference_definitions(
            validate.ROOT / "README.md", fixtures[4]
        )[0]
        self.assertEqual((multiline_label["line_start"], multiline_label["line_end"]), (3, 4))
        self.assertEqual(multiline_label["normalized_label"], "FOO BAR")
        multiline_destination = validate.extract_reference_definitions(
            validate.ROOT / "README.md", fixtures[5]
        )[0]
        self.assertEqual(
            (multiline_destination["line_start"], multiline_destination["line_end"]),
            (3, 5),
        )
        crlf = validate.extract_reference_definitions(
            validate.ROOT / "README.md", fixtures[6]
        )[0]
        self.assertEqual(
            (crlf["line_start"], crlf["line_end"], crlf["column_start"]),
            (3, 3, 3),
        )

    def test_reference_definition_order_and_multiplicity_are_exact(self) -> None:
        text = (
            "> [one][a] and [two][b]\n>\n"
            "> [a]: docs/migration/CLOSEOUT.md\n"
            "> [b]: docs/archive/HISTORICAL_BUILD.md\n"
        )
        records = self.validate_extracted(text)
        definitions = validate.extract_reference_definitions(
            validate.ROOT / "README.md", text
        )
        self.assertEqual([row["occurrence"] for row in definitions], [1, 2])
        self.assertEqual([row["normalized_label"] for row in definitions], ["A", "B"])
        self.assertEqual([row["line_start"] for row in definitions], [3, 4])
        self.assertEqual(
            [row["destination"] for row in definitions],
            ["docs/migration/CLOSEOUT.md", "docs/archive/HISTORICAL_BUILD.md"],
        )
        self.assertEqual(len(records), 2)

    def test_duplicate_destinations_preserve_occurrence_and_line_identity(self) -> None:
        records = self.validate_extracted(
            "[one](docs/migration/CLOSEOUT.md)\n\n"
            "[two](docs/migration/CLOSEOUT.md)\n"
        )
        self.assertEqual([record["occurrence"] for record in records], [1, 2])
        self.assertEqual([record["line_start"] for record in records], [1, 3])
        self.assertEqual([record["line_end"] for record in records], [1, 3])
        self.assertEqual(
            [record["destination"] for record in records],
            ["docs/migration/CLOSEOUT.md", "docs/migration/CLOSEOUT.md"],
        )

    def test_autolink_inline_html_and_markdown_boundaries_are_exact(self) -> None:
        records = self.validate_extracted(
            "<https://example.com/archive>\n\n"
            '<a href="docs/migration/CLOSEOUT.md"><img src="docs/archive/HISTORICAL_BUILD.md"></a>\n\n'
            "<span>[close](docs/migration/CLOSEOUT.md)</span>\n"
        )
        self.assertEqual(
            self.semantic(records),
            [
                {"syntax": "autolink", "destination": "https://example.com/archive"},
                {"syntax": "html", "destination": "docs/migration/CLOSEOUT.md"},
                {"syntax": "html", "destination": "docs/archive/HISTORICAL_BUILD.md"},
                {"syntax": "link", "destination": "docs/migration/CLOSEOUT.md"},
            ],
        )

    def test_raw_html_blocks_do_not_activate_markdown_syntax(self) -> None:
        records = validate.extract_link_destinations(
            validate.ROOT / "README.md",
            "<div>\n[not active](docs/migration/DOES_NOT_EXIST.md)\n"
            "[broken](<unterminated\n</div>\n",
        )
        self.assertEqual(records, [])

    def test_inline_raw_html_special_forms_do_not_hide_or_invent_links(self) -> None:
        records = self.validate_extracted(
            "prefix <!-- [bad](<unterminated) --> "
            "<?archive [bad](<unterminated)?> "
            "<![CDATA[[bad](<unterminated)]]> "
            "[good](docs/migration/CLOSEOUT.md)\n"
        )
        self.assertEqual(
            self.semantic(records),
            [{"syntax": "link", "destination": "docs/migration/CLOSEOUT.md"}],
        )

    def test_parser_dependency_identity_is_exact(self) -> None:
        validate.validate_markdown_parser_identity()

    def test_missing_inline_link_is_rejected(self) -> None:
        with self.assertRaisesRegex(AssertionError, "target missing"):
            self.validate_extracted("[broken](docs/migration/DOES_NOT_EXIST.md)\n")

    def test_nested_image_inside_link_missing_inner_is_rejected(self) -> None:
        variants = (
            "[![alt](docs/migration/DOES_NOT_EXIST.md)](docs/migration/CLOSEOUT.md)\n",
            "[![![alt](docs/migration/DOES_NOT_EXIST.md)](docs/archive/HISTORICAL_BUILD.md)]"
            "(docs/migration/CLOSEOUT.md)\n",
        )
        for text in variants:
            with self.subTest(text=text):
                with self.assertRaisesRegex(AssertionError, "target missing"):
                    self.validate_extracted(text)

    def test_inner_link_inside_nonlink_outer_missing_is_rejected(self) -> None:
        with self.assertRaisesRegex(AssertionError, "target missing"):
            self.validate_extracted(
                "[outer [inner](docs/migration/DOES_NOT_EXIST.md)](docs/migration/CLOSEOUT.md)\n"
            )

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

    def assert_markdown_code(self, text: str, code: str) -> None:
        with self.assertRaises(validate.MarkdownSyntaxError) as caught:
            validate.extract_link_destinations(validate.ROOT / "README.md", text)
        self.assertEqual(caught.exception.code, code)
        self.assertIsNotNone(caught.exception.line)
        self.assertIsNotNone(caught.exception.column)

    def assert_reference_code(
        self,
        text: str,
        code: str,
        line: int,
        column: int,
    ) -> None:
        with self.assertRaises(validate.MarkdownSyntaxError) as caught:
            validate.extract_reference_definitions(validate.ROOT / "README.md", text)
        self.assertEqual(caught.exception.code, code)
        self.assertEqual(caught.exception.line, line)
        self.assertEqual(caught.exception.column, column)

    def test_unterminated_angle_destinations_are_typed_rejections(self) -> None:
        variants = (
            "[x](<docs/migration/CLOSEOUT.md)\n",
            "![x](<docs/migration/CLOSEOUT.md\n",
            "[outer [x](<docs/migration/CLOSEOUT.md)](docs/migration/CLOSEOUT.md)\n",
        )
        for text in variants:
            with self.subTest(text=text):
                self.assert_markdown_code(text, "MARKDOWN_UNTERMINATED_ANGLE_DESTINATION")

    def test_malformed_angle_destination_is_typed_rejection(self) -> None:
        self.assert_markdown_code(
            "[x](<docs/<migration/CLOSEOUT.md>)\n",
            "MARKDOWN_MALFORMED_ANGLE_DESTINATION",
        )

    def test_unterminated_quoted_titles_are_typed_rejections(self) -> None:
        for quote in ('"', "'"):
            text = f"[x](docs/migration/CLOSEOUT.md {quote}literal ) title)\n"
            with self.subTest(quote=quote):
                self.assert_markdown_code(text, "MARKDOWN_UNTERMINATED_QUOTED_TITLE")

    def test_unterminated_parenthesized_title_is_typed_rejection(self) -> None:
        self.assert_markdown_code(
            "[x](docs/migration/CLOSEOUT.md (unterminated title)",
            "MARKDOWN_UNTERMINATED_INLINE_DESTINATION",
        )
        self.assert_markdown_code(
            "[x](docs/migration/CLOSEOUT.md (unterminated title",
            "MARKDOWN_UNTERMINATED_PARENTHESIZED_TITLE",
        )

    def test_malformed_inline_title_and_tail_are_typed_rejections(self) -> None:
        cases = (
            (
                "[x](docs/migration/CLOSEOUT.md bare-title)\n",
                "MARKDOWN_MALFORMED_INLINE_TITLE",
            ),
            (
                '[x](docs/migration/CLOSEOUT.md "title" trailing)\n',
                "MARKDOWN_MALFORMED_INLINE_TAIL",
            ),
        )
        for text, code in cases:
            with self.subTest(text=text):
                self.assert_markdown_code(text, code)

    def test_multiline_title_is_typed_rejection(self) -> None:
        self.assert_markdown_code(
            '[x](docs/migration/CLOSEOUT.md "line one\nline two")\n',
            "MARKDOWN_UNSUPPORTED_MULTILINE_INLINE_TITLE",
        )

    def test_destination_depth_and_size_limits_are_typed(self) -> None:
        self.assert_markdown_code(
            "[x](" + "(" * 33 + "target" + ")" * 34 + "\n",
            "MARKDOWN_LINK_PAREN_DEPTH_EXCEEDED",
        )
        self.assert_markdown_code(
            "[x](" + "a" * (validate.MAX_LINK_DESTINATION_CHARS + 1) + ")\n",
            "MARKDOWN_LINK_DESTINATION_LIMIT_EXCEEDED",
        )

    def test_reference_definition_malformed_forms_are_typed(self) -> None:
        cases = (
            (
                "[x][r]\n\n[r]: <docs/migration/CLOSEOUT.md\n",
                "MARKDOWN_UNTERMINATED_ANGLE_DESTINATION",
            ),
            (
                '[x][r]\n\n[r]: docs/migration/CLOSEOUT.md "title\n',
                "MARKDOWN_UNTERMINATED_QUOTED_TITLE",
            ),
            (
                "[x][r]\n\n[r]: docs/migration/CLOSEOUT.md bare\n",
                "MARKDOWN_MALFORMED_REFERENCE_TITLE",
            ),
        )
        for text, code in cases:
            with self.subTest(text=text):
                self.assert_markdown_code(text, code)

    def test_r10_exact_container_unterminated_angle_fixtures_are_typed(self) -> None:
        fixtures = (
            ("> [x][r]\n>\n> [r]: <docs/migration/CLOSEOUT.md\n", 3, 8),
            ("> > [x][r]\n> >\n> > [r]: <docs/migration/CLOSEOUT.md\n", 3, 10),
            ("123. [x][r]\n\n     [r]: <docs/migration/CLOSEOUT.md\n", 3, 11),
            ("- outer\n  - [x][r]\n\n    [r]: <docs/migration/CLOSEOUT.md\n", 4, 10),
            ("[x][r]\n\n[r]: <docs/migration/CLOSEOUT.md\n", 3, 6),
            ("> [x][r]\r\n>\r\n> [r]: <docs/migration/CLOSEOUT.md\r\n", 3, 8),
            ("- [x][r]\n\n\t[r]: <docs/migration/CLOSEOUT.md\n", 3, 7),
        )
        for text, line, column in fixtures:
            with self.subTest(text=text):
                self.assert_reference_code(
                    text,
                    "MARKDOWN_UNTERMINATED_ANGLE_DESTINATION",
                    line,
                    column,
                )

    def test_r10_exact_container_unterminated_title_fixtures_are_typed(self) -> None:
        fixtures = (
            ("> [x][r]\n>\n> [r]: docs/migration/CLOSEOUT.md \"title\n", 3, 35),
            (
                "- > [x][r]\n  >\n  > [r]: docs/migration/CLOSEOUT.md \"title\n",
                3,
                37,
            ),
        )
        for text, line, column in fixtures:
            with self.subTest(text=text):
                self.assert_reference_code(
                    text,
                    "MARKDOWN_UNTERMINATED_QUOTED_TITLE",
                    line,
                    column,
                )

    def test_r10_exact_container_duplicate_fixtures_are_typed(self) -> None:
        fixtures = (
            (
                "> [x][r]\n>\n> [r]: docs/migration/CLOSEOUT.md\n"
                "> [R]: docs/migration/DOES_NOT_EXIST.md\n",
                4,
                3,
            ),
            (
                "123. [x][r]\n\n     [r]: docs/migration/CLOSEOUT.md\n"
                "     [R]: docs/migration/DOES_NOT_EXIST.md\n",
                4,
                6,
            ),
            (
                "- outer\n  - [x][r]\n\n    [r]: docs/migration/CLOSEOUT.md\n"
                "    [R]: docs/migration/DOES_NOT_EXIST.md\n",
                5,
                5,
            ),
            (
                "- [x][r]\n\n  [r]: docs/migration/CLOSEOUT.md\n"
                "  [R]: docs/migration/DOES_NOT_EXIST.md\n",
                4,
                3,
            ),
        )
        for text, line, column in fixtures:
            with self.subTest(text=text):
                self.assert_reference_code(
                    text,
                    "MARKDOWN_DUPLICATE_REFERENCE_DEFINITION",
                    line,
                    column,
                )

    def test_container_reference_missing_and_unsafe_destinations_are_rejected(self) -> None:
        fixtures = (
            "> [x][r]\n>\n> [r]: docs/migration/DOES_NOT_EXIST.md\n",
            "> [x][r]\n>\n> [r]: ../outside.md\n",
            "> > [x][r]\n> >\n> > [r]: %2e%2e/outside.md\n",
            "123. [x][r]\n\n     [r]: /etc/passwd\n",
            "- outer\n  - [x][r]\n\n    [r]: http://example.com/archive\n",
            "- > [x][r]\n  >\n  > [r]: docs/migration/CLOSEOUT.md?activate=true\n",
            "> [x][r]\n>\n> [r]: docs/migration/CLOSEOUT.md#missing-heading\n",
        )
        for text in fixtures:
            with self.subTest(text=text):
                with self.assertRaises(AssertionError):
                    self.validate_extracted(text)

    def test_container_reference_malformed_depth_and_size_forms_are_typed(self) -> None:
        fixtures = (
            ("> [x][r]\n>\n> [r]: <docs/<migration/CLOSEOUT.md>\n", "MARKDOWN_MALFORMED_ANGLE_DESTINATION"),
            ("> [x][r]\n>\n> [r]: docs/migration/CLOSEOUT.md bare\n", "MARKDOWN_MALFORMED_REFERENCE_TITLE"),
            ("> [x][r]\n>\n> [r]: docs/migration/CLOSEOUT.md (title ( nested))\n", "MARKDOWN_MALFORMED_REFERENCE_TITLE"),
            ("> [x][r]\n>\n> [r]: docs/migration/CLOSEOUT.md (title\n", "MARKDOWN_UNTERMINATED_PARENTHESIZED_TITLE"),
            ("> [x][r]\n>\n> [r]: " + "(" * 33 + "x" + ")" * 33 + "\n", "MARKDOWN_LINK_PAREN_DEPTH_EXCEEDED"),
            ("> [x][r]\n>\n> [r]: " + "a" * (validate.MAX_LINK_DESTINATION_CHARS + 1) + "\n", "MARKDOWN_LINK_DESTINATION_LIMIT_EXCEEDED"),
        )
        for text, code in fixtures:
            with self.subTest(code=code):
                with self.assertRaises(validate.MarkdownSyntaxError) as caught:
                    validate.extract_reference_definitions(
                        validate.ROOT / "README.md", text
                    )
                self.assertEqual(caught.exception.code, code)

    def test_cross_container_duplicate_definition_is_typed_rejection(self) -> None:
        text = (
            "> [x][r]\n>\n> [r]: docs/migration/CLOSEOUT.md\n\n"
            "123. [y][R]\n\n     [R]: docs/archive/HISTORICAL_BUILD.md\n"
        )
        with self.assertRaises(validate.MarkdownSyntaxError) as caught:
            validate.extract_reference_definitions(validate.ROOT / "README.md", text)
        self.assertEqual(caught.exception.code, "MARKDOWN_DUPLICATE_REFERENCE_DEFINITION")
        self.assertEqual((caught.exception.line, caught.exception.column), (7, 6))

    def test_duplicate_reference_definitions_are_typed_rejection(self) -> None:
        self.assert_markdown_code(
            "[x][r]\n\n[r]: docs/migration/CLOSEOUT.md\n"
            "[R]: docs/archive/HISTORICAL_BUILD.md\n",
            "MARKDOWN_DUPLICATE_REFERENCE_DEFINITION",
        )

    def test_nested_active_traversal_and_query_vectors_are_rejected(self) -> None:
        variants = (
            "[![alt](../outside.md)](docs/migration/CLOSEOUT.md)\n",
            "[outer [inner](%2e%2e/outside.md)](docs/migration/CLOSEOUT.md)\n",
            "[![alt](docs/migration/CLOSEOUT.md?activate=true)](docs/migration/CLOSEOUT.md)\n",
        )
        for text in variants:
            with self.subTest(text=text):
                with self.assertRaises(AssertionError):
                    self.validate_extracted(text)

    def test_inline_html_wrapping_missing_markdown_is_rejected(self) -> None:
        with self.assertRaisesRegex(AssertionError, "target missing"):
            self.validate_extracted(
                "<span>[missing](docs/migration/DOES_NOT_EXIST.md)</span>\n"
            )

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
