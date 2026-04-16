"""Test backendconfig models."""

from uuid import UUID, uuid4
import warnings

import pytest
from pydantic import ValidationError

from quantinuum_schemas.models.backend_config import (
    AerConfig,
    HeliosConfig,
    HeliosEmulatorConfig,
    QuantinuumConfig,
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

    if error_model_class is QSystemErrorModel and runtime_class is not HeliosRuntime:
        with pytest.raises(ValidationError):
            SelenePlusConfig(
                runtime=runtime_class(),
                simulator=simulator_class(),
                error_model=error_model_class(),
                n_qubits=4,
            )
        return

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


@pytest.mark.parametrize(
    "batch_id,attempt_batching,expect_exception",
    [
        (
            uuid4(),
            False,
            True,
        ),  # batch_id with attempt_batching=False should throw an error
        (uuid4(), True, False),  # valid workflow, should be fine
        (None, True, False),  # valid workflow, should be fine.
    ],
)
def test_batch_id(
    batch_id: UUID, attempt_batching: bool, expect_exception: bool
) -> None:
    """Test batch_id validation follows requirements."""
    if expect_exception:
        with pytest.raises(ValidationError):
            QuantinuumConfig(
                device_name="H2-2",
                batch_id=batch_id,
                attempt_batching=attempt_batching,
            )
        with pytest.raises(ValidationError):
            HeliosConfig(
                system_name="Helios-1",
                batch_id=batch_id,
                attempt_batching=attempt_batching,
            )
    else:
        QuantinuumConfig(
            device_name="H2-2",
            batch_id=batch_id,
            attempt_batching=attempt_batching,
        )
        HeliosConfig(
            system_name="Helios-1", batch_id=batch_id, attempt_batching=attempt_batching
        )


def test_attempt_batching_against_simulators() -> None:
    """Test warning if attempt_batching is True and the backend doesn't support batching."""
    with pytest.warns(RuntimeWarning):
        HeliosConfig(
            system_name="Helios-1E",
            emulator_config=HeliosEmulatorConfig(),
            attempt_batching=True,
        )
        HeliosConfig(system_name="Helios-1SC", attempt_batching=True)
        QuantinuumConfig(device_name="H2-1E", attempt_batching=True)
        QuantinuumConfig(device_name="H1-Emulator", attempt_batching=True)
        QuantinuumConfig(device_name="H2-1SC", attempt_batching=True)

    with warnings.catch_warnings():
        warnings.simplefilter("error")
        HeliosConfig(system_name="Helios-1", attempt_batching=True)
        QuantinuumConfig(device_name="H2-2", attempt_batching=True)
        # if attempt batching is false, no warning is throw
        HeliosConfig(system_name="Helios-1E", emulator_config=HeliosEmulatorConfig())
        HeliosConfig(system_name="Helios-1SC")
        QuantinuumConfig(device_name="H2-1E")
        QuantinuumConfig(device_name="H1-Emulator")
        QuantinuumConfig(device_name="H2-1SC")
