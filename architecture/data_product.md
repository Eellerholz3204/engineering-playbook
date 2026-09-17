# Data Product Pattern

A data product publishes governed, versioned datasets through explicit contracts. It owns
its transformations, conformance tests, quality evidence, lineage, publication behavior,
and compatibility policy. It does not own private upstream storage or downstream business
decisions.

Consumers depend on released interfaces rather than private models. Every publication
records exact input, reference-data, code, and contract versions. Unknown, unsupported,
ambiguous, and invalid states remain distinguishable.
