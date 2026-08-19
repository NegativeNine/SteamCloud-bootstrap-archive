#!/usr/bin/env python3
"""Drive the shipped placeholder archive validator on the real tree and failure paths."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from validate_placeholder import (
    ARCHITECTURE_ZIP,
    ROOT,
    fail,
    load_json,
    main,
    unique_object,
    validate_closeout_document,
    validate_coordination,
    validate_phase_ledger,
    validate_program_ledger,
    validate_structure,
)


class PlaceholderValidatorTests(unittest.TestCase):
    def test_cli_entry_point_passes_on_real_tree(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(ROOT / "scripts/validate_placeholder.py")],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("placeholder archive validation passed", completed.stdout)

    def test_main_function_passes_on_real_tree(self) -> None:
        self.assertEqual(main(), 0)

    def test_unique_object_rejects_duplicate_keys(self) -> None:
        with self.assertRaises(AssertionError) as ctx:
            unique_object([("legacy", "a"), ("legacy", "b")])
        self.assertIn("duplicate JSON key", str(ctx.exception))

    def test_load_json_rejects_duplicate_keys(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "dup.json"
            path.write_text('{"legacy": "a", "legacy": "b"}\n', encoding="utf-8")
            with self.assertRaises(AssertionError) as ctx:
                load_json(path)
            self.assertIn("duplicate JSON key", str(ctx.exception))

    def test_architecture_zip_fails_structure(self) -> None:
        self.addCleanup(lambda: ARCHITECTURE_ZIP.unlink(missing_ok=True))
        ARCHITECTURE_ZIP.write_bytes(b"not-the-reviewed-architecture-package")
        with self.assertRaises(AssertionError) as ctx:
            validate_structure()
        self.assertIn("architecture ZIP must be removed", str(ctx.exception))

    def test_application_scaffold_fails_structure(self) -> None:
        cargo = ROOT / "Cargo.toml"
        self.addCleanup(lambda: cargo.unlink(missing_ok=True))
        cargo.write_text("[package]\nname = \"not-allowed\"\n", encoding="utf-8")
        with self.assertRaises(AssertionError) as ctx:
            validate_structure()
        self.assertIn("superseded application/sample path remains", str(ctx.exception))

    def test_fail_raises_assertion_error(self) -> None:
        with self.assertRaises(AssertionError) as ctx:
            fail("expected failure")
        self.assertEqual(str(ctx.exception), "expected failure")

    def test_phase_ledger_from_tree_is_accepted(self) -> None:
        ledger = load_json(ROOT / "docs/roadmap/PHASE_LEDGER.json")
        validate_phase_ledger(ledger)

    def test_complete_without_commit_is_refused(self) -> None:
        ledger = load_json(ROOT / "docs/roadmap/PHASE_LEDGER.json")
        phases = ledger["phases"]
        assert isinstance(phases, list)
        phase0 = phases[0]
        assert isinstance(phase0, dict)
        phase0["current_status"] = "COMPLETE"
        phase0["completion_commit"] = None
        with self.assertRaises(AssertionError) as ctx:
            validate_phase_ledger(ledger)
        self.assertIn("completion_commit", str(ctx.exception))

    def test_live_without_commit_is_refused(self) -> None:
        ledger = load_json(ROOT / "docs/roadmap/PHASE_LEDGER.json")
        phases = ledger["phases"]
        assert isinstance(phases, list)
        phase0 = phases[0]
        assert isinstance(phase0, dict)
        phase0["current_status"] = "LIVE"
        phase0["completion_commit"] = None
        with self.assertRaises(AssertionError) as ctx:
            validate_phase_ledger(ledger)
        self.assertIn("completion_commit", str(ctx.exception))

    def test_admin_phase_complete_is_refused(self) -> None:
        ledger = load_json(ROOT / "docs/roadmap/PHASE_LEDGER.json")
        phases = ledger["phases"]
        assert isinstance(phases, list)
        phase1 = next(
            phase for phase in phases if phase["phase_or_wave_id"] == "phase-1"
        )
        assert isinstance(phase1, dict)
        phase1["current_status"] = "COMPLETE"
        phase1["completion_commit"] = "541ff226a963ffa9acc1fcc6062b6878c2832592"
        phase1["completed_at"] = "2026-08-19"
        with self.assertRaises(AssertionError) as ctx:
            validate_phase_ledger(ledger)
        self.assertIn("must not be marked complete", str(ctx.exception))

    def test_sibling_phase_production_qualified_is_refused(self) -> None:
        ledger = load_json(ROOT / "docs/roadmap/PHASE_LEDGER.json")
        phases = ledger["phases"]
        assert isinstance(phases, list)
        phase4 = next(
            phase for phase in phases if phase["phase_or_wave_id"] == "phase-4"
        )
        assert isinstance(phase4, dict)
        phase4["current_status"] = "PRODUCTION_QUALIFIED"
        phase4["completion_commit"] = "541ff226a963ffa9acc1fcc6062b6878c2832592"
        phase4["completed_at"] = "2026-08-19"
        with self.assertRaises(AssertionError) as ctx:
            validate_phase_ledger(ledger)
        self.assertIn("must not be marked complete", str(ctx.exception))

    def test_missing_deployment_target_is_refused(self) -> None:
        ledger = load_json(ROOT / "docs/roadmap/PHASE_LEDGER.json")
        phases = ledger["phases"]
        assert isinstance(phases, list)
        phase0 = phases[0]
        assert isinstance(phase0, dict)
        del phase0["deployment_target"]
        with self.assertRaises(AssertionError) as ctx:
            validate_phase_ledger(ledger)
        self.assertIn("deployment_target", str(ctx.exception))

    def test_program_ledger_from_tree_is_accepted(self) -> None:
        validate_program_ledger(load_json(ROOT / "docs/migration/PROGRAM_LEDGER.json"))
        validate_coordination(load_json(ROOT / "docs/migration/COORDINATION.json"))
        validate_closeout_document(load_json(ROOT / "docs/migration/CLOSEOUT.json"))

    def test_program_ledger_sibling_pin_is_refused(self) -> None:
        ledger = load_json(ROOT / "docs/migration/PROGRAM_LEDGER.json")
        pins = ledger["dependency_pins"]
        assert isinstance(pins, dict)
        pins["NegativeNine/Ember"] = "deadbeef"
        with self.assertRaises(AssertionError) as ctx:
            validate_program_ledger(ledger)
        self.assertIn("UNKNOWN", str(ctx.exception))

    def test_closeout_program_complete_is_refused(self) -> None:
        closeout = load_json(ROOT / "docs/migration/CLOSEOUT.json")
        closeout["program_complete"] = True
        with self.assertRaises(AssertionError) as ctx:
            validate_closeout_document(closeout)
        self.assertIn("program_complete", str(ctx.exception))

    def test_closeout_local_complete_is_refused(self) -> None:
        closeout = load_json(ROOT / "docs/migration/CLOSEOUT.json")
        closeout["terminal_state"] = "LOCAL_COMPLETE"
        closeout["closeout_status"] = "LOCAL_COMPLETE"
        with self.assertRaises(AssertionError) as ctx:
            validate_closeout_document(closeout)
        self.assertIn("BLOCKED_EXTERNAL", str(ctx.exception))

    def test_coordination_program_complete_is_refused(self) -> None:
        record = load_json(ROOT / "docs/migration/COORDINATION.json")
        messages = record["messages"]
        assert isinstance(messages, list)
        latest = messages[-1]
        assert isinstance(latest, dict)
        latest["state"] = "PROGRAM_COMPLETE"
        with self.assertRaises(AssertionError) as ctx:
            validate_coordination(record)
        self.assertIn("PROGRAM_COMPLETE", str(ctx.exception))


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__])
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if result.wasSuccessful():
        print("placeholder archive tests passed")
    raise SystemExit(0 if result.wasSuccessful() else 1)
