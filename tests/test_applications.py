import pytest

from appunit.applications import Module


def test_app_property():
    module = Module()

    with pytest.raises(RuntimeError) as exc_info:
        _ = module.app

    assert str(exc_info.value) == "Module is not configured."
