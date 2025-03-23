"""Test backendconfig models."""

import pytest
from pydantic import ValidationError

from quantinuum_schemas.models.backend_config import (
    AerConfig,
    QuantinuumCompilerOptions,
)


def test_instantiation() -> None:
    """Test instantiation of AerConfig"""
    aer_config = AerConfig()
    assert isinstance(aer_config, AerConfig)


def test_valid_quantinuum_compiler_options() -> None:
    """Test to ensure that all expected arguments can be accepted by the compiler options class"""
    dict_of_options = {
        "expect_threshold": 0.5,
        "DD_threshold_times": [0.1, 0.2, 0.3],
        "CF": "non linear",
        "test_cz": False,
        "max_planning": 601,
    }

    QuantinuumCompilerOptions(**dict_of_options)


def test_handling_invalid_option() -> None:
    """Expect an assert error raised when passing a bad compiler option"""
    dict_of_options = {
        "DD_threshold_times": [0.1, 3, 0.3],
    }

    with pytest.raises(ValidationError):
        QuantinuumCompilerOptions(**dict_of_options)
