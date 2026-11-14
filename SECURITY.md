# Security policy

Report a vulnerability privately. Do not open a public GitHub issue for a security report, and do not include secret values, tokens, passwords, or private keys in the report.

## How to report

1. Use GitHub private vulnerability reporting: <https://github.com/galion-studio/nexuslang-v2/security/advisories/new>
2. Or email <security@nexuslang.dev>, which is the contact published in [`.well-known/security.txt`](.well-known/security.txt).

Say what is affected, how to reproduce it, and the impact you observed. If you want to be credited, say so.

The published response targets are in `.well-known/security.txt`. This file does not add a different schedule.

## Credential rotation

Rewriting git history does not revoke a credential that was already exposed. The owner still needs to rotate the nexuscore database password, the RunPod API key, and the Twitter bearer token. Details, with no secret values, are in [docs/credential-rotation.md](docs/credential-rotation.md).
