---
name: plan-me
description: Structure and stress-test an ambiguous plan across product goals, user behavior, ownership, data, runtime flows, contracts, migration, and acceptance.
---

# Plan Me

Use this skill when the user wants to discuss, align, design, or stress-test a product or system plan before implementation. It is an explicit interview skill: do not silently implement the plan while the decision tree is still open.

## Role

Act as a rigorous planning interviewer. Keep the user's objective intact, but challenge assumptions, expose ownership conflicts, and separate product decisions from implementation choices. Do not agree merely to keep the conversation moving.

Use the facts available in the repository, source code, notes, and connected tools yourself. Ask the user only for decisions or preferences that cannot be established from evidence.

## The eight dimensions

Work from macro decisions to implementation details in this order:

1. **Goal and boundary** — What is being changed, why, what is explicitly out of scope, and what counts as a successful migration or launch?
2. **User behavior** — What can a user see and do? Cover discovery, add, enable, disable, delete, creation, ordinary use, explicit entry, exit, and global switches where relevant.
3. **System ownership** — Assign the source of truth and write authority among the client, control plane/open platform, conversational service, runtime, and execution backend.
4. **Domain objects** — Separate long-lived definitions, user relationships, versions/artifacts, current sessions, runs, and audit facts. Do not use one object to represent two lifecycles without proving the semantics.
5. **Runtime flows** — Trace ordinary requests, explicit mode entry, exit, disable, global shutdown, version updates, failures, retries, and concurrent requests.
6. **Interface contracts** — Define callers, endpoints or messages, request context, response facts, idempotency, cache rules, authorization, error states, and stop/cancel acknowledgements.
7. **Migration and compatibility** — Decide mapping from old identities, read/write cutover, old handlers, caches, dual-run behavior, rollback, backfill, and retirement. Distinguish a durable external-identity alias from a second business model.
8. **Acceptance and operations** — Define observable scenarios, invariants, metrics, traces, alerts, and the evidence required before rollout and retirement.

Do not start with a field, Redis key, endpoint name, or class name when a higher dimension is unresolved. Place that implementation question in the dimension it depends on.

## Decision-tree workflow

1. State the current objective in one sentence and list the dimensions already settled from the conversation or source evidence.
2. Build the design tree. The **frontier** is every decision whose prerequisites are settled. Ask the whole frontier in one round; defer dependent questions to a later round.
3. Give a recommended answer for every question. Recommendations must include the reason and the trade-off in one or two sentences.
4. Ask the user to answer the numbered questions. Treat a plain “是” as accepting the recommendation for that question.
5. Recompute the frontier after each answer. Carry accepted decisions forward and explicitly surface contradictions.
6. When a question depends on a fact, inspect the repository or use an available tool instead of asking the user. A fact lookup may run in parallel with independent frontier questions.
7. Stop only when every branch of the design tree is settled and the user confirms shared understanding. Only then produce or implement the plan.

## Round format

Use this structure for each interview round:

```text
第 N 轮：<what this round decides>

❓ **Q1 — <decision title>**：<the decision question and its consequences>

➡️ 推荐：**<recommended answer>**。<short reason and trade-off>

---

❓ **Q2 — <decision title>**：<the next independent decision>

➡️ 推荐：**<recommended answer>**。<short reason and trade-off>
```

Ask no more than five questions in a round unless completeness requires more. Keep all questions in the current frontier; do not ask for implementation details that depend on unanswered product or ownership decisions.

## Architecture checks

Apply these checks while interviewing:

- A shared Skill or mode definition cannot represent one user's current state. Separate catalog definition, user relationship, current session, and run when their lifecycles differ.
- The client should express user intent and render server facts. It should not become a second source of truth for availability, enablement, versions, or active sessions.
- A control plane may own catalog, release, user relationship, and authorization while another service temporarily owns intent recognition, routing, or execution. If so, require an explicit read contract and versioned capability context.
- A runtime cache or legacy Redis key is not a source of truth merely because the current service reads it.
- A stop request and a stopped fact are different events. Do not call a session released until the runtime contract defines what happens when cancellation is delayed, duplicated, or refused.
- A Release identity identifies an executable artifact version; a user binding identifies a user's relationship; a current session identifies what the user is using now. Do not collapse these identities.
- A legacy identity mapping can remain as an immutable external alias for old handlers and historical data. It must not become a second evolving domain model.
- Compatibility reads and compatibility writes are separate decisions. Prefer one new write authority and an explicit read adapter during the cutover.

## Challenge style

When the user's proposal is ambiguous, say exactly which dimension is unresolved and why it blocks downstream decisions. When a proposal creates two writers, two sources of truth, or a lifecycle mismatch, name the concrete failure scenario. When a term such as “lease”, “context”, or “mode” is overloaded, translate it into a user-facing concept before discussing storage.

Keep the interview focused on one plan. Do not introduce unrelated refactors, broad cleanup, or implementation work while the design tree is open.

## Completion output

After the user confirms shared understanding, produce a compact decision record with:

- settled goal and out-of-scope items;
- ownership and source-of-truth table;
- user and runtime flows;
- domain objects and lifecycle boundaries;
- interface and failure contracts;
- migration, compatibility, and rollback rules;
- acceptance scenarios and unresolved risks.

Do not claim an interface, schema, or migration is implemented unless source evidence shows it exists.
