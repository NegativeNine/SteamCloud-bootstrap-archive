import spec from '../schemas/forbidden-fields.json' with { type: 'json' };

export const FORBIDDEN_FIELDS = Object.freeze(
  new Set(spec.keys.map((key) => key.toLowerCase())),
);

export function assertNoSecretFields(value, trail = '') {
  if (Array.isArray(value)) {
    value.forEach((item, index) => assertNoSecretFields(item, `${trail}/${index}`));
    return;
  }
  if (!value || typeof value !== 'object') return;
  for (const [key, child] of Object.entries(value)) {
    if (FORBIDDEN_FIELDS.has(key.toLowerCase())) {
      throw new Error(`forbidden field ${trail}/${key}`);
    }
    assertNoSecretFields(child, `${trail}/${key}`);
  }
}
