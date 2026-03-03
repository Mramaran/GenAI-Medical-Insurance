# ClaimChain Smart Contract

## Overview

Solidity contract deployed on Ethereum Sepolia testnet. Stores cryptographic proofs (Merkle roots) of AI coverage verdicts and tracks claim status changes as immutable on-chain events.

## Contract: `ClaimChain.sol`

### Functions

| Function | Access | Description |
|----------|--------|-------------|
| `submitClaimMeta(claimId, merkleRoot)` | Anyone | Submit a new claim with its Merkle root |
| `updateStatus(claimId, newStatus, reasonHash)` | Owner only | Update claim status (insurer action) |
| `getClaimRecord(claimId)` | View | Get core claim data |
| `getStatusHistory(claimId)` | View | Get full status change history |

### Status Enum

| Value | Name | Description |
|-------|------|-------------|
| 0 | Submitted | AI verdict committed on-chain |
| 1 | UnderReview | Insurer is reviewing |
| 2 | Approved | Insurer approved the claim |
| 3 | Rejected | Insurer rejected the claim |
| 4 | QueryRaised | Insurer needs more information |
| 5 | Settled | Payment settled |

### Events

- `ClaimSubmitted(claimId, merkleRoot, submitter, timestamp)`
- `StatusUpdated(claimId, oldStatus, newStatus, reasonHash, timestamp)`

## Deployment

### Using Remix IDE (Recommended)

1. Open [remix.ethereum.org](https://remix.ethereum.org)
2. Create a new file, paste `contracts/ClaimChain.sol`
3. Compile with Solidity 0.8.19+
4. In Deploy tab: select "Injected Provider - MetaMask"
5. Ensure MetaMask is on **Sepolia testnet**
6. Click Deploy
7. Copy the deployed contract address
8. Copy the ABI from Compilation Details -> ABI

### After Deployment

1. Save the ABI to `abi/ClaimChain.json`
2. Update the values below:

```
CONTRACT_ADDRESS=<paste deployed address here>
DEPLOYER_ADDRESS=<your MetaMask wallet address>
NETWORK=Sepolia
```

### Getting Sepolia ETH

- [Google Cloud Faucet](https://cloud.google.com/application/web3/faucet/ethereum/sepolia)
- [Alchemy Faucet](https://sepoliafaucet.com/)
- [Infura Faucet](https://www.infura.io/faucet/sepolia)

### Testing in Remix

After deploying, test these calls in order:

1. `submitClaimMeta("TEST-001", 0xabc...)` - verify ClaimSubmitted event
2. `getClaimRecord("TEST-001")` - verify data returned
3. `updateStatus("TEST-001", 2, 0xdef...)` - verify StatusUpdated event
4. `getStatusHistory("TEST-001")` - verify 2 entries in history
