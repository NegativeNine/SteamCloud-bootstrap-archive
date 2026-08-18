import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

export function packageRoot() {
  return path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
}

function readJsonFiles(dir) {
  return fs
    .readdirSync(dir)
    .filter((name) => name.endsWith('.json'))
    .map((name) => JSON.parse(fs.readFileSync(path.join(dir, name), 'utf8')));
}

export function loadOperationCatalog(root = packageRoot()) {
  const rows = readJsonFiles(path.join(root, 'operations'));
  return new Map(rows.map((row) => [row.operation, Object.freeze(row)]));
}

export function loadPacks(root = packageRoot()) {
  return readJsonFiles(path.join(root, 'packs')).map((pack) => Object.freeze(pack));
}
