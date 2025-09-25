"""Test backendconfig models."""

import pytest
from pydantic import ValidationError

from quantinuum_schemas.models.backend_config import (
    AerConfig,
    SeleneConfig,
    QuantinuumCompilerOptions,
    SelenePlusConfig,
)
from quantinuum_schemas.models.emulator_config import (
    ClassicalReplaySimulator,
    CoinflipSimulator,
    DepolarizingErrorModel,
    HeliosRuntime,
    MatrixProductStateSimulator,
    NoErrorModel,
    QSystemErrorModel,
    SimpleRuntime,
    StabilizerSimulator,
    StatevectorSimulator,
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


@pytest.mark.parametrize("runtime_class", [SimpleRuntime])
@pytest.mark.parametrize("error_model_class", [NoErrorModel, DepolarizingErrorModel])
@pytest.mark.parametrize(
    "simulator_class",
    [
        StabilizerSimulator,
        StatevectorSimulator,
        CoinflipSimulator,
        ClassicalReplaySimulator,
    ],
)
def test_selene_config_roundtrip(
    runtime_class: type,
    error_model_class: type,
    simulator_class: type,
) -> None:
    """Test roundtrip of SeleneConfig, importantly the ability to discriminate the
    error model and the runtime."""

    config = SeleneConfig(
        simulator=simulator_class(),
        runtime=runtime_class(),
        error_model=error_model_class(),
        n_qubits=4,
    )

    reloaded_config = SeleneConfig.model_validate_json(config.model_dump_json())

    assert config == reloaded_config
    assert config.runtime == reloaded_config.runtime
    assert config.error_model == reloaded_config.error_model


@pytest.mark.parametrize("runtime_class", [SimpleRuntime, HeliosRuntime])
@pytest.mark.parametrize(
    "error_model_class", [NoErrorModel, DepolarizingErrorModel, QSystemErrorModel]
)
@pytest.mark.parametrize(
    "simulator_class",
    [
        StabilizerSimulator,
        StatevectorSimulator,
        CoinflipSimulator,
        MatrixProductStateSimulator,
        ClassicalReplaySimulator,
    ],
)
def test_selene_plus_config_roundtrip(
    runtime_class: type,
    simulator_class: type,
    error_model_class: type,
) -> None:
    """Test roundtrip of SelenePlusConfig, importantly the ability to discriminate the
    error model and the runtime."""

    config = SelenePlusConfig(
        runtime=runtime_class(),
        simulator=simulator_class(),
        error_model=error_model_class(),
        n_qubits=4,
    )

    reloaded_config = SelenePlusConfig.model_validate_json(config.model_dump_json())

    assert config == reloaded_config
    assert config.runtime == reloaded_config.runtime
    assert config.error_model == reloaded_config.error_model
