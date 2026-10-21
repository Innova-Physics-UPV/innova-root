from Prototype import Validator
import numpy as np
import pytest

def test_compare_equal_values():
    assert Validator.compare_values(1.0, 1.0)
def test_compare_close_values():
    assert Validator.compare_values(100.0, 100.00000001)
def test_compare_different_values():
    assert not Validator.compare_values(2,3)
def test_compare_nonfinite_values():
    assert not Validator.compare_values(np.nan, 2)
    assert not Validator.compare_values(np.inf, 2)
    assert not Validator.compare_values(-np.inf, 2)
    assert not Validator.compare_values(np.inf, np.inf)

def test_validate_property():
    result = Validator.validate_property("test_energy", 1.0, 1.1)

    assert result["name"] == "test_energy"
    assert result["calculated"] == 1.0
    assert result["reference"] == 1.1
    assert result["absolute_error"] == pytest.approx(0.1)
    assert not result["passed"]

def test_build_validation_report():
    results = [
        {"passed": True},
        {"passed": False},
        {"passed": True}
    ]

    report = Validator.build_validation_report(results)

    assert report["total"] == 3
    assert report["passed"] == 2
    assert report["failed"] == 1
    assert report["status"] == "FAIL"
    assert report["results"] == results