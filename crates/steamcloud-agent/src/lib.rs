use async_trait::async_trait;
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ActionGrant {
    pub attempt_id: String,
    pub action_intent_id: String,
    pub operation: String,
    pub arguments_sha256: String,
    pub account_id: Option<String>,
    pub credential_generation: u64,
    pub runtime_generation: u64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum SettlementOutcome { Completed, Failed, Retryable, Waiting, Declined, Unsupported, Uncertain }

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Settlement { pub attempt_id: String, pub outcome: SettlementOutcome, pub result_digest: Option<String> }

#[async_trait]
pub trait SteamActionAdapter: Send + Sync {
    async fn execute(&self, grant: &ActionGrant, canonical_arguments: &[u8]) -> Result<Settlement, String>;
    async fn reconcile(&self, grant: &ActionGrant) -> Result<Settlement, String>;
}

pub fn validate_generation(grant: &ActionGrant, runtime: u64, credential: u64) -> Result<(), String> {
    if grant.runtime_generation != runtime { return Err("stale runtime generation".into()); }
    if grant.credential_generation != credential { return Err("stale credential generation".into()); }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn stale_generation_rejected() {
        let grant = ActionGrant { attempt_id:"a".into(), action_intent_id:"i".into(), operation:"x".into(), arguments_sha256:"h".into(), account_id:None, credential_generation:2, runtime_generation:3 };
        assert!(validate_generation(&grant, 4, 2).is_err());
    }
}
