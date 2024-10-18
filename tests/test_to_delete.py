"""Fake test implementation as a part of the MLOps."""


def test_to_delete():
    """Run a basic check."""
    try:
        print("Hello") is None
    except Exception:
        print("Test print function failed.")
        assert False
