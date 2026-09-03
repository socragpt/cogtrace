# Decision records

Decision records preserve durable project reasoning across context windows.
They are append-only after acceptance: correct errors with a clearly marked
amendment or supersede the record with a new one.

## Index

| ID | Status | Decision |
| --- | --- | --- |
| [ADR-001](ADR-001-monitoring-projection.md) | Accepted | Treat structured traces as monitoring projections, not ground truth or action control |
| [ADR-002](ADR-002-treatment-claim-boundaries.md) | Accepted | Give each treatment an explicit causal and interpretive boundary |
| [ADR-003](ADR-003-evidence-and-provenance.md) | Accepted | Separate fixture evidence, live evidence, and harness-trusted provenance |
| [ADR-004](ADR-004-termination-and-completion-budgets.md) | Accepted | Retain provider termination reasons and separate per-call capacity from trajectory cost |
| [ADR-005](ADR-005-m1-design-and-data-policy.md) | Accepted | Freeze the M1 task split, annotation, metrics, capability budget, compute accounting, and private-data policy |

## When to add a record

Add one when changing a research assumption, treatment semantic, trace contract,
primary metric, data policy, evidence threshold, safety boundary, or
infrastructure choice that future work should not casually reverse.

Copy [`ADR-template.md`](ADR-template.md), assign the next number, and add it to
the index. A proposed record can accompany exploratory work; mark it accepted
only when the project has actually adopted the decision.
