"""SHA-256 hashing and Merkle root computation for ClaimChain."""

import hashlib


def hash_file(file_path: str) -> str:
    """Read file bytes and return SHA-256 hex digest."""
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def hash_string(text: str) -> str:
    """Return SHA-256 hex digest of a UTF-8 string."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def hash_bytes(data: bytes) -> str:
    """Return SHA-256 hex digest of raw bytes."""
    return hashlib.sha256(data).hexdigest()


def compute_merkle_root(hashes: list[str]) -> str:
    """
    Compute a Merkle root from a list of hex hash strings.

    - Pairs adjacent hashes and computes SHA-256(hash_a + hash_b).
    - If odd number of leaves, duplicates the last hash.
    - Repeats until a single root remains.
    - Returns hex string prefixed with '0x' for blockchain compatibility.
    """
    if not hashes:
        return "0x" + "0" * 64

    # Work with raw hex strings (no 0x prefix internally)
    layer = [h.replace("0x", "") for h in hashes]

    while len(layer) > 1:
        if len(layer) % 2 == 1:
            layer.append(layer[-1])  # duplicate last if odd

        next_layer = []
        for i in range(0, len(layer), 2):
            combined = layer[i] + layer[i + 1]
            next_layer.append(hashlib.sha256(combined.encode("utf-8")).hexdigest())
        layer = next_layer

    return "0x" + layer[0]
