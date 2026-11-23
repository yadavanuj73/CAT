# Security Architecture & Acceptance Specification

## 1. Threat Model & Asset Protection

| Asset | Sensitivity | Mitigation |
|---|---|---|
| User OpenAI API Key | Critical | Ephemeral in-memory storage (default) or AES-256-GCM (opt-in); zero logging |
| User Password | High | bcrypt hashing with 12 salt rounds |
| JWT Access Tokens | High | Signed with HS256, stored in httpOnly SameSite cookies or Bearer header |
| Uploaded Question Papers | Medium | Magic byte (%PDF) check, SHA-256 dedup, 50MB ceiling, untrusted text handling |

---

## 2. The 10 Security Acceptance Controls

| # | Control | Implementation | Verification Test |
|---|---|---|---|
| 1 | No API keys in frontend bundles | Keys never passed to frontend; masked strings only (`sk-...a1b2`) | `test_1_and_2_inspect_frontend_for_secret_leakage` |
| 2 | No secrets in browser storage | Auth token in httpOnly cookie; API key never placed in storage | Code audit + regex bundle test |
| 3 | Exception & log redaction | `redact_secrets` strips `sk-...` patterns across all error messages | `test_3_and_10_redact_secrets_in_exception_traces` |
| 4 | Cross-user session isolation | Session key store indexed by `(user_id, session_id)` tuple | `test_4_cross_user_isolation` |
| 5 | Logout credential invalidation | `POST /api/auth/logout` explicitly deletes session RAM key | `test_5_logout_credential_invalidation` |
| 6 | Session expiration | In-memory keys carry timestamp and auto-purge after expiry | `test_6_session_expiration` |
| 7 | Server restart volatile purging | Volatile RAM store loses all state upon container stop/restart | `test_7_server_restart_behavior` |
| 8 | Encrypted credential deletion | `DELETE /api/keys` deletes row from `encrypted_credentials` | `test_8_encrypted_credential_roundtrip_and_deletion` |
| 9 | Unauthorized credential retrieval | `GET /api/keys/status` returns status + masked key only | `test_9_unauthorized_credential_retrieval` |
| 10 | Error response safety | Global FastAPI exception handler redacts secrets before 500 response | Unit tested in pytest suite |
