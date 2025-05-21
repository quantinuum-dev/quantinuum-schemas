"""Test backendconfig models."""

import pytest
from pydantic import ValidationError

from quantinuum_schemas.models.backend_config import (
    AerConfig,
    QuantinuumCompilerOptions,
    SeleneClassicalReplayConfig,
    SeleneCoinFlipConfig,
    SeleneLeanConfig,
    SeleneQuestConfig,
    SeleneStimConfig,
)
from quantinuum_schemas.models.selene_config import (
    DepolarizingErrorModel,
    HeliosRuntime,
    NoErrorModel,
    QSystemErrorModel,
    SimpleRuntime,
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


@pytest.mark.parametrize("runtime_class", [SimpleRuntime, HeliosRuntime])
@pytest.mark.parametrize(
    "error_model_class", [NoErrorModel, DepolarizingErrorModel, QSystemErrorModel]
)
@pytest.mark.parametrize(
    "config_class",
    [
        SeleneQuestConfig,
        SeleneLeanConfig,
        SeleneCoinFlipConfig,
        SeleneStimConfig,
        SeleneClassicalReplayConfig,
    ],
)
def test_selene_roundtrip(
    config_class: type,
    runtime_class: type,
    error_model_class: type,
) -> None:
    """Test roundtrip of SeleneConfigs, importantly the ability to discriminate the
    error model and the runtime."""

    config = config_class(
        runtime=runtime_class(),
        error_model=error_model_class(),
        n_qubits=4,
    )

    reloaded_config = config_class.model_validate_json(config.model_dump_json())  # type: ignore

    assert config == reloaded_config
    assert config.runtime == reloaded_config.runtime
    assert config.error_model == reloaded_config.error_model
