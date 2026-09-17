# Reusable Architecture Patterns

## Evidence Intake

Accepts artifacts, assigns identity, records provenance, performs safety validation, and preserves immutable source material. It does not interpret, summarize, evaluate, rank, or decide.

## Document Processing

Consumes immutable artifacts and produces versioned structured observations. OCR, transcription, parsing, and LLM extraction belong here. Outputs retain processor version, provenance, confidence, and source references. Processing does not modify source artifacts or make business decisions.

## Evidence Profile

Aggregates selected observations into an operational view of an entity. A profile is separate from source evidence and separate from evaluation. It is replaceable or supersedable and must retain links to supporting observations.

## Organizational Knowledge

Policies, rubrics, taxonomies, classifications, reference data, and evaluation criteria are proposed, curated, approved, versioned, and frozen. LLMs may assist but do not become the authoritative source.

## Deterministic Evaluation

Consumes an explicit evidence set and a frozen knowledge snapshot. Produces an immutable evaluation result with explainable criteria, provenance, and reproducible calculations.

## Ranking

Consumes compatible completed evaluations and a frozen ranking policy. Produces an immutable comparison snapshot. Ranking never modifies evaluation results and never substitutes for a final human decision.

## Operator Workflow

Coordinates commands across bounded contexts, records progress, exposes failures, and supports restart. It does not own domain entities or business rules.

## Workspace

An operational surface centered on a business context or entity. It assembles projections, evidence, history, commands, and workflow status. It is not authoritative business state.

## Operator Console

Provides navigation, queues, notifications, operational status, and workflow initiation. It delegates all business behavior to application and domain services.

## Immutable History and Supersession

Historical facts and consequential results are append-only. Corrections create new records that explicitly supersede prior records rather than rewriting history.
