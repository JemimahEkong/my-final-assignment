# Retention policy

**Filled by:** session 11.

STORED: Per-user application memory values associated with an explicit user ID and key.

WHY: Stored values allow the assistant to retain useful user-specific context without mixing one user's memory with another user's memory.

CORRECTED BY: A user can correct or replace a stored value by remembering a new value for the same key.

EXPIRES: Memory is bounded by the application's retention policy and must not be treated as permanent storage; sensitive information is not intentionally retained.

WE REFUSE TO REMEMBER: API keys, tokens, passwords, secrets, and other sensitive credentials.

## How the code enforces it

`MemoryStore` requires a non-empty user ID, keeps values keyed by user and key, and uses defensive copies on both remember and recall so callers cannot mutate stored memory through a shared reference. The contract is covered by `test_memory_is_capped_reset_and_kept_per_user` in `tests/test_contract.py`.
