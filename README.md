# md-runtime-guard

> Runtime domain enforcement for the ABRCE invariant relational kernel.
> **Metatron Dynamics, 2026**

---

## What this does

Enforces declared domain membership at decorated function boundaries —
before execution produces invalid state that propagates through the system.

This is a direct implementation of the operator-E execution gate from the
[ABRCE invariant relational kernel](https://relationalrelativity.dev/):
no decorated execution is permitted outside the declared domain D.

---

## How it works

Wrap any function with `@bounded_domain` to enforce D-membership on every call:

- Positional and keyword arguments are checked against declared D constraints
- Output is checked before being returned
- Recursion depth is bounded (quantifier enforcement)
- Execution time is bounded
- Nested structures (outside flat ℝⁿ) are rejected as domain expansion
- Execution failures are reported before re-raising

Violations are reported in three modes:

| Mode      | Behavior                        |
|-----------|---------------------------------|
| `warn`    | Print drift signal, continue    |
| `enforce` | Raise RuntimeError, halt        |
| `silent`  | No output                       |

---

## Example

```python
from bounded_domain import bounded_domain, DomainConfig

DomainConfig.MODE = "enforce"

@bounded_domain
def safe_transform(x):
    return [v * 0.9 for v in x]

safe_transform([1.0, 2.0, 3.0])        # passes
safe_transform([1.0, [2.0, 3.0]])      # raises: domain_expansion
safe_transform(x=[1.0, 2.0, 3.0])     # kwargs now enforced too
```

Running the module directly demonstrates three violations:

```
python bounded_domain.py
```

Output (warn mode):

```
⚠️ [DRIFT:magnitude_divergence] in explode (output)
⚠️ [DRIFT:domain_expansion] in nested (output)
⚠️ [DRIFT:magnitude_divergence] in kwarg_test (kwarg input)
```

---

## Domain D

```
D := { x ∈ ℝⁿ | n < ∞  and  |x[i]| < ∞  ∀ i ∈ {0, ..., n−1} }
```

Constraints (configurable in `DomainConfig`):

| Parameter             | Default  | Meaning                        |
|-----------------------|----------|--------------------------------|
| `MAX_DIMENSION`       | 10,000   | Maximum vector length          |
| `MAX_MAGNITUDE`       | 1e9      | Maximum absolute value         |
| `MAX_EXECUTION_TIME`  | 2.0s     | Execution time bound           |
| `MAX_RECURSION_DEPTH` | 50       | Quantifier depth bound         |

---

## Declared enforcement boundary

This tool enforces D-membership at **decorated function boundaries only**.

The following are outside the declared enforcement scope:

- Intermediate values inside function bodies
- Loop growth between iterations
- Unbounded iteration (only recursion depth is bounded)
- Methods inside class definitions
- Dynamically created functions after `wrap_module()` is called
- Imported callables

This is a boundary guard, not a full runtime monitor.
These limitations are structural, not implementation gaps.

---

## ABRCE layer

This tool operates at **operator E** — the execution gate that enforces
D-membership at the boundary of the full A → B → R → C composition.

| Layer | Operator       | Description                              | Repo |
|-------|----------------|------------------------------------------|------|
| ✅ A  | Admissibility  | Declared domain vs. implemented domain   | [md-domain-verifier](https://github.com/Relational-Relativity-Corporation/md-domain-verifier) |
| 🔲 B  | Boundedness    | Value and cardinality constraints        | — |
| 🔲 R  | Relational     | Relation composition order               | — |
| 🔲 C  | Coherence      | Cross-component consistency              | — |
| ✅ E  | Execution gate | Runtime domain enforcement               | this repo |

---

## Framework

Framework: [ABRCE Invariant Relational Kernel](https://relationalrelativity.dev/)
Org: [Relational-Relativity-Corporation](https://github.com/Relational-Relativity-Corporation)