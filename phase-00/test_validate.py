#!/usr/bin/env python3
"""Positive and fail-closed tests for the Phase 00 archive validator."""

from __future__ import annotations

import importlib.util
import pathlib
import unittest
from unittest import mock


MODULE_PATH = pathlib.Path(__file__).with_name("validate.py")
SPEC = importlib.util.spec_from_file_location("archive_phase00_validate", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)


class Phase00ValidatorTests(unittest.TestCase):
    def test_exact_archive_and_tag_pass(self) -> None:
        validator.validate_archive()

    def test_archive_digest_drift_fails(self) -> None:
        with mock.patch.object(validator, "BASE_ARCHIVE_SHA256", "0" * 64):
            with self.assertRaisesRegex(AssertionError, "base archive digest drift"):
                validator.validate_archive()

    def test_tag_target_drift_fails(self) -> None:
        with mock.patch.object(validator, "TAG_TARGET", "0" * 40):
            with self.assertRaisesRegex(AssertionError, "freeze tag target drift"):
                validator.validate_archive()

    def test_archive_only_workflow_passes(self) -> None:
        validator.validate_workflow()

    def test_source_boundary_passes(self) -> None:
        validator.validate_source_boundary()

    def test_seven_classes_and_nonclaims_pass(self) -> None:
        validator.validate_packet(preseal=True)

    def test_authority_movement_fails_closed(self) -> None:
        original = validator.load

        def altered(name: str):
            value = original(name)
            if name == "status.v1.json":
                value["authority_movement"] = "CURRENT_AUTHORITY"
            return value

        with mock.patch.object(validator, "load", side_effect=altered):
            with self.assertRaisesRegex(AssertionError, "activation or authority movement"):
                validator.validate_packet(preseal=True)

    def test_high_confidence_secret_patterns_match_adversarial_fixtures(self) -> None:
        fixtures = (
            b"-----BEGIN " + b"PRIVATE KEY-----",
            b"AK" + b"IA" + b"ABCDEFGHIJKLMNOP",
            b"gh" + b"p_" + b"abcdefghijklmnopqrstuvwxyz123456",
            b"xox" + b"b-" + b"abcdefghijklmnopqrstuvwxyz",
        )
        for fixture in fixtures:
            self.assertTrue(
                any(pattern.search(fixture) for pattern in validator.SECRET_PATTERNS),
                fixture,
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
