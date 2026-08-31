import hashlib
import pytest

def generate_sha256(data: bytes) -> str:
    """Helper to generate SHA-256 hash."""
    hasher = hashlib.sha256()
    hasher.update(data)
    return hasher.hexdigest()

def test_hash_integrity_single_byte_alteration():
    """
    Test INT-HASH-001: A single byte alteration in a binary document 
    should produce a completely different SHA-256 hash, marking it as corrupt.
    """
    # Simulated PDF content
    original_data = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
    
    # Calculate original hash
    original_hash = generate_sha256(original_data)
    
    # Alter exactly 1 byte (change 'P' to 'Q')
    altered_data = b"%QDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
    
    # Calculate altered hash
    altered_hash = generate_sha256(altered_data)
    
    assert original_hash != altered_hash, "Hash should change when 1 byte is altered."

def test_hash_is_deterministic():
    """
    Verify that generating a hash for the same file twice produces the same result.
    """
    data = b"Dummy data for deterministic check."
    
    hash_1 = generate_sha256(data)
    hash_2 = generate_sha256(data)
    
    assert hash_1 == hash_2, "Hashes of the same data should be identical."
