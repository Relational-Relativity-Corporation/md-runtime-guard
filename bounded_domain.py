import time
import functools
import threading
import math
import sys

# -------------------------------------------------------
# Configuration (Domain D constraints)
# -------------------------------------------------------

class DomainConfig:
    MAX_DIMENSION = 10000
    MAX_MAGNITUDE = 1e9
    MAX_EXECUTION_TIME = 2.0
    MAX_RECURSION_DEPTH = 50

    MODE = "warn"  # "warn", "enforce", "silent"


# -------------------------------------------------------
# Thread-local recursion tracking
# -------------------------------------------------------

_thread_local = threading.local()

def get_depth():
    return getattr(_thread_local, "depth", 0)

def inc_depth():
    _thread_local.depth = get_depth() + 1

def dec_depth():
    _thread_local.depth = max(get_depth() - 1, 0)


# -------------------------------------------------------
# Domain Checks (D)
# -------------------------------------------------------

def is_finite_number(x):
    return isinstance(x, (int, float)) and math.isfinite(x)


def is_in_domain(x):
    """
    Checks membership in D:
    - flat ℝⁿ (no nesting)
    - finite dimensional
    - finite magnitude
    """

    # ---- Vector case ----
    if isinstance(x, (list, tuple)):
        if len(x) > DomainConfig.MAX_DIMENSION:
            return False, "domain_expansion"

        for v in x:
            if isinstance(v, (list, tuple)):
                return False, "domain_expansion"
            if not is_finite_number(v):
                return False, "non_finite_value"
            if abs(v) > DomainConfig.MAX_MAGNITUDE:
                return False, "magnitude_divergence"

        return True, None

    # ---- Scalar case ----
    if is_finite_number(x):
        if abs(x) > DomainConfig.MAX_MAGNITUDE:
            return False, "magnitude_divergence"
        return True, None

    # ---- Unknown type ----
    return False, "unknown_type"


# -------------------------------------------------------
# Violation Handling
# -------------------------------------------------------

def report_violation(kind, func_name, detail=""):
    if DomainConfig.MODE == "silent":
        return

    message = f"⚠️ [DRIFT:{kind}] in {func_name} {detail}"

    if DomainConfig.MODE == "warn":
        print(message)

    elif DomainConfig.MODE == "enforce":
        raise RuntimeError(message)


# -------------------------------------------------------
# Core Decorator
# -------------------------------------------------------

def bounded_domain(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        inc_depth()
        depth = get_depth()

        # ---- Recursion check ----
        if depth > DomainConfig.MAX_RECURSION_DEPTH:
            report_violation(
                "unbounded_quantifier",
                func.__name__,
                f"(depth={depth})"
            )

        # ---- Input domain check (args + kwargs) ----
        for arg in args:
            ok, reason = is_in_domain(arg)
            if not ok:
                report_violation(reason, func.__name__, "(input)")

        for arg in kwargs.values():
            ok, reason = is_in_domain(arg)
            if not ok:
                report_violation(reason, func.__name__, "(kwarg input)")

        result = None
        start = time.time()

        try:
            result = func(*args, **kwargs)

            # ---- Output domain check ----
            ok, reason = is_in_domain(result)
            if not ok:
                report_violation(reason, func.__name__, "(output)")

        except Exception as e:
            # ---- Execution failure signal ----
            report_violation(
                "execution_failure",
                func.__name__,
                f"({type(e).__name__}: {str(e)})"
            )
            raise

        finally:
            dec_depth()

        # ---- Execution time check ----
        elapsed = time.time() - start
        if elapsed > DomainConfig.MAX_EXECUTION_TIME:
            report_violation(
                "unbounded_execution",
                func.__name__,
                f"({elapsed:.3f}s)"
            )

        return result

    return wrapper


# -------------------------------------------------------
# Module Wrapper
# -------------------------------------------------------

def wrap_module(module_dict):
    """
    Wraps top-level callables in a module dict (e.g., exec_globals).

    Coverage limitations (declared):
    - Does not wrap methods inside class definitions
    - Does not wrap dynamically created functions after this call
    - Does not wrap imported callables
    Runtime coverage is at decorated boundaries only.
    """
    for name, obj in list(module_dict.items()):
        if callable(obj) and not name.startswith("__"):
            try:
                module_dict[name] = bounded_domain(obj)
            except Exception as e:
                report_violation(
                    "wrap_failure",
                    name,
                    f"({str(e)})"
                )


# -------------------------------------------------------
# CLI Entry
# -------------------------------------------------------

def run_file(filepath):
    with open(filepath, "r") as f:
        code = f.read()

    exec_globals = {}
    exec(code, exec_globals)
    wrap_module(exec_globals)

    main_fn = exec_globals.get("main")
    if callable(main_fn):
        main_fn()


# -------------------------------------------------------
# Example
# -------------------------------------------------------

if __name__ == "__main__":

    @bounded_domain
    def explode(x):
        return x * 1e12  # output exceeds MAX_MAGNITUDE — triggers magnitude_divergence

    @bounded_domain
    def nested():
        return [[1, 2], [3, 4]]  # nested structure — triggers domain_expansion

    @bounded_domain
    def kwarg_test(x=None):
        return x  # kwarg path now checked

    explode(10)
    nested()
    kwarg_test(x=[1e10, 2e10])  # triggers magnitude_divergence via kwarg