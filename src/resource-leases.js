import crypto from 'node:crypto';

export class ResourceLeaseBook {
  #generation = new Map();
  #active = new Map();

  acquire(resourceKey, owner) {
    const current = this.#active.get(resourceKey);
    if (current && current.owner !== owner) throw new Error(`resource busy: ${resourceKey}`);
    if (current) return current;
    const generation = (this.#generation.get(resourceKey) ?? 0) + 1;
    this.#generation.set(resourceKey, generation);
    const fence = crypto.createHash('sha256').update(`${resourceKey}:${generation}:${owner}`).digest('hex');
    const lease = Object.freeze({resourceKey, owner, generation, fence});
    this.#active.set(resourceKey, lease);
    return lease;
  }

  release(lease) {
    if (this.#active.get(lease.resourceKey) !== lease) throw new Error('stale lease release');
    this.#active.delete(lease.resourceKey);
  }

  require(resourceKey, generation) {
    const current = this.#active.get(resourceKey);
    if (!current || current.generation !== generation) throw new Error(`stale fence: ${resourceKey}`);
    return current;
  }
}
