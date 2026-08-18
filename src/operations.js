import crypto from 'node:crypto';
import { assertNoSecretFields } from './secrets.js';

const BLOCKED_POLICY = new Set(['DISABLED_POLICY', 'REMOVED', 'VALVE_APPROVAL_REQUIRED']);

export const REGIONAL_AGENT_EXCLUDED_OPERATIONS = Object.freeze(
  new Set(['asf.owner.edge.fetch']),
);

function canonical(value) {
  if (Array.isArray(value)) return `[${value.map(canonical).join(',')}]`;
  if (value && typeof value === 'object') {
    return `{${Object.keys(value)
      .sort()
      .map((key) => `${JSON.stringify(key)}:${canonical(value[key])}`)
      .join(',')}}`;
  }
  return JSON.stringify(value);
}

export function hashArguments(value) {
  return crypto.createHash('sha256').update(canonical(value)).digest('hex');
}

export function admitOperation(request, catalog) {
  if (!(catalog instanceof Map)) throw new Error('operation catalog is required');
  const { operation, accountClass, arguments: args } = request;
  const definition = catalog.get(operation);
  if (!definition) throw new Error(`unknown operation ${operation}`);
  if (!definition.account_classes.includes(accountClass)) throw new Error('account class not allowed');
  if (BLOCKED_POLICY.has(definition.policy_status)) {
    throw new Error(`operation blocked: ${definition.policy_status}`);
  }
  assertNoSecretFields(args);
  return Object.freeze({ definition, arguments_sha256: hashArguments(args) });
}

export function compilePack(pack) {
  if (pack.schema !== 'campfire.pack/v1' || pack.profile !== 'steamcloud') {
    throw new Error('wrong pack profile');
  }
  const ids = new Set();
  for (const step of pack.steps) {
    if (ids.has(step.id)) throw new Error('duplicate step id');
    for (const need of step.needs) {
      if (!ids.has(need)) throw new Error(`dependency ${need} not yet declared`);
    }
    ids.add(step.id);
  }
  return Object.freeze({ ...pack, compiled: true });
}

export function assertRegionalAgentMayExecute(operation) {
  if (REGIONAL_AGENT_EXCLUDED_OPERATIONS.has(operation)) {
    throw new Error('owner edge action cannot execute in regional agent');
  }
}
