# Python Service Pattern

A Python service exposes a bounded capability through an explicit service or artifact
contract. Domain behavior remains independent of transport, persistence, cloud SDKs, and
model providers. Configuration is validated at startup, failures are observable, and
outputs retain sufficient provenance for audit and reproduction.

Services using probabilistic models must separate deterministic policy from model
invocation and must define model, prompt, validation, privacy, and human-authority rules.
