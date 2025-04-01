import difflib

pytest_plugins = ("sphinx.testing.fixtures",)


def pytest_assertrepr_compare(op, left, right):
    if isinstance(left, str) and isinstance(right, str) and op == "==":
        return list(difflib.context_diff(left.split("\n"), right.split("\n")))
