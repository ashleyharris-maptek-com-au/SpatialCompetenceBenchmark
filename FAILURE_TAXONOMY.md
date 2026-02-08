# Failure-Mode Taxonomy (5-way)

This taxonomy is for analyzing failures on SCBench/VGBench-style tasks where a model must produce an executable artifact under hard constraints.

These **failure modes are orthogonal** to the SCBench task buckets (**Axiomatic**, **Constructive**, **Planning**). The same failure mode can occur in any bucket.

## Labels

### 1) Evasion / Forfeit
**Definition:** The model chooses not to seriously attempt the required construction.

**Include when:**
- It refuses, declines, or explicitly decides the task is "too hard" and punts to "write code", "use a solver", etc.
- It returns empty / placeholder structures (e.g., `[]`, `{}`, missing required keys) that are not a meaningful attempt.

**Exclude when:**
- The model produces a substantive attempt but is wrong; use one of the other labels.

### 2) Trivialized / Misframed
**Definition:** The model fails to grasp what is being asked (wrong task model), and solves an easier/different problem or silently drops key constraints.

**Include when:**
- It answers a different question than asked.
- It ignores core constraints that define the task (not just a small edge case).

### 3) Runaway Overthinking
**Definition:** The model spends tokens in a long direction that does not cash out into the required executable artifact, or it commits to an overly general method that derails execution.

**Include when:**
- The reasoning is long and self-consistent, but the produced artifact is misaligned with the required interface/constraints (despite being non-empty).

**Tie-breaker vs. Evasion / Forfeit:**
- If the final output is empty/placeholder, label **Evasion / Forfeit** instead.

### 4) Local-Only (Global Constraint Integration Failure)
**Definition:** The model can handle local geometry/logic, but cannot consolidate the solution into a globally consistent artifact under hard constraints.

**Typical signatures:**
- Overlaps/intersections where non-overlap is required.
- Self-intersections, non-manifold meshes, inconsistent winding, invalid topology.
- Crossing paths, holes in projections, global coverage violations.
- Discrete-vs-continuous mismatch (e.g., "looks right" but violates snap/quantization/assemblability rules).

**When to prefer this label:**
- The verifier reports multiple constraint violations, or a structural violation that indicates the overall solution is not globally coherent.

### 5) Near-Miss Edge Case
**Definition:** The model solves most of the spatial problem, but misses a crisp edge condition.

**Typical signatures:**
- Off-by-one counts, a single duplicate vertex/voxel, one out-of-bounds point, one segment-length tolerance miss.
- A single constraint failure in an otherwise coherent artifact.

**Tie-breaker vs. Local-Only:**
- Use **Near-Miss Edge Case** when the failure is plausibly fixable by a small, local correction without redesigning the whole solution.

## Tie-Break Rules (Decision Order)

1. If the output is empty/placeholder or the model clearly declines: **Evasion / Forfeit**
2. If the model is solving the wrong problem / dropped defining constraints: **Trivialized / Misframed**
3. If the output is mostly correct with one crisp check failing: **Near-Miss Edge Case**
4. If the output shows structural/global inconsistency under constraints: **Local-Only**
5. Otherwise, if the model went long and off-track while still producing a non-empty artifact: **Runaway Overthinking**

## Meta Labels (Not Part of the 5-way)

These are useful for bookkeeping but should be tracked separately from the 5 failure modes:

- **Derived skip:** Not executed (earlyFail / earlier-zero / test forfeited by runner).
- **Infra / harness issue:** Dependency/runtime error, toolchain failure, or other non-model error.
- **Pipeline loss:** Model output cannot be inspected due to parsing/logging loss (e.g., stored as `{}` with no trace of original text).

## Suggested Classifier Output Schema

If you use an LLM as a classifier, have it emit something like:

```json
{
  "failure_mode": "evasion_forfeit | trivialized_misframed | runaway_overthinking | local_only_global_integration | near_miss_edge_case",
  "task_bucket": "axiomatic | constructive | planning",
  "confidence": 0.0,
  "justification": "One short paragraph grounded in prompt/output/verifier signals."
}
```

