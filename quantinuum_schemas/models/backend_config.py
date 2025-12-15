"""Defines classes that pass information about the backend to be used for processing
a circuit, and any parameters needed to set up an instance of that backend.

These do not include any parameters that are used to pass access tokens or other credentials,
as our backend credential classes handle those.
"""

# pylint: disable=too-many-lines,no-member
import abc
from typing import Any, Dict, Literal, Optional, Type, TypeVar, Union
import warnings

from pydantic import ConfigDict, PositiveInt, field_validator, model_validator
from pydantic.fields import Field
from typing_extensions import Annotated, Self

from quantinuum_schemas.models.aer_noise import AerNoiseModel, CrosstalkParams
from quantinuum_schemas.models.emulator_config import (
    ClassicalReplaySimulator,
    CoinflipSimulator,
    DepolarizingErrorModel,
    HeliosCustomErrorModel,
    HeliosRuntime,
    MatrixProductStateSimulator,
    NoErrorModel,
    QSystemErrorModel,
    SimpleRuntime,
    StabilizerSimulator,
    StatevectorSimulator,
)
from quantinuum_schemas.models.quantinuum_systems_noise import UserErrorParams

from .base import BaseModel

ST = TypeVar("ST", bound="BaseModel")

KNOWN_NEXUS_HELIOS_EMULATORS = ["Helios-1E-lite"]


class BaseBackendConfig(BaseModel, abc.ABC):
    """Base class for all the backend configs.
    Implements the to_serializable and from_serializable methods
    for backwards compatibility.
    """

    model_config = ConfigDict(frozen=True, extra="ignore")

    def to_serializable(self) -> Dict[str, Any]:
        """Obtain orjson serializable form of the model."""
        return self.model_dump(exclude_none=True)

    @classmethod
    def from_serializable(cls: Type[ST], jsonable: Dict[str, Any]) -> ST:
        """Construct the class from a dict and perform validation."""
        return cls(**jsonable)


class AerConfig(BaseBackendConfig):
    """Qiskit Aer QASM simulator."""

    type: Literal["AerConfig"] = "AerConfig"
    noise_model: Optional[AerNoiseModel] = None
    simulation_method: str = "automatic"
    crosstalk_params: Optional[CrosstalkParams] = None
    n_qubits: PositiveInt = 40
    seed: Optional[int] = None

    @field_validator("noise_model", mode="before")
    @classmethod
    def validate_noise_model(
        cls,
        value: Any,
    ) -> Optional[AerNoiseModel]:
        """Validate that we can use this"""
        if value is not None:
            if isinstance(value, AerNoiseModel):
                return value
            if hasattr(value, "to_dict"):
                # Should cover the case of an Aer NoiseModel being passed directly.
                # Needs to be passed serializable=True to prevent numpy
                # arrays being included in the dictionary.
                return AerNoiseModel(**value.to_dict(serializable=True))
            if isinstance(value, dict):
                return AerNoiseModel(**value)
            raise ValueError(
                "must be an AerNoiseModel, a qiskit-aer NoiseModel or conform to the spec."
            )
        return None


class AerStateConfig(BaseBackendConfig):
    """Qiskit Aer state vector simulator."""

    type: Literal["AerStateConfig"] = "AerStateConfig"
    n_qubits: PositiveInt = 40


class AerUnitaryConfig(BaseBackendConfig):
    """Qiskit Aer unitary simulator."""

    type: Literal["AerUnitaryConfig"] = "AerUnitaryConfig"
    n_qubits: PositiveInt = 40


class BraketConfig(BaseBackendConfig):
    """Runs circuits on quantum devices and simulators using Amazon's Braket service."""

    type: Literal["BraketConfig"] = "BraketConfig"
    local: bool
    local_device: str = "default"
    device_type: Optional[str] = None
    provider: Optional[str] = None
    device: Optional[str] = (
        None  # The quantum computer or simulator to run a circuit on.
    )
    s3_bucket: Optional[str] = None
    s3_folder: Optional[str] = None
    # Parameters below are kwargs used in BraketBackend.process_circuits().
    simplify_initial: bool = False

    @model_validator(mode="before")
    def check_local_remote_parameters_are_consistent(  # pylint: disable=no-self-argument,
        cls, values: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate that the parameters for BraketConfig are consistent for either a local device,
        or a remote device."""
        if values.get("local"):
            # For a local config, we care about local_device only. This has a default value,
            # so we don't need to validate it, but we should give a ValidationError if any of
            # the other items are set.
            if any(
                (
                    values.get(remote_field) is not None
                    for remote_field in (
                        "device_type",
                        "provider",
                        "device",
                        "s3_bucket",
                        "s3_folder",
                    )
                )
            ):
                raise ValueError(
                    "BraketConfig with local=True must only have local and local_device set"
                )
        else:
            # We can ignore local_device, because it has a default value in BraketBackend,
            # but all of the other parameters must be set.
            if any(
                (
                    values.get(remote_field) is None
                    for remote_field in (
                        "device_type",
                        "provider",
                        "device",
                        "s3_bucket",
                        "s3_folder",
                    )
                )
            ):
                raise ValueError(
                    "BraketConfig with local=False must have device_type, provider, device, "
                    "s3_bucket and s3_folder set"
                )
        return values


class QuantinuumOptions(BaseModel):
    """Class for Quantinuum additional options.

    Intentionally allows extra unknown flags to be defined.
    """

    model_config = ConfigDict(extra="allow", frozen=True)

    @model_validator(mode="before")
    def check_field_values_are_supported_types(  # pylint: disable=no-self-argument,
        cls, values: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check that option values are supported types."""
        for key in values:
            assert isinstance(values[key], (str, int, bool, float, list)), (
                "Options must be str, bool int, float or a list of floats"
            )
            if isinstance(values[key], list):
                for x in values[key]:
                    assert isinstance(x, float), "Lists must only contain floats"
        return values


# Alias via inheritance for backwards compatibility
class QuantinuumCompilerOptions(QuantinuumOptions):
    """Class for Quantinuum compiler options.

    Intentionally allows extra unknown flags to be defined.
    """


class QuantinuumConfig(BaseBackendConfig):
    """Runs circuits on Quantinuum's quantum devices and simulators.

    Args:
        device_name: The quantum computer or emulator to target.
        simulator: If device_name is a simulator, the type of simulator to use.
        machine_debug: Whether to run in machine debug mode.
        attempt_batching: Whether to attempt batching of circuits.
        allow_implicit_swaps: Whether to allow implicit swaps in the compilation process.
        postprocess:
          Apply end-of-circuit simplifications and classical postprocessing
          to improve fidelity of results
        noisy_simulation: Whether to use a noisy simulation with an error model.
        target_2qb_gate: The target 2-qubit gate for the compilation process.
        compiler_options: Additional options for the Quantinuum Systems compiler.
        no_opt: Whether to disable optimization in the compilation process.
        allow_2q_gate_rebase: Whether to allow 2-qubit gate rebase in the compilation process.
        leakage_detection:
          If true, adds additional Qubit and Bit to Circuit to detect leakage errors.
          Run prune_shots_detected_as_leaky on returned BackendResult to get counts with
          leakage errors removed.
        simplify_initial: Apply the pytket SimplifyInitial pass to improve fidelity of
          results assuming all qubits initialized to zero.
        error_params: Additional error parameters for execution on an emulator.
        user_group: The user group for the compilation jobs.
        max_batch_cost: The maximum HQC cost for a batch of programs (total).
        max_cost: The maximum HQC cost for a single programs.
    """

    type: Literal["QuantinuumConfig"] = "QuantinuumConfig"
    device_name: str
    simulator: str = "state-vector"
    machine_debug: bool = False
    attempt_batching: bool = False
    # Parameters below are passed into QuantinuumBackend.compilation_config in their own class.
    allow_implicit_swaps: bool = True
    # Parameters below are kwargs used in QuantinuumBackend.process_circuits().
    postprocess: bool = False
    noisy_simulation: bool = True
    target_2qb_gate: Optional[str] = None
    user_group: Optional[str] = None
    max_batch_cost: int = 2000
    compiler_options: Optional[QuantinuumCompilerOptions] = None
    no_opt: bool = True
    allow_2q_gate_rebase: bool = False
    leakage_detection: bool = False
    simplify_initial: bool = False
    max_cost: Optional[int] = None
    error_params: Optional[UserErrorParams] = None

    @model_validator(mode="after")
    def show_deprecation_warnings(self) -> Self:
        """Warn about deprecated usage."""

        if self.user_group is not None:
            warnings.warn(
                "'QuantinuumConfig.user_group' is deprecated and will be "
                "removed in a future release. Please specify user_group in the execute job"
                "submission parameters instead.",
                DeprecationWarning,
            )

        if self.device_name.startswith("Helios"):
            warnings.warn(
                "QuantinuumConfig is deprecated for submission to Helios systems and support "
                "will be removed in a future release. Please use HeliosConfig instead.",
                DeprecationWarning,
            )

        return self


class IBMQConfig(BaseBackendConfig):
    """Runs circuits on IBM's quantum devices."""

    type: Literal["IBMQConfig"] = "IBMQConfig"
    backend_name: str  # The quantum computer or simulator to run a circuit on.
    instance: str
    region: Optional[str] = None
    monitor: bool = False
    # Parameters below are kwargs used in IBMQBackend.process_circuits().
    postprocess: bool = False
    simplify_initial: bool = False


class IBMQEmulatorConfig(BaseBackendConfig):
    """
    Runs circuits on a Nexus-hosted simulator which uses the noise model of a
    specific IBM quantum device.
    """

    type: Literal["IBMQEmulatorConfig"] = "IBMQEmulatorConfig"
    backend_name: str  # The quantum computer to emulate.
    instance: str
    region: Optional[str] = None
    # Parameters below are kwargs
    seed: Optional[int] = None
    postprocess: bool = False


class QulacsConfig(BaseBackendConfig):
    """Qulacs simulator."""

    type: Literal["QulacsConfig"] = "QulacsConfig"
    result_type: str = "state_vector"
    gpu_sim: bool = False
    # Parameters below are kwargs
    seed: Optional[int] = None


class BaseEmulatorConfig(BaseModel):
    """Shared configuration for Selene emulator instances. Not to be used directly.

    Args:
        n_qubits: The maximum number of qubits to simulate.
    """

    n_qubits: int | None = None

    @model_validator(mode="after")
    def prevent_direct_instantiation(self) -> Self:
        """Prevent direct instantiation of BaseEmulatorConfig."""
        if self.__class__ == BaseEmulatorConfig:
            raise TypeError(
                f"{self.__class__.__name__} cannot be instantiated directly"
            )
        return self


class SeleneConfig(BaseEmulatorConfig, BaseBackendConfig):
    """Configuration for Quantinuum's Selene.

    Args:
        simulator: The simulator backend to use.
        runtime: The runtime for the Selene emulator. Runtimes for specific systems
          will model system aspects such as ion transport.
        error_model: The error model for the Selene emulator.
        n_qubits: The maximum number of qubits to simulate.
    """

    type: Literal["SeleneConfig"] = "SeleneConfig"

    simulator: (
        StatevectorSimulator
        | StabilizerSimulator
        | CoinflipSimulator
        | ClassicalReplaySimulator
    ) = Field(default_factory=StatevectorSimulator)
    runtime: SimpleRuntime = Field(default_factory=SimpleRuntime)
    error_model: NoErrorModel | DepolarizingErrorModel = Field(
        default_factory=NoErrorModel
    )


class SelenePlusConfig(BaseEmulatorConfig, BaseBackendConfig):
    """Configuration for Quantinuum's Selene Plus, including advanced runtimes and simulators.

    Args:
        simulator: The simulator backend to use.
        runtime: The runtime for the Selene emulator. Runtimes for specific systems (e.g. Helios)
          will model system aspects such as ion transport.
        error_model: The error model for the Selene emulator.
        n_qubits: The maximum number of qubits to simulate.
    """

    type: Literal["SelenePlusConfig"] = "SelenePlusConfig"

    simulator: (
        StatevectorSimulator
        | StabilizerSimulator
        | MatrixProductStateSimulator
        | CoinflipSimulator
        | ClassicalReplaySimulator
    ) = Field(default_factory=StatevectorSimulator)
    runtime: SimpleRuntime | HeliosRuntime = Field(default_factory=HeliosRuntime)
    error_model: (
        NoErrorModel
        | DepolarizingErrorModel
        | QSystemErrorModel
        | HeliosCustomErrorModel
    ) = Field(default_factory=QSystemErrorModel)

    @model_validator(mode="after")
    def validate_runtime_and_error_model(self) -> Self:
        """Validate that the runtime and error model are compatible."""
        if isinstance(self.error_model, (QSystemErrorModel, HeliosCustomErrorModel)):
            if not isinstance(self.runtime, HeliosRuntime):
                raise ValueError(
                    f"error_model of type: {self.error_model.__class__.__name__} "
                    "can only be used with runtime of type: HeliosRuntime"
                )
        if isinstance(self.error_model, HeliosCustomErrorModel):
            if isinstance(self.simulator, StabilizerSimulator):
                if self.error_model.error_params.coherent_dephasing is True:
                    raise ValueError(
                        "HeliosErrorModel with StabilizerSimulator must have "
                        "coherent_dephasing set to False"
                    )

        return self


class HeliosEmulatorConfig(BaseEmulatorConfig):
    """Configuration for Helios emulator systems."""

    n_qubits: int | None = None

    simulator: (
        StatevectorSimulator
        | StabilizerSimulator
        | MatrixProductStateSimulator
        | CoinflipSimulator
        | ClassicalReplaySimulator
    ) = Field(default_factory=StatevectorSimulator)
    error_model: (
        NoErrorModel
        | DepolarizingErrorModel
        | QSystemErrorModel
        | HeliosCustomErrorModel
    ) = Field(default_factory=QSystemErrorModel)
    runtime: HeliosRuntime = Field(default_factory=HeliosRuntime)


class HeliosConfig(BaseBackendConfig):
    """Configuration for Helios generation QPUs, emulators and checkers."""

    type: Literal["HeliosConfig"] = "HeliosConfig"

    system_name: str = "Helios-1"
    emulator_config: HeliosEmulatorConfig | None = None

    max_cost: float | None = None

    attempt_batching: bool = False
    max_batch_cost: float = 2000.0

    options: QuantinuumOptions | None = None

    @model_validator(mode="after")
    def check_valid_config(self) -> Self:
        """Perform simple configuration validation."""

        if self.max_cost is None:
            if (
                not self.system_name.endswith("SC")
                and self.system_name not in KNOWN_NEXUS_HELIOS_EMULATORS
            ):
                raise ValueError(f"max_cost must be set for {self.system_name}.")

        if self.emulator_config is not None:
            if self.attempt_batching:
                raise ValueError("Batching not available for emulators.")
            if self.system_name in KNOWN_NEXUS_HELIOS_EMULATORS:
                if self.max_cost:
                    raise ValueError(
                        f"max_cost not currently supported for {self.system_name}"
                    )
            if self.system_name not in KNOWN_NEXUS_HELIOS_EMULATORS:
                if self.emulator_config.simulator.type == "ClassicalReplaySimulator":
                    raise ValueError(
                        f"ClassicalReplaySimulator is only available for "
                        f"emulators in: {KNOWN_NEXUS_HELIOS_EMULATORS}"
                    )
                if self.emulator_config.error_model.type == "DepolarizingErrorModel":
                    raise ValueError(
                        f"DepolarizingErrorModel is only available for "
                        f"emulators in: {KNOWN_NEXUS_HELIOS_EMULATORS}"
                    )
                if self.emulator_config.runtime.seed is not None:
                    raise ValueError(
                        f"runtime.seed will be ignored for {self.system_name}"
                    )
                if self.emulator_config.simulator.seed is not None:
                    raise ValueError(
                        f"simulator.seed will be ignored for {self.system_name}"
                    )
                if self.emulator_config.error_model.seed is not None:
                    raise ValueError(
                        f"error_model.seed will be ignored for {self.system_name}"
                    )
        return self


BackendConfig = Annotated[
    Union[
        AerConfig,
        AerStateConfig,
        AerUnitaryConfig,
        BraketConfig,
        QuantinuumConfig,
        IBMQConfig,
        IBMQEmulatorConfig,
        QulacsConfig,
        SeleneConfig,
        SelenePlusConfig,
        HeliosConfig,
    ],
    Field(discriminator="type"),
]

config_name_to_class: Dict[str, BackendConfig] = {
    config_type.__name__: config_type  # type: ignore
    for config_type in BaseBackendConfig.__subclasses__()
}
