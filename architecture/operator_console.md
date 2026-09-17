# Operator Console Pattern

The Operator Console is a navigation and orchestration surface.

It may provide queues, search, notifications, workflow status, command initiation, exception handling, and links to workspaces.

It must not own business entities, evaluate evidence, rank entities, contain policy calculations, mutate history directly, or become an alternative persistence layer.

All consequential actions delegate to application services with explicit authorization, validation, audit records, and visible outcomes.
