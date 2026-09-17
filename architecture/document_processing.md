# Document Processing Pattern

## Boundary

Document Processing begins after immutable artifacts have entered Evidence Intake.

## Responsibilities

- format detection and safe reading;
- OCR and text extraction;
- transcription;
- structural parsing;
- LLM-assisted extraction of observations;
- confidence and quality signals;
- processor and model provenance;
- repeatable reprocessing;
- human review support.

## Prohibitions

Document Processing does not mutate artifacts, establish organizational truth, create authoritative entity profiles by itself, evaluate, rank, advance workflows, or make business decisions.

## Output

Outputs are immutable processing runs and structured observations linked to exact source locations and processor versions. Reprocessing creates new outputs and preserves prior history.
