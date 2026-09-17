# Organizational Knowledge Pattern

## Definition

Organizational knowledge is approved business meaning used by software: policies, taxonomies, rubrics, criteria, reference data, role definitions, classifications, thresholds, and governed prompt templates.

## Authority

- LLMs may discover candidates, draft language, normalize, compare, and propose changes.
- Humans curate, approve, reject, and freeze authoritative versions.
- Runtime services consume identified frozen versions.
- Historical results retain the exact version used.

## Lifecycle

```text
Proposal -> Human Review -> Approval -> Frozen Version -> Use -> Supersession
```

Approved versions are immutable. Change creates a new version. Supersession does not erase history.

## Requirements

Each authoritative version should carry identity, version, effective date, status, provenance, approver, canonical content or fingerprint, and supersession relationships.
