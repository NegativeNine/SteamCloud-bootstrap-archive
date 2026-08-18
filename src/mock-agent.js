import { assertRegionalAgentMayExecute } from './operations.js';
import { assertNoSecretFields } from './secrets.js';

export class MockSteamAgent {
  #seen = new Map();

  constructor({ leaseBook }) {
    if (!leaseBook) throw new Error('lease book is required');
    this.leaseBook = leaseBook;
  }

  execute(grant, argumentsValue) {
    if (grant.schema !== 'campfire.action-grant/v1') throw new Error('invalid action grant');
    if (grant.audience !== 'urn:steamcloud:agent') throw new Error('wrong audience');
    assertNoSecretFields(argumentsValue);
    for (const [key, generation] of Object.entries(grant.lease_fences)) {
      this.leaseBook.require(key, generation);
    }
    const fingerprint = `${grant.idempotency_key}:${grant.arguments_sha256}`;
    const prior = this.#seen.get(fingerprint);
    if (prior) return { ...prior, replayed: true };
    assertRegionalAgentMayExecute(grant.operation);
    const result = Object.freeze({
      schema: 'campfire.action-settlement/v1',
      attempt_id: grant.attempt_id,
      outcome: 'COMPLETED',
      operation: grant.operation,
      replayed: false,
      result: { kind: 'mock', observed_at: '2026-08-18T16:00:00Z' },
    });
    this.#seen.set(fingerprint, result);
    return result;
  }
}
