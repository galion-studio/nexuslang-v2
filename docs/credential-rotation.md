# Credential rotation

The owner must rotate these credentials. They were exposed, and rewriting git history does not invalidate them. This note does not contain the values, and it does not rotate anything.

- Nexuscore database password
- RunPod API key
- Twitter bearer token

Rotate each one at the place that issued it (the database, RunPod, and the Twitter developer app). Then update the private environment that uses it. Do not commit the new values.

A gitleaks 8.28.0 scan of the 9 commits on `main` reported 129 findings. `.gitleaks.toml` allowlists only documented placeholders (example tokens such as `YOUR_TOKEN`, test JWT strings, and truncated `eyJ...` samples). It does not allowlist live credentials. Findings that remain include cloud API material in `v1/galion/k8s/secrets.yaml` and `env.production.template`, OpenRouter-style keys in deploy scripts, and hardcoded defaults in `v2/backend/core/auth.py`. Treat those as exposed and rotate them as well.

The GitHub Actions job scans commits added by a push or pull request. It does not rewrite history and it does not change repository settings.
