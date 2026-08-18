#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import pathlib
from copy import deepcopy

import jsonschema
import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]

def load_json(path: pathlib.Path):
    return json.loads(path.read_text(encoding='utf-8'))

def validate_review() -> None:
    schema_dir = ROOT / 'review' / 'schemas'
    finding_schema = load_json(schema_dir / 'finding.schema.json')
    report_schema = load_json(schema_dir / 'repo-report.schema.json')
    report = load_json(ROOT / 'review' / 'report.json')
    for finding in report['findings']:
        jsonschema.Draft202012Validator(finding_schema).validate(finding)
    expanded = deepcopy(report_schema)
    expanded['properties']['findings']['items'] = finding_schema
    jsonschema.Draft202012Validator(expanded).validate(report)

def validate_fixtures() -> None:
    schema_dir = ROOT / 'schemas'
    fixture_dir = schema_dir / 'fixtures'
    aliases = {
        'command-capability': 'command-capability.schema.json',
        'action-grant': 'action-grant.schema.json',
        'resource-lease': 'resource-lease.schema.json',
        'collection-permit': 'collection-permit.schema.json',
        'source-artifact': 'source-artifact.schema.json',
        'observation-publication': 'observation-publication.schema.json',
        'world-view': 'world-view.schema.json',
        'dependency-status': 'dependency-status.schema.json',
        'operation-definition': 'operation-definition.schema.json',
        'pack': 'pack.schema.json',
    }
    for fixture in sorted(fixture_dir.glob('*.json')):
        stem = fixture.name.split('.')[0]
        schema = load_json(schema_dir / aliases[stem])
        instance = load_json(fixture)
        validator = jsonschema.Draft202012Validator(schema, format_checker=jsonschema.FormatChecker())
        errors = list(validator.iter_errors(instance))
        if '.valid.' in fixture.name and errors:
            raise AssertionError(f'{fixture}: expected valid: {errors[0].message}')
        if '.invalid.' in fixture.name and not errors:
            raise AssertionError(f'{fixture}: expected invalid')

def parse_structured_files() -> None:
    for path in ROOT.rglob('*.json'):
        load_json(path)
    for pattern in ('*.yaml', '*.yml'):
        for path in ROOT.rglob(pattern):
            yaml.safe_load(path.read_text(encoding='utf-8'))

def load_forbidden_keys() -> set[str]:
    document = load_json(ROOT / 'schemas' / 'forbidden-fields.json')
    if document.get('schema') != 'steamcloud.forbidden-fields/v1':
        raise AssertionError('unexpected forbidden-fields schema')
    return {str(key).lower() for key in document['keys']}

def scan_keys(value, source: pathlib.Path, forbidden: set[str], trail='') -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            norm = str(key).lower()
            if norm in forbidden:
                raise AssertionError(f'{source}: forbidden high-risk key at {trail}/{key}')
            scan_keys(child, source, forbidden, f'{trail}/{key}')
    elif isinstance(value, list):
        for idx, child in enumerate(value):
            scan_keys(child, source, forbidden, f'{trail}/{idx}')

def scan_domain_json() -> None:
    forbidden = load_forbidden_keys()
    for dirname in ('operations', 'packs', 'examples'):
        root = ROOT / dirname
        if not root.exists():
            continue
        for path in root.rglob('*.json'):
            scan_keys(load_json(path), path, forbidden)

def is_manifest_subject(rel: str) -> bool:
    if rel == 'MANIFEST.sha256':
        return False
    if rel == '.git' or rel.startswith('.git/'):
        return False
    if rel == 'SteamCloud_13_Repository_Rearchitecture_Package_v1.0.zip':
        return False
    if rel == 'Cargo.lock' or rel == 'target' or rel.startswith('target/'):
        return False
    return True


def validate_manifest() -> None:
    manifest = ROOT / 'MANIFEST.sha256'
    if not manifest.exists():
        raise AssertionError('missing MANIFEST.sha256')
    expected = {}
    for line in manifest.read_text(encoding='utf-8').splitlines():
        if not line.strip():
            continue
        digest, rel = line.split('  ', 1)
        expected[rel] = digest
    actual = {}
    for path in sorted(p for p in ROOT.rglob('*') if p.is_file()):
        rel = path.relative_to(ROOT).as_posix()
        if not is_manifest_subject(rel):
            continue
        actual[rel] = hashlib.sha256(path.read_bytes()).hexdigest()
    if actual != expected:
        missing = sorted(set(expected) - set(actual))
        extra = sorted(set(actual) - set(expected))
        changed = sorted(k for k in set(actual) & set(expected) if actual[k] != expected[k])
        raise AssertionError(f'manifest mismatch missing={missing} extra={extra} changed={changed}')

def main() -> int:
    parse_structured_files()
    validate_review()
    validate_fixtures()
    scan_domain_json()
    validate_manifest()
    print(json.dumps({'ok': True, 'repository': load_json(ROOT / 'REPO-METADATA.json')['repository']}))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
