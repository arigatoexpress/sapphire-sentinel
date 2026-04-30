// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/// @title EncryptedRiskGateMock
/// @notice Plain-Solidity stand-in for the Zama FHEVM risk gate.
/// @dev This contract is intentionally not an FHE contract. It gives the repo a
///      compilable local artifact with the same public interface Sentinel wants
///      from a future Zama Sepolia deployment: submit an opaque encrypted input
///      commitment, then export a risk commitment for the public receipt path.
contract EncryptedRiskGateMock {
    struct RiskDecision {
        bytes32 encryptedInputCommitment;
        bytes32 riskCommitment;
        bool allowed;
        uint64 createdAt;
    }

    mapping(bytes32 decisionId => RiskDecision decision) public decisions;

    event RiskEvaluated(
        bytes32 indexed decisionId,
        bytes32 indexed encryptedInputCommitment,
        bytes32 riskCommitment,
        bool allowed
    );

    function evaluateEncryptedRisk(
        bytes32 decisionId,
        bytes32 encryptedInputCommitment,
        bytes32 policyHash,
        bytes32 resourceHash,
        bool allowed
    ) external returns (bytes32 riskCommitment) {
        require(decisionId != bytes32(0), "Zero decision");
        require(encryptedInputCommitment != bytes32(0), "Zero input");
        require(decisions[decisionId].createdAt == 0, "Decision exists");

        riskCommitment = keccak256(
            abi.encode(
                "sapphire-sentinel-zama-risk-v1",
                encryptedInputCommitment,
                policyHash,
                resourceHash,
                allowed
            )
        );
        decisions[decisionId] = RiskDecision({
            encryptedInputCommitment: encryptedInputCommitment,
            riskCommitment: riskCommitment,
            allowed: allowed,
            createdAt: uint64(block.timestamp)
        });
        emit RiskEvaluated(decisionId, encryptedInputCommitment, riskCommitment, allowed);
    }
}
