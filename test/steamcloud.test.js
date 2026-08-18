import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { admitOperation, compilePack, hashArguments } from '../src/profile.js';
import { ResourceLeaseBook } from '../src/resource-leases.js';
import { MockSteamAgent } from '../src/mock-agent.js';
import { projectWorldView } from '../src/projector.js';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');

test('removed operation cannot be admitted', () => {
  assert.throws(() => admitOperation({operation:'steam.synthetic_gameplay',accountClass:'TEST_CANARY',arguments:{}}), /blocked/);
});

test('operation arguments cannot carry credential material', () => {
  assert.throws(() => admitOperation({operation:'steam.profile.public.refresh',accountClass:'PLATFORM_PUBLIC_BOT',arguments:{api_key:'x'}}), /forbidden/);
});

test('all data-only packs compile', () => {
  for (const name of fs.readdirSync(path.join(ROOT,'packs'))) {
    if (!name.endsWith('.json')) continue;
    const pack = JSON.parse(fs.readFileSync(path.join(ROOT,'packs',name),'utf8'));
    assert.equal(compilePack(pack).compiled, true);
  }
});

test('duplicate delivery replays one logical settlement', () => {
  const leases = new ResourceLeaseBook();
  const lease = leases.acquire('steam-account:acct_demo','run_demo/work_demo');
  const agent = new MockSteamAgent({leaseBook:leases});
  const args = {subject:'steam:76561198000000000'};
  const grant = {
    schema:'campfire.action-grant/v1', audience:'urn:steamcloud:agent', attempt_id:'attempt_demo',
    idempotency_key:'intent_demo', arguments_sha256:hashArguments(args), operation:'asf.steam.webapi.fetch',
    lease_fences:{[lease.resourceKey]:lease.generation},
  };
  assert.equal(agent.execute(grant,args).replayed,false);
  assert.equal(agent.execute(grant,args).replayed,true);
});

test('stale lease generation is rejected', () => {
  const leases = new ResourceLeaseBook();
  const lease = leases.acquire('steam-account:acct_demo','r/w');
  const agent = new MockSteamAgent({leaseBook:leases});
  assert.throws(() => agent.execute({schema:'campfire.action-grant/v1',audience:'urn:steamcloud:agent',attempt_id:'a',idempotency_key:'i',arguments_sha256:hashArguments({}),operation:'asf.account.session_status',lease_fences:{[lease.resourceKey]:lease.generation+1}},{}), /stale/);
});

test('WorldView takes monotonic generations', () => {
  const view = projectWorldView([
    {account_id:'acct_demo',tenant_id:'ten_demo',runtime_generation:4,credential_generation:2,runtime_state:'online',steam_state:'logged_on'},
    {account_id:'acct_demo',tenant_id:'ten_demo',runtime_generation:3,credential_generation:1,runtime_state:'online'},
  ]);
  assert.equal(view.runtime_generation,4);
  assert.equal(view.credential_generation,2);
});
