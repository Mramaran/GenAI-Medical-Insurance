"""Web3.py interaction with the ClaimChain smart contract on Sepolia."""

import json
import os
import time

from dotenv import load_dotenv

load_dotenv()

# ── Configuration ───────────────────────────────────────────────────────
SEPOLIA_RPC_URL = os.getenv("SEPOLIA_RPC_URL", "")
WALLET_PRIVATE_KEY = os.getenv("WALLET_PRIVATE_KEY", "")
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS", "")

# Ordered by reliability — free RPCs that don't require API keys come first,
# then the user-configured URL (which may be Alchemy/Infura with a key).
_FALLBACK_RPCS = [
    "https://rpc.ankr.com/eth_sepolia",
    "https://ethereum-sepolia-rpc.publicnode.com",
    "https://sepolia.drpc.org",
    "https://rpc.sepolia.org",
    "https://eth-sepolia.public.blastapi.io",
]

# ── Lazy-loaded web3 instances ──────────────────────────────────────────
_w3 = None
_contract = None
_account = None


def _try_connect(rpc_url: str):
    """Attempt to connect to a single RPC URL. Returns Web3 instance or None."""
    from web3 import Web3

    try:
        w3 = Web3(Web3.HTTPProvider(rpc_url, request_kwargs={"timeout": 10}))
        if w3.is_connected():
            print(f"[blockchain] Connected to Sepolia via {rpc_url}")
            return w3
    except Exception:
        pass
    return None


def _get_web3():
    """Lazy-initialize web3 connection with automatic RPC fallback."""
    global _w3, _contract, _account

    if _w3 is not None:
        # Verify existing connection is still alive
        try:
            if _w3.is_connected():
                return _w3, _contract, _account
        except Exception:
            pass
        # Connection died — reset and reconnect
        _w3 = None
        _contract = None
        _account = None

    from web3 import Web3

    # Build list of RPCs to try: user-configured first (if set), then fallbacks
    rpcs_to_try = []
    if SEPOLIA_RPC_URL:
        rpcs_to_try.append(SEPOLIA_RPC_URL)
    rpcs_to_try.extend(url for url in _FALLBACK_RPCS if url not in rpcs_to_try)

    # Try each RPC until one connects
    for rpc_url in rpcs_to_try:
        _w3 = _try_connect(rpc_url)
        if _w3 is not None:
            break

    if _w3 is None:
        tried = ", ".join(rpcs_to_try[:3])
        raise ConnectionError(
            f"Cannot connect to any Sepolia RPC. Tried: {tried}... "
            f"Check your internet connection, or set SEPOLIA_RPC_URL in .env "
            f"to an Alchemy/Infura endpoint (free tier)."
        )

    # Load ABI
    abi_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "..", "blockchain", "abi", "ClaimChain.json")
    )
    with open(abi_path, "r") as f:
        abi = json.load(f)

    _contract = _w3.eth.contract(
        address=Web3.to_checksum_address(CONTRACT_ADDRESS),
        abi=abi,
    )

    if WALLET_PRIVATE_KEY:
        _account = _w3.eth.account.from_key(WALLET_PRIVATE_KEY)
    else:
        _account = None

    return _w3, _contract, _account


def _is_configured() -> bool:
    """Check if blockchain credentials are configured."""
    return bool(WALLET_PRIVATE_KEY and CONTRACT_ADDRESS)


def submit_claim_meta(claim_id: str, merkle_root: str) -> dict:
    """
    Call submitClaimMeta() on the ClaimChain contract.

    Args:
        claim_id: e.g. "CLM-20260303-001"
        merkle_root: hex string like "0xabc123..."

    Returns:
        dict with tx_hash, block_number, gas_used — or error info.
    """
    if not _is_configured():
        return {
            "tx_hash": None,
            "block_number": None,
            "gas_used": None,
            "error": "Blockchain not configured (missing WALLET_PRIVATE_KEY or CONTRACT_ADDRESS in .env)",
        }

    try:
        w3, contract, account = _get_web3()

        # Convert merkle_root hex string to bytes32
        merkle_bytes = bytes.fromhex(merkle_root.replace("0x", "").ljust(64, "0"))

        # Build transaction
        nonce = w3.eth.get_transaction_count(account.address)
        tx = contract.functions.submitClaimMeta(
            claim_id, merkle_bytes
        ).build_transaction({
            "from": account.address,
            "nonce": nonce,
            "gas": 300000,
            "gasPrice": w3.eth.gas_price,
            "chainId": 11155111,  # Sepolia chain ID
        })

        # Sign and send
        signed = account.sign_transaction(tx)
        tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=60)

        return {
            "tx_hash": receipt.transactionHash.hex(),
            "block_number": receipt.blockNumber,
            "gas_used": receipt.gasUsed,
            "error": None,
        }

    except Exception as e:
        return {
            "tx_hash": None,
            "block_number": None,
            "gas_used": None,
            "error": str(e),
        }


def update_claim_status(claim_id: str, status: int, reason_hash: str) -> dict:
    """
    Call updateStatus() on the ClaimChain contract.

    Args:
        claim_id: The claim to update.
        status: Enum int (0=Submitted, 1=UnderReview, 2=Approved, 3=Rejected, 4=QueryRaised, 5=Settled).
        reason_hash: SHA-256 hex hash of the reason text.

    Returns:
        dict with tx_hash, block_number — or error info.
    """
    if not _is_configured():
        return {
            "tx_hash": None,
            "block_number": None,
            "error": "Blockchain not configured",
        }

    try:
        w3, contract, account = _get_web3()

        reason_bytes = bytes.fromhex(reason_hash.replace("0x", "").ljust(64, "0"))

        nonce = w3.eth.get_transaction_count(account.address)
        tx = contract.functions.updateStatus(
            claim_id, status, reason_bytes
        ).build_transaction({
            "from": account.address,
            "nonce": nonce,
            "gas": 200000,
            "gasPrice": w3.eth.gas_price,
            "chainId": 11155111,
        })

        signed = account.sign_transaction(tx)
        tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=60)

        return {
            "tx_hash": receipt.transactionHash.hex(),
            "block_number": receipt.blockNumber,
            "error": None,
        }

    except Exception as e:
        return {
            "tx_hash": None,
            "block_number": None,
            "error": str(e),
        }


def get_claim_events(claim_id: str) -> list[dict]:
    """
    Read ClaimSubmitted and StatusUpdated events for a given claimId.

    Uses get_logs with a bounded block range to stay within RPC provider
    limits (most free RPCs cap at 50,000 blocks per query).

    Returns:
        List of event dicts with event_type, tx_hash, block_number, timestamp, data.
    """
    if not _is_configured():
        return []

    try:
        w3, contract, _ = _get_web3()

        # Free RPCs enforce a max block range (typically 50k).
        # Scan only the last 49,000 blocks — the contract was deployed recently
        # so all its events are well within this window.
        latest_block = w3.eth.block_number
        from_block = max(0, latest_block - 49_000)

        events = []
        status_names = ["Submitted", "UnderReview", "Approved", "Rejected", "QueryRaised", "Settled"]

        # Get ClaimSubmitted events using get_logs (more compatible than create_filter)
        submitted_logs = contract.events.ClaimSubmitted.get_logs(
            from_block=from_block, to_block="latest"
        )
        for log in submitted_logs:
            if log.args.claimId == claim_id:
                block = w3.eth.get_block(log.blockNumber)
                events.append({
                    "event_type": "ClaimSubmitted",
                    "tx_hash": log.transactionHash.hex(),
                    "block_number": log.blockNumber,
                    "timestamp": block.timestamp,
                    "data": {
                        "claim_id": log.args.claimId,
                        "merkle_root": log.args.merkleRoot.hex(),
                        "submitter": log.args.submitter,
                    },
                })

        # Get StatusUpdated events
        status_logs = contract.events.StatusUpdated.get_logs(
            from_block=from_block, to_block="latest"
        )
        for log in status_logs:
            if log.args.claimId == claim_id:
                block = w3.eth.get_block(log.blockNumber)
                events.append({
                    "event_type": "StatusUpdated",
                    "tx_hash": log.transactionHash.hex(),
                    "block_number": log.blockNumber,
                    "timestamp": block.timestamp,
                    "data": {
                        "claim_id": log.args.claimId,
                        "old_status": status_names[log.args.oldStatus] if log.args.oldStatus < len(status_names) else str(log.args.oldStatus),
                        "new_status": status_names[log.args.newStatus] if log.args.newStatus < len(status_names) else str(log.args.newStatus),
                        "reason_hash": log.args.reasonHash.hex(),
                    },
                })

        # Sort by block number
        events.sort(key=lambda e: e["block_number"])
        return events

    except Exception as e:
        return [{"event_type": "error", "error": str(e)}]
