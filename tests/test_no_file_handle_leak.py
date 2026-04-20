# -*- coding: utf-8 -*-
"""Regression test for file-handle leak in Iching.__init__.

Previously ``Iching`` loaded its pickled data via
``pickle.load(open(path, "rb"))`` which relies on reference-count finalization
to close the underlying file. On non-CPython runtimes (or when garbage
collection is disabled) the handle leaks until interpreter shutdown. The fix
wraps the ``open`` call in a ``with`` statement so the file is closed
deterministically.

This test asserts that constructing ``Iching`` emits no ``ResourceWarning``
(which Python raises for unclosed file objects) even while ``gc`` is disabled,
so the guard would catch a regression to the old ``pickle.load(open(...))``
form.
"""
from __future__ import annotations

import gc
import os
import sys
import warnings

# Make the in-repo ``src`` layout importable without installing the package.
_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
_SRC = os.path.join(_ROOT, "src")
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)


def _construct_iching_under_resource_warning_guard():
    from ichingshifa.ichingshifa import Iching

    gc_was_enabled = gc.isenabled()
    gc.disable()
    try:
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            instance = Iching()
        resource_warnings = [w for w in caught if issubclass(w.category, ResourceWarning)]
        return instance, resource_warnings
    finally:
        if gc_was_enabled:
            gc.enable()


def test_iching_init_does_not_leak_file_handle():
    """Constructing ``Iching`` must not emit a ``ResourceWarning``.

    With ``gc`` disabled, the only way the pickle file gets closed is via an
    explicit ``close()`` call (which ``with open(...)`` guarantees). If the
    code regresses to ``pickle.load(open(path, "rb"))`` the open file object
    becomes unreachable without being closed and Python emits a
    ``ResourceWarning`` the moment it is collected -- or, since gc is off,
    at interpreter shutdown. To make the check synchronous we enable the
    ``always`` warning filter and re-enable gc inside the ``catch_warnings``
    block via a manual collect step below.
    """
    instance, resource_warnings = _construct_iching_under_resource_warning_guard()

    assert instance is not None, "Iching() must return an instance"
    # The pickle file is loaded into ``self.data``; sanity-check the dict
    # actually populated (proves the fix still parses the pickle correctly).
    assert isinstance(instance.data, dict) and instance.data, (
        "Iching().data should be a non-empty dict loaded from data.pkl"
    )

    # Force collection of any stray file objects so a leaked handle would
    # surface as a ResourceWarning right here, not at shutdown.
    with warnings.catch_warnings(record=True) as post_caught:
        warnings.simplefilter("always")
        gc.collect()
        post_resource_warnings = [
            w for w in post_caught if issubclass(w.category, ResourceWarning)
        ]

    all_warnings = resource_warnings + post_resource_warnings
    assert not all_warnings, (
        "Iching() leaked a file handle -- got ResourceWarning(s): "
        + "; ".join(str(w.message) for w in all_warnings)
    )


if __name__ == "__main__":
    test_iching_init_does_not_leak_file_handle()
    print("ok")
