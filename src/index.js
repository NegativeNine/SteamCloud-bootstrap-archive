import { MockSteamAgent } from './mock-agent.js';
import { ResourceLeaseBook } from './resource-leases.js';

export { assertNoSecretFields, FORBIDDEN_FIELDS } from './secrets.js';
export {
  REGIONAL_AGENT_EXCLUDED_OPERATIONS,
  admitOperation,
  assertRegionalAgentMayExecute,
  compilePack,
  hashArguments,
} from './operations.js';
export { loadOperationCatalog, loadPacks, packageRoot } from './catalog.js';
export { ResourceLeaseBook } from './resource-leases.js';
export { MockSteamAgent } from './mock-agent.js';
export { projectWorldView } from './projector.js';

export function createMockRuntime({ leaseBook } = {}) {
  const book = leaseBook ?? new ResourceLeaseBook();
  return { leaseBook: book, agent: new MockSteamAgent({ leaseBook: book }) };
}
