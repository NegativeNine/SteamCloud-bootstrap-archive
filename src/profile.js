import crypto from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, '..');
const SECRET_KEYS = new Set(['password','steam_password','refresh_token','shared_secret','identity_secret','cookie','cookies','api_key','webapi_key','access_token','private_key','url','hostname','http_method','headers','asf_command','raw_payload']);

function canonical(value) {
  if (Array.isArray(value)) return `[${value.map(canonical).join(',')}]`;
  if (value && typeof value === 'object') return `{${Object.keys(value).sort().map((key) => `${JSON.stringify(key)}:${canonical(value[key])}`).join(',')}}`;
  return JSON.stringify(value);
}

export function hashArguments(value) {
  return crypto.createHash('sha256').update(canonical(value)).digest('hex');
}

export function assertNoSecretFields(value, trail='') {
  if (Array.isArray(value)) return value.forEach((item, index) => assertNoSecretFields(item, `${trail}/${index}`));
  if (!value || typeof value !== 'object') return;
  for (const [key, child] of Object.entries(value)) {
    if (SECRET_KEYS.has(key.toLowerCase())) throw new Error(`forbidden field ${trail}/${key}`);
    assertNoSecretFields(child, `${trail}/${key}`);
  }
}

export function loadOperationCatalog() {
  const dir = path.join(ROOT, 'operations');
  const rows = fs.readdirSync(dir).filter((name) => name.endsWith('.json')).map((name) => JSON.parse(fs.readFileSync(path.join(dir, name), 'utf8')));
  return new Map(rows.map((row) => [row.operation, Object.freeze(row)]));
}

export function admitOperation({operation, accountClass, arguments: args}, catalog=loadOperationCatalog()) {
  const definition = catalog.get(operation);
  if (!definition) throw new Error(`unknown operation ${operation}`);
  if (!definition.account_classes.includes(accountClass)) throw new Error('account class not allowed');
  if (['DISABLED_POLICY','REMOVED','VALVE_APPROVAL_REQUIRED'].includes(definition.policy_status)) throw new Error(`operation blocked: ${definition.policy_status}`);
  assertNoSecretFields(args);
  return Object.freeze({definition, arguments_sha256:hashArguments(args)});
}

export function compilePack(pack, catalog=loadOperationCatalog()) {
  if (pack.schema !== 'campfire.pack/v1' || pack.profile !== 'steamcloud') throw new Error('wrong pack profile');
  const ids = new Set();
  for (const step of pack.steps) {
    if (ids.has(step.id)) throw new Error('duplicate step id');
    for (const need of step.needs) if (!ids.has(need)) throw new Error(`dependency ${need} not yet declared`);
    ids.add(step.id);
  }
  return Object.freeze({...pack, compiled:true, catalogSize:catalog.size});
}
