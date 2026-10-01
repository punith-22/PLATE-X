# PLATE-X Architecture

Client -> FastAPI -> Services -> Authorized Connectors -> Data Store

## Privacy boundary

Owner identity data is protected. The default API performs registration-format validation only.

Future connectors must enforce:
- authentication
- authorization
- purpose limitation
- field minimization
- audit logging
- provider terms
- retention rules

## Evidence

Evidence ingestion will calculate SHA-256 hashes and maintain an audit trail.

## Modules

- Vehicle intelligence
- Cases
- Evidence
- Authorized connectors
- Audit
- Reporting
