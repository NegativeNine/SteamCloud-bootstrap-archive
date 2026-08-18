import test from 'node:test';
import assert from 'node:assert/strict';
import {
  createMockRuntime,
  hashArguments,
  MockSteamAgent,
  ResourceLeaseBook,
} from '../src/index.js';

function grant(overrides = {}) {
  return {
    schema: 'campfire.action-grant/v1',
    audience: 'urn:steamcloud:agent',
    attempt_id: 'attempt_demo',
    idempotency_key: 'intent_demo',
    arguments_sha256: hashArguments({}),
    operation: 'asf.steam.webapi.fetch',
    lease_fences: {},
    ...overrides,
  };
}

test('createMockRuntime wires one lease book into the agent', () => {
  const runtime = createMockRuntime();
  const lease = runtime.leaseBook.acquire('steam-account:acct_demo', 'run/work');
  const result = runtime.agent.execute(
    grant({
      arguments_sha256: hashArguments({ subject: 's' }),
      lease_fences: { [lease.resourceKey]: lease.generation },
    }),
    { subject: 's' },
  );
  assert.equal(result.outcome, 'COMPLETED');
  assert.equal(runtime.agent.leaseBook, runtime.leaseBook);
});

test('duplicate delivery replays one logical settlement', () => {
  const { leaseBook, agent } = createMockRuntime();
  const lease = leaseBook.acquire('steam-account:acct_demo', 'run_demo/work_demo');
  const args = { subject: 'steam:76561198000000000' };
  const request = grant({
    arguments_sha256: hashArguments(args),
    operation: 'asf.steam.webapi.fetch',
    lease_fences: { [lease.resourceKey]: lease.generation },
  });
  assert.equal(agent.execute(request, args).replayed, false);
  assert.equal(agent.execute(request, args).replayed, true);
});

test('stale lease generation is rejected', () => {
  const { leaseBook, agent } = createMockRuntime();
  const lease = leaseBook.acquire('steam-account:acct_demo', 'r/w');
  assert.throws(
    () => agent.execute(grant({
      operation: 'asf.account.session_status',
      lease_fences: { [lease.resourceKey]: lease.generation + 1 },
    }), {}),
    /stale/,
  );
});

test('owner-edge operations cannot run on the regional mock agent', () => {
  const { leaseBook, agent } = createMockRuntime();
  const lease = leaseBook.acquire('steam-account:acct_demo', 'r/w');
  assert.throws(
    () => agent.execute(grant({
      operation: 'asf.owner.edge.fetch',
      lease_fences: { [lease.resourceKey]: lease.generation },
    }), {}),
    /owner edge action cannot execute in regional agent/,
  );
});

test('agent requires a grant envelope and audience', () => {
  const { agent } = createMockRuntime();
  assert.throws(() => agent.execute({ audience: 'urn:steamcloud:agent' }, {}), /invalid action grant/);
  assert.throws(
    () => agent.execute({ schema: 'campfire.action-grant/v1', audience: 'urn:other' }, {}),
    /wrong audience/,
  );
});

test('lease book rejects a second owner and a stale release', () => {
  const book = new ResourceLeaseBook();
  const lease = book.acquire('steam-account:acct_demo', 'owner-a');
  assert.equal(book.acquire('steam-account:acct_demo', 'owner-a'), lease);
  assert.throws(() => book.acquire('steam-account:acct_demo', 'owner-b'), /resource busy/);
  book.release(lease);
  assert.throws(() => book.release(lease), /stale lease release/);
});

test('MockSteamAgent requires a lease book', () => {
  assert.throws(() => new MockSteamAgent({}), /lease book is required/);
});
