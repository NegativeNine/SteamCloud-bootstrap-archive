export function projectWorldView(events) {
  const state = {
    schema:'steamcloud.world-view/v1', account_id:null, tenant_id:null,
    runtime_state:'absent', steam_state:'unlinked', web_session_state:'absent',
    gc_state:'disconnected', runtime_id:null, egress_id:null,
    runtime_generation:0, credential_generation:0, active_challenge_id:null,
    observed_at:'2026-08-18T16:00:00Z',
  };
  for (const event of events) {
    if (event.account_id) state.account_id = event.account_id;
    if (event.tenant_id) state.tenant_id = event.tenant_id;
    if (event.runtime_state) state.runtime_state = event.runtime_state;
    if (event.steam_state) state.steam_state = event.steam_state;
    if (event.runtime_generation != null) state.runtime_generation = Math.max(state.runtime_generation, event.runtime_generation);
    if (event.credential_generation != null) state.credential_generation = Math.max(state.credential_generation, event.credential_generation);
    state.observed_at = event.observed_at ?? state.observed_at;
  }
  if (!state.account_id || !state.tenant_id) throw new Error('incomplete WorldView identity');
  return Object.freeze(state);
}
