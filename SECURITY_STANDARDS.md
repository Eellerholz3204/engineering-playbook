# Security Standards

Sensitive values must not be persisted, printed, logged, committed, embedded in prompts, or copied into evidence excerpts.

Protected material includes passwords, access keys, secret keys, session tokens, OAuth tokens, authorization headers, private keys, database credentials, secret environment values, Terraform state, cloud plans, and `.env` contents.

Collectors and processors should apply bounded limits, path validation, traversal rejection, binary rejection where appropriate, secret detection, visible collection gaps, and redaction before persistence.

When compromised historical evidence is discovered, stop downstream work, preserve an audit record, sanitize or remove affected local material when authorized, identify an authoritative replacement, add a regression test, and rerun security validation.
