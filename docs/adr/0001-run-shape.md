# ADR 0001: the shape of one run

**Filled by:** session 10.

- Status: accepted
- Date: 2026-10-04

## Context

The research assistant needed a simple run shape that was easy to reason about, test, trace, and keep within the model-call budget. A chain was preferred over a more complex loop or graph because the workflow has a clear retrieval-then-answer path.

## Decision (`decision`)

We keep the simple chain in `agent.py`.

## Options considered (`options_considered`)

1. A simple retrieval-to-answer chain.
2. A loop or graph with additional model-driven steps.

## Why not the other option (`why_not`)

The loop or graph adds complexity and additional model calls without being necessary for the current research workflow.

## What would reverse it (`reverses_it`)

We would reconsider the decision if the golden evaluation cases regularly required more than 2 model calls to answer correctly.
