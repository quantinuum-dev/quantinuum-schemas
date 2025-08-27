

from typing import Literal
from warnings import warn

from pydantic import model_validator
from pydantic.fields import Field
from typing_extensions import Self

from quantinuum_schemas.models.backend_config import BaseBackendConfig, BaseEmulatorConfig, QuantinuumCompilerOptions
from quantinuum_schemas.models.base import BaseModel
from quantinuum_schemas.models.emulator_config import (
    ClassicalReplaySimulator,
    CoinflipSimulator,
    DepolarizingErrorModel,
    MatrixProductStateSimulator,
    NoErrorModel,
    QSystemErrorModel,
    StabilizerSimulator,
    StatevectorSimulator,
)

KNOWN_NEXUS_EMULATORS = ["Helios-1E-lite"]


class RunConstraints(BaseModel):
    """Administrative parameters for running on Quantinuum Systems."""

    attempt_batching: bool = False
    max_batch_cost: int = 2000
    max_cost: int = 100
    priority: str = "normal"


class HeliosEmulatorConfig(BaseEmulatorConfig, BaseBackendConfig):
    """Configuration for any Helios emulator systems."""

    name: str

    seed: int | None = Field(default=None)
    n_qubits: int

    simulator: (
        StatevectorSimulator
        | StabilizerSimulator
        | MatrixProductStateSimulator
        | CoinflipSimulator
        | ClassicalReplaySimulator
    ) = Field(default_factory=StatevectorSimulator)
    error_model: NoErrorModel | DepolarizingErrorModel | QSystemErrorModel = Field(
        default_factory=QSystemErrorModel
    )

    run_constraints: RunConstraints | None = None
    options: QuantinuumCompilerOptions | None # TODO rename

    @model_validator(mode="after")
    def check_valid_config(self) -> Self:
        """Validate the configuration for the emulator."""
        if self.name not in KNOWN_NEXUS_EMULATORS:
            if self.simulator.type == "ClassicalReplaySimulator":
                raise ValueError(f"ClassicalReplaySimulator is only available for emulators in: {KNOWN_NEXUS_EMULATORS}")
            if self.error_model.type == "DepolarizingErrorModel":
                raise ValueError(f"DepolarizingErrorModel is only available for emulators in: {KNOWN_NEXUS_EMULATORS}")
            if self.seed is not None:
                warn(f"seed is ignored for emulators not in: {KNOWN_NEXUS_EMULATORS}")
            if self.simulator.seed is not None:
                warn(f"simulator.seed is ignored for emulators not in: {KNOWN_NEXUS_EMULATORS}")
            if self.error_model.seed is not None:
                warn(f"error_model.seed is ignored for emulators not in: {KNOWN_NEXUS_EMULATORS}")
            if self.run_constraints is not None:
                raise ValueError(f"{RunConstraints.__class__.__name__} required for this emulator")
        if self.run_constraints and self.run_constraints.attempt_batching is True:
            raise ValueError("Batching not available for Helios emulators")
        return self


class HeliosConfig(BaseBackendConfig):
    """Configuration for Helios hardware systems.
    """

    type: Literal["HeliosConfig"] = "HeliosConfig"

    device_name: str

    run_constraints: RunConstraints = Field(default_factory=RunConstraints)

    options: QuantinuumCompilerOptions | None = None # TODO rename


class HeliosCheckerConfig(BaseBackendConfig):
    """Configuration for Helios Checker systems.
    """

    type: Literal["HeliosCheckerConfig"] = "HeliosCheckerConfig"

    device_name: str

    options: QuantinuumCompilerOptions | None = None # TODO rename