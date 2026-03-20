# md-runtime-guard

> Runtime domain enforcement for the ABRCE invariant relational kernel.
> **Metatron Dynamics, 2026**

---

## What this does

Enforces declared domain membership at function boundaries — before execution
produces invalid state that propagates through the system.

This is a direct implementation of the operator-E execution gate from the
[ABRCE invariant relational kernel](https://relationalrelativity.dev/):
no processing outside the declared domain D is valid.

---

## How it works

Wrap any function with `@bounded_domain` to enforce D-membership on every call:

- Input vectors and scalars are checked against declared D constraints
- Output is checked before being returned
- Recursion depth is bounded (quantifier enforcement)
- Execution time is bounded
- Nested structures (outside flat ℝⁿ) are rejected as domain expansion

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

safe_transform([1.0, 2.0, 3.0])  # passes
safe_transform([1.0, [2.0, 3.0]])  # raises: domain_expansion
```

Running the module directly demonstrates two violations:

```
python bounded_domain.py
```

Output (warn mode):

```
⚠️ [DRIFT:magnitude_divergence] in explode (output)
⚠️ [DRIFT:domain_expansion] in nested (output)
```

---

## Domain D

```
D := { x ∈ ℝⁿ | n < ∞  and  |x[i]| < ∞  ∀ i ∈ {0, ..., n−1} }
```

Constraints (configurable in `DomainConfig`):

| Parameter            | Default  | Meaning                        |
|----------------------|----------|--------------------------------|
| `MAX_DIMENSION`      | 10,000   | Maximum vector length          |
| `MAX_MAGNITUDE`      | 1e9      | Maximum absolute value         |
| `MAX_EXECUTION_TIME` | 2.0s     | Execution time bound           |
| `MAX_RECURSION_DEPTH`| 50       | Quantifier depth bound         |

---

## ABRCE layer

This tool operates at **operator E** — the execution gate that enforces
D-membership across the full A → B → R → C composition.

| Layer | Operator | Description                              | Repo |
|-------|----------|------------------------------------------|------|
| ✅ A  | Admissibility  | Declared domain vs. implemented domain | [md-domain-verifier](https://github.com/Relational-Relativity-Corporation/md-domain-verifier) |
| 🔲 B  | Boundedness    | Value and cardinality constraints      | — |
| 🔲 R  | Relational     | Relation composition order             | — |
| 🔲 C  | Coherence      | Cross-component consistency            | — |
| ✅ E  | Execution gate | Runtime domain enforcement             | this repo |

---

## Framework

Framework: [ABRCE Invariant Relational Kernel](https://relationalrelativity.dev/)
Org: [Relational-Relativity-Corporation](https://github.com/Relational-Relativity-Corporation)