"""Defines classes that pass information about the backend to be used for processing
a circuit, and any parameters needed to set up an instance of that backend.

These do not include any parameters that are used to pass access tokens or other credentials,
as our backend credential classes handle those.
"""

# pylint: disable=too-many-lines
import abc
from typing import Any, Dict, Literal, Optional, Union

from pydantic import (
    BaseModel,
    ConfigDict,
    PositiveInt,
    field_validator,
    model_validator,
)
from pydantic.fields import Field
from typing_extensions import Annotated, Self

from quantinuum_schemas.models.aer_noise import AerNoiseModel, CrosstalkParams
from quantinuum_schemas.models.quantinuum_systems_noise import (
    UserErrorParams,
)
from quantinuum_schemas.models.selene_config import (
    DepolarizingErrorModel,
    HeliosRuntime,
    IdealErrorModel,
    SimpleRuntime,
)


class BaseBackendConfig(BaseModel, abc.ABC):
    """Base class for all the backend configs."""

    model_config = ConfigDict(frozen=True)


class AerConfig(BaseBackendConfig):
    """Qiskit Aer QASM simulator."""

    type: Literal["AerConfig"] = "AerConfig"
    noise_model: Optional[AerNoiseModel] = None
    simulation_method: str = "automatic"
    crosstalk_params: Optional[CrosstalkParams] = None
    n_qubits: PositiveInt = 40

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


class QuantinuumCompilerOptions(BaseModel):
    """Class for Quantinuum Compiler Options.

    Intentionally allows extra unknown flags to be defined.
    """

    model_config = ConfigDict(extra="allow", frozen=True)

    @model_validator(mode="before")
    def check_field_values_are_supported_types(  # pylint: disable=no-self-argument,
        cls, values: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check that compiler option values are supported types."""
        for key in values:
            assert isinstance(
                values[key], (str, int, bool, float, list)
            ), "Compiler options must be str, bool or int"
            if isinstance(values[key], list):
                for x in values[key]:
                    assert isinstance(x, float), "Lists must only contain floats"
        return values


class QuantinuumConfig(BaseBackendConfig):
    """Runs circuits on Quantinuum's quantum devices and simulators.

    Args:
        device_name: The quantum computer or emulator to target.
        simulator: If device_name is a simulator, the type of simulator to use.
        machine_debug: Whether to run in machine debug mode.
        attempt_batching: Whether to attempt batching of circuits.
        allow_implicit_swaps: Whether to allow implicit swaps in the compilation process.
        target_2qb_gate: The target 2-qubit gate for the compilation process.
        noisy_simulation: Whether to use a noisy simulation with an error model.
        user_group: The user group for the compilation jobs.
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
    """

    type: Literal["QuantinuumConfig"] = "QuantinuumConfig"
    device_name: str
    simulator: str = "state-vector"
    machine_debug: bool = False
    attempt_batching: bool = False
    # Parameters below are passed into QuantinuumBackend.compilation_config in their own class.
    allow_implicit_swaps: bool = True
    target_2qb_gate: Optional[str] = None
    # Parameters below are kwargs used in QuantinuumBackend.process_circuits().
    noisy_simulation: bool = True
    user_group: Optional[str] = None
    compiler_options: Optional[QuantinuumCompilerOptions] = None
    no_opt: bool = True
    allow_2q_gate_rebase: bool = False
    leakage_detection: bool = False
    simplify_initial: bool = False
    error_params: Optional[UserErrorParams] = None


class IBMQConfig(BaseBackendConfig):
    """Runs circuits on IBM's quantum devices."""

    type: Literal["IBMQConfig"] = "IBMQConfig"
    backend_name: str  # The quantum computer or simulator to run a circuit on.
    hub: str
    group: str
    project: str
    monitor: bool = False
    # Parameters below are kwargs used in IBMQBackend.process_circuits().
    simplify_initial: bool = False


class IBMQEmulatorConfig(BaseBackendConfig):
    """
    Runs circuits on a Nexus-hosted simulator which uses the noise model of a
    specific IBM quantum device.
    """

    type: Literal["IBMQEmulatorConfig"] = "IBMQEmulatorConfig"
    backend_name: str  # The quantum computer to emulate.
    hub: str
    group: str
    project: str


class ProjectQConfig(BaseBackendConfig):
    """ProjectQ state vector simulator."""

    type: Literal["ProjectQConfig"] = "ProjectQConfig"


class QulacsConfig(BaseBackendConfig):
    """Qulacs simulator."""

    type: Literal["QulacsConfig"] = "QulacsConfig"
    result_type: str = "state_vector"


class SeleneConfig(BaseModel):
    """Shared configuration for Selene emulator instances.

    Args:
        runtime: The runtime for the Selene emulator. Runtimes for specific systems (e.g. Helios)
          will model system aspects such as ion transport.
        error_model: The error model for the Selene emulator.
        seed: Random seed for the simulation engine.
        n_qubits: The maximum number of qubits to simulate.
    """

    runtime: SimpleRuntime | HeliosRuntime = Field(default=SimpleRuntime())
    error_model: IdealErrorModel | DepolarizingErrorModel = Field(
        default=IdealErrorModel()
    )
    seed: int | None = Field(default=None)
    n_qubits: int = Field(ge=1)

    @model_validator(mode="after")
    def check_valid_config(self) -> Self:
        """Validate the configuration for the Selene emulator."""
        # Can add validation here once needed.
        return self


class SeleneQuestConfig(BaseBackendConfig, SeleneConfig):
    """Selene QuEST statevector simulator.

    Args:
        runtime: The runtime for the Selene emulator. Runtimes for specific systems (e.g. Helios)
          will model system aspects such as ion transport.
        error_model: The error model for the Selene emulator.
        seed: Random seed for the simulation engine.
        n_qubits: The maximum number of qubits to simulate. Selene QuEST in Nexus is currently
          limited to 28 qubits.
    """

    type: Literal["SeleneQuest"] = "SeleneQuest"

    n_qubits: int = Field(ge=1, le=28)


class SeleneStimConfig(BaseBackendConfig, SeleneConfig):
    """Selene Stim stabilizer simulator. As Stim is a stabilizer simulator, it can only simulate
    Clifford operations. We provide an angle threshold parameter for users to decide how far angles
    can be away from pi/2 rotations on the bloch sphere before they are considered invalid.
    This is to avoid numerical instability, or to inject approximations.

    Args:
        runtime: The runtime for the Selene emulator. Runtimes for specific systems (e.g. Helios)
          will model system aspects such as ion transport.
        error_model: The error model for the Selene emulator.
        seed: Random seed for the simulation engine.
        n_qubits: The maximum number of qubits to simulate.
        angle_threshold: How far angles can be away from pi/2 rotations on the bloch sphere
          before they are considered invalid.
    """

    type: Literal["SeleneStim"] = "SeleneStim"

    angle_threshold: float = Field(default=1e-8, gt=0.0)


class SeleneLeanConfig(BaseBackendConfig, SeleneConfig):
    """Selene Lean (low-entanglement approximation engine) tensor network simulator.

    Args:
        runtime: The runtime for the Selene emulator. Runtimes for specific systems (e.g. Helios)
          will model system aspects such as ion transport.
        error_model: The error model for the Selene emulator.
        seed: Random seed for the simulation engine.
        n_qubits: The maximum number of qubits to simulate.
        backend: The classical compute backend to use.
        precision: The floating point precision used in tensor calculations.
        chi: The maximum value allowed for the dimension of the virtual bonds. Higher implies better
          approximation but more computational resources. If not provided, chi will be unbounded.
        truncation_fidelity: Every time a two-qubit gate is applied, the virtual bond will be
          truncated to the minimum dimension that satisfies |<psi|phi>|^2 >= trucantion_fidelity,
          where |psi> and |phi> are the states before and after truncation (both normalised).
          If not provided, it will default to its maximum value 1.
        zero_threshold: Any number below this value will be considered equal to zero.
          Even when no chi or truncation_fidelity is provided, singular values below
          this number will be truncated.
    """

    type: Literal["SeleneLeanReplay"] = "SeleneLeanReplay"

    backend: Literal["cpu", "cuda"] = "cpu"
    precision: Literal[32, 64] = 32
    chi: int | None = Field(default=None, gt=0, lt=256)
    truncation_fidelity: float | None = Field(default=None, gt=0, le=1)
    zero_threshold: float | None = Field(default=None, gt=0, le=1)

    @model_validator(mode="after")
    def check_valid_config(self) -> Self:
        """Validate the configuration for the Selene emulator."""
        if self.chi and self.truncation_fidelity:
            raise ValueError("Cannot set both chi and truncation_fidelity.")
        return self


class SeleneCoinFlipConfig(BaseBackendConfig, SeleneConfig):
    """Selene 'Coin Flip'  simulator. Doesn't maintain any quantum state and picks a random
    boolean value for each measurement.

    Args:
        runtime: The runtime for the Selene emulator. Runtimes for specific systems (e.g. Helios)
          will model system aspects such as ion transport.
        error_model: The error model for the Selene emulator.
        seed: Random seed for the simulation engine.
        n_qubits: The maximum number of qubits to simulate.
        bias: The bias of the coin flip. The greater this value, the more likely a measurement
          will return True.
    """

    type: Literal["SeleneCoinFlip"] = "SeleneCoinFlip"

    bias: float = Field(default=0.5, ge=0.0, le=1.0)


class SeleneClassicalReplayConfig(BaseBackendConfig, SeleneConfig):
    """Selene 'Classical Replay' simulator. This simulator allows a user to predefine the
    results of measurements for each shot. No quantum operations are performed.

    Args:
        runtime: The runtime for the Selene emulator. Runtimes for specific systems (e.g. Helios)
          will model system aspects such as ion transport.
        error_model: The error model for the Selene emulator.
        seed: Random seed for the simulation engine.
        n_qubits: The maximum number of qubits to simulate.
        measurements: A list of lists of booleans, where each inner list represents the boolean
          measurement results for a single shot."""

    type: Literal["SeleneClassicalReplay"] = "SeleneClassicalReplay"

    measurements: list[list[bool]] = Field(default_factory=list[list[bool]])


BackendConfig = Annotated[
    Union[
        AerConfig,
        AerStateConfig,
        AerUnitaryConfig,
        BraketConfig,
        QuantinuumConfig,
        IBMQConfig,
        IBMQEmulatorConfig,
        ProjectQConfig,
        QulacsConfig,
        SeleneQuestConfig,
        SeleneStimConfig,
        SeleneLeanConfig,
        SeleneCoinFlipConfig,
        SeleneClassicalReplayConfig,
    ],
    Field(discriminator="type"),
]

config_name_to_class: Dict[str, BackendConfig] = {
    config_type.__name__: config_type  # type: ignore
    for config_type in BaseBackendConfig.__subclasses__()
}
