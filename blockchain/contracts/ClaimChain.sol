// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * @title ClaimChain
 * @notice Stores cryptographic proofs of AI coverage verdicts on-chain
 *         before the insurer sees them, giving patients a tamper-proof
 *         claim timeline.
 */
contract ClaimChain {
    // ── Enums ──────────────────────────────────────────────────────────
    enum ClaimStatus {
        Submitted,    // 0 – AI verdict committed
        UnderReview,  // 1 – Insurer is reviewing
        Approved,     // 2 – Insurer approved
        Rejected,     // 3 – Insurer rejected
        QueryRaised,  // 4 – Insurer needs more info
        Settled       // 5 – Payment settled
    }

    // ── Structs ────────────────────────────────────────────────────────
    struct StatusEntry {
        ClaimStatus status;
        bytes32 reasonHash;
        uint256 timestamp;
        address updatedBy;
    }

    struct ClaimRecord {
        bytes32 merkleRoot;
        ClaimStatus currentStatus;
        address submitter;
        uint256 submittedAt;
        StatusEntry[] statusHistory;
    }

    // ── State ──────────────────────────────────────────────────────────
    address public owner;
    mapping(string => ClaimRecord) private claims;
    mapping(string => bool) public claimExists;

    // ── Events ─────────────────────────────────────────────────────────
    event ClaimSubmitted(
        string claimId,
        bytes32 merkleRoot,
        address submitter,
        uint256 timestamp
    );

    event StatusUpdated(
        string claimId,
        ClaimStatus oldStatus,
        ClaimStatus newStatus,
        bytes32 reasonHash,
        uint256 timestamp
    );

    // ── Modifiers ──────────────────────────────────────────────────────
    modifier onlyOwner() {
        require(msg.sender == owner, "ClaimChain: caller is not the owner");
        _;
    }

    // ── Constructor ────────────────────────────────────────────────────
    constructor() {
        owner = msg.sender;
    }

    // ── External Functions ─────────────────────────────────────────────

    /**
     * @notice Submit a new claim with its Merkle root (hash of docs + verdict).
     * @param claimId  Unique claim identifier (e.g. "CLM-20260303-001")
     * @param merkleRoot SHA-256 Merkle root of document hashes + verdict hash
     */
    function submitClaimMeta(
        string calldata claimId,
        bytes32 merkleRoot
    ) external {
        require(merkleRoot != bytes32(0), "ClaimChain: merkle root cannot be zero");
        require(!claimExists[claimId], "ClaimChain: claim already exists");

        ClaimRecord storage record = claims[claimId];
        record.merkleRoot = merkleRoot;
        record.currentStatus = ClaimStatus.Submitted;
        record.submitter = msg.sender;
        record.submittedAt = block.timestamp;

        // First history entry
        record.statusHistory.push(StatusEntry({
            status: ClaimStatus.Submitted,
            reasonHash: merkleRoot,
            timestamp: block.timestamp,
            updatedBy: msg.sender
        }));

        claimExists[claimId] = true;

        emit ClaimSubmitted(claimId, merkleRoot, msg.sender, block.timestamp);
    }

    /**
     * @notice Update the status of an existing claim (insurer action).
     * @param claimId   The claim to update
     * @param newStatus The new status enum value
     * @param reasonHash SHA-256 hash of the reason text
     */
    function updateStatus(
        string calldata claimId,
        ClaimStatus newStatus,
        bytes32 reasonHash
    ) external onlyOwner {
        require(claimExists[claimId], "ClaimChain: claim does not exist");

        ClaimRecord storage record = claims[claimId];
        ClaimStatus oldStatus = record.currentStatus;
        record.currentStatus = newStatus;

        record.statusHistory.push(StatusEntry({
            status: newStatus,
            reasonHash: reasonHash,
            timestamp: block.timestamp,
            updatedBy: msg.sender
        }));

        emit StatusUpdated(claimId, oldStatus, newStatus, reasonHash, block.timestamp);
    }

    // ── View Functions ─────────────────────────────────────────────────

    /**
     * @notice Get the core claim record data.
     */
    function getClaimRecord(
        string calldata claimId
    )
        external
        view
        returns (
            bytes32 merkleRoot,
            ClaimStatus currentStatus,
            address submitter,
            uint256 submittedAt
        )
    {
        require(claimExists[claimId], "ClaimChain: claim does not exist");
        ClaimRecord storage record = claims[claimId];
        return (
            record.merkleRoot,
            record.currentStatus,
            record.submitter,
            record.submittedAt
        );
    }

    /**
     * @notice Get the full status history for a claim.
     */
    function getStatusHistory(
        string calldata claimId
    ) external view returns (StatusEntry[] memory) {
        require(claimExists[claimId], "ClaimChain: claim does not exist");
        return claims[claimId].statusHistory;
    }
}
