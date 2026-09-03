# Tutorial: Formalizing a Philosophical Argument with 4Leibniz

This tutorial demonstrates how to encode a multi-step philosophical argument without confusing textual plausibility with formal proof. We use a deliberately small example inspired by Leibniz's principle of sufficient reason. The historical source is recorded as provenance; the logical inference is checked independently by the Phase 2 proof-search engine and remains a `derived` result until its Lean proof is supplied.

## 1. Write the argument in universal-calculus syntax

Create `examples/monadology_argument.uc`:

```text
claim SufficientReason:
  given intelligible order >= contingent event
  given sufficient reason >= intelligible order
  infer sufficient reason >= contingent event
  source: Principles of Nature and Grace, §7
  status: derived
  tag: metaphysics, sufficient-reason, transitivity
```

The declaration has five layers. `claim` names the argument. Each `given` clause is a premise. `infer` is the target conclusion. `source` records the historical provenance without turning the source into a proof. `status` expresses epistemic confidence, and `tag` supports later semantic search.

## 2. Compile the declaration

Run:

```bash
python3 ucalculus.py examples/monadology_argument.uc
```

The compiler returns a typed intermediate representation containing a normalized claim, its proof obligations, and a SHA-256 fingerprint. The fingerprint changes whenever the structured declaration changes, which makes argument revisions auditable.

The API equivalent is:

```bash
curl -X POST http://127.0.0.1:5050/api/compile \
  -H 'Content-Type: application/json' \
  --data-binary @<(python3 -c 'import json; print(json.dumps({"text": open("examples/monadology_argument.uc").read()}))')
```

## 3. Search for a proof

Use the proof endpoint or the dashboard's **Search for proof** button:

```bash
curl -X POST http://127.0.0.1:5050/api/prove \
  -H 'Content-Type: application/json' \
  --data-binary @<(python3 -c 'import json; print(json.dumps({"text": open("examples/monadology_argument.uc").read()}))')
```

The current transparent engine recognizes direct reuse and order transitivity. It finds the chain

```text
sufficient reason >= intelligible order
intelligible order >= contingent event
therefore sufficient reason >= contingent event
```

The result is `proved` relative to the declared order rule, and it reports the exact premises used. This is an orchestration result, not a claim that the philosophical premises are empirically or metaphysically established.

## 4. Apply a semantic patch

A semantic patch changes the structured argument rather than performing a fragile text replacement. For example, an `add_premise` patch can introduce a missing bridge:

```json
{
  "id": "add-bridge",
  "description": "Add an explicit bridge premise",
  "operation": "add_premise",
  "target": "",
  "replacement": "C >= D"
}
```

Supported operations are `rename`, `replace_conclusion`, and `add_premise`. Every patch is suitable for review, serialization, and later signing as part of a research capsule.

## 5. Interpret the epistemic lattice

The status lattice is ordered as:

```text
open < conjectured < axiomatic < derived < proven
```

This order is not a truth meter. It expresses what kind of support is currently attached to a claim. For the example, `derived` means the conclusion follows from the declared inference rule, while the historical and philosophical premises remain visible as assumptions. A later Lean proof can create a typed `ProvenArgument`, but the system will not silently upgrade the status.

## 6. Read the dependency graph

The dashboard's dependency graph treats theorem names as nodes and declared dependencies as edges. Click a node to inspect its module and status. This makes hidden foundations visible: a high-level result cannot be evaluated responsibly without seeing the lower-level claims on which it depends.

## 7. Extend the argument responsibly

To add a new step, introduce a new `given` clause and change the `infer` target. Then rerun compilation and proof search. If no supported rule closes the result, the engine returns `open` with a remaining obligation. That failure is useful: it identifies the precise bridge that must be formalized, challenged, or marked as conjectural.

The design principle is the one Leibniz's project demands: **make reasoning compositional, make premises explicit, and make disagreement localizable**. The language is intentionally modest today so that each future proof rule can be independently specified, tested, and connected to Lean's kernel.
