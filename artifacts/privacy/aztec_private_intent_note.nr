// Sapphire Sentinel Aztec private-intent blueprint.
//
// This Noir sketch is intentionally not wired into the Python demo yet. It
// captures the public/private boundary we want from Aztec:
// - private: mandate secret, user salt, private balance, risk score
// - public: policy hash, resource hash, risk threshold, exported commitment
//
// The hackathon claim is a blueprint/private-intent artifact, not a deployed
// Aztec production contract.

fn main(
    private_mandate_secret: Field,
    private_user_salt: Field,
    private_balance_atomic: Field,
    private_risk_score_bps: Field,
    public_policy_hash: pub Field,
    public_resource_hash: pub Field,
    public_max_risk_bps: pub Field,
    public_min_balance_atomic: pub Field,
) -> pub Field {
    assert(private_balance_atomic >= public_min_balance_atomic);
    assert(private_risk_score_bps <= public_max_risk_bps);

    let commitment = std::hash::pedersen_hash([
        private_mandate_secret,
        private_user_salt,
        private_balance_atomic,
        private_risk_score_bps,
        public_policy_hash,
        public_resource_hash,
    ]);

    commitment
}
