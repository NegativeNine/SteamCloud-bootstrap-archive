import test from 'node:test';
import assert from 'node:assert/strict';
import { projectWorldView } from '../src/index.js';

test('WorldView takes monotonic generations', () => {
  const view = projectWorldView([
    {
      account_id: 'acct_demo',
      tenant_id: 'ten_demo',
      runtime_generation: 4,
      credential_generation: 2,
      runtime_state: 'online',
      steam_state: 'logged_on',
    },
    {
      account_id: 'acct_demo',
      tenant_id: 'ten_demo',
      runtime_generation: 3,
      credential_generation: 1,
      runtime_state: 'online',
    },
  ]);
  assert.equal(view.runtime_generation, 4);
  assert.equal(view.credential_generation, 2);
  assert.equal(view.steam_state, 'logged_on');
});

test('WorldView requires account and tenant identity', () => {
  assert.throws(() => projectWorldView([{ runtime_generation: 1 }]), /incomplete WorldView identity/);
  assert.throws(() => projectWorldView([{ account_id: 'acct_demo' }]), /incomplete WorldView identity/);
});
