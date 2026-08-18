import test from 'node:test';
import assert from 'node:assert/strict';
import {
  admitOperation,
  compilePack,
  hashArguments,
  loadOperationCatalog,
  loadPacks,
} from '../src/index.js';

const catalog = loadOperationCatalog();

test('argument hashes are canonical', () => {
  assert.equal(
    hashArguments({}),
    '44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a',
  );
  assert.equal(
    hashArguments({ subject: 'steam:76561198000000000' }),
    'a704d5abd7877401870e7ed917433999c730907f9bf583d9a7d1e01067c0612b',
  );
  assert.equal(hashArguments({ b: 1, a: 2 }), hashArguments({ a: 2, b: 1 }));
});

test('admit requires an explicit catalog', () => {
  assert.throws(
    () => admitOperation({ operation: 'steam.profile.public.refresh', accountClass: 'PLATFORM_PUBLIC_BOT', arguments: {} }),
    /operation catalog is required/,
  );
});

test('enabled public refresh is admitted', () => {
  const args = { subject: 'steam:76561198000000000' };
  const admitted = admitOperation(
    { operation: 'steam.profile.public.refresh', accountClass: 'PLATFORM_PUBLIC_BOT', arguments: args },
    catalog,
  );
  assert.equal(admitted.definition.operation, 'steam.profile.public.refresh');
  assert.equal(admitted.arguments_sha256, hashArguments(args));
});

test('removed operation cannot be admitted', () => {
  assert.throws(
    () => admitOperation({ operation: 'steam.synthetic_gameplay', accountClass: 'TEST_CANARY', arguments: {} }, catalog),
    /blocked/,
  );
});

test('valve-gated operation cannot be admitted', () => {
  assert.throws(
    () => admitOperation({ operation: 'steam.gc.self.snapshot', accountClass: 'PLATFORM_GC_CANARY', arguments: {} }, catalog),
    /VALVE_APPROVAL_REQUIRED/,
  );
});

test('unknown operation cannot be admitted', () => {
  assert.throws(
    () => admitOperation({ operation: 'steam.not.a.thing', accountClass: 'TEST_CANARY', arguments: {} }, catalog),
    /unknown operation/,
  );
});

test('account class must be listed on the operation', () => {
  assert.throws(
    () => admitOperation({ operation: 'steam.profile.public.refresh', accountClass: 'CUSTOMER_LINKED', arguments: {} }, catalog),
    /account class not allowed/,
  );
});

test('operation arguments cannot carry credential material', () => {
  assert.throws(
    () => admitOperation(
      { operation: 'steam.profile.public.refresh', accountClass: 'PLATFORM_PUBLIC_BOT', arguments: { api_key: 'x' } },
      catalog,
    ),
    /forbidden/,
  );
});

test('operation arguments cannot carry player or pairing tokens', () => {
  assert.throws(
    () => admitOperation(
      { operation: 'steam.profile.public.refresh', accountClass: 'PLATFORM_PUBLIC_BOT', arguments: { player_token: 'x' } },
      catalog,
    ),
    /forbidden/,
  );
});

test('all data-only packs compile', () => {
  for (const pack of loadPacks()) {
    assert.equal(compilePack(pack).compiled, true);
  }
});

test('compilePack rejects the wrong profile and broken graphs', () => {
  assert.throws(() => compilePack({ schema: 'campfire.pack/v1', profile: 'other', steps: [] }), /wrong pack profile/);
  assert.throws(
    () => compilePack({
      schema: 'campfire.pack/v1',
      profile: 'steamcloud',
      steps: [
        { id: 'a', needs: [] },
        { id: 'a', needs: [] },
      ],
    }),
    /duplicate step id/,
  );
  assert.throws(
    () => compilePack({
      schema: 'campfire.pack/v1',
      profile: 'steamcloud',
      steps: [{ id: 'fetch', needs: ['lease'] }],
    }),
    /dependency lease not yet declared/,
  );
});
