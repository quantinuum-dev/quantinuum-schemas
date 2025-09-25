"""Additional configuration models for Quantinuum's emulator, built on Selene."""

from typing import Literal

from pydantic import BaseModel, Field, model_validator
from typing_extensions import Self


class SimpleRuntime(BaseModel):
    """A 'simple' runtime for the Selene emulator.

    Does not emulate the runtime (e.g. ion transport) of any specific Quantinuum System.

    Args:
        seed: Random seed for the runtime.
    """

    type: Literal["SimpleRuntime"] = "SimpleRuntime"

    seed: int | None = Field(default=None)


class HeliosRuntime(BaseModel):
    """A Selene runtime that emulates the Helios system, including ion transport.


    Args:
        seed: Random seed for the runtime.
    """

    type: Literal["HeliosRuntime"] = "HeliosRuntime"

    seed: int | None = Field(default=None)


class NoErrorModel(BaseModel):
    """Model for simulating ideal quantum systems via Selene.

    All operations provided by the runtime will be executed as-is, without any
    errors.

    Args:
        seed: Random seed for the error model.
    """

    type: Literal["NoErrorModel"] = "NoErrorModel"

    seed: int | None = Field(default=None)


class DepolarizingErrorModel(BaseModel):
    """Model for simulating depolarizing error in quantum systems
    via Selene.

    Args:
        seed: Random seed for the error model.
        p_1q: The error probability for single-qubit gates.
        p_2q: The error probability for two-qubit gates.
        p_meas: The error probability for measurement operations.
        p_init: The error probability for initialization operations.
    """

    type: Literal["DepolarizingErrorModel"] = "DepolarizingErrorModel"

    seed: int | None = Field(default=None)
    p_1q: float = Field(default=0.0, ge=0.0, le=1.0)
    p_2q: float = Field(default=0.0, ge=0.0, le=1.0)
    p_meas: float = Field(default=0.0, ge=0.0, le=1.0)
    p_init: float = Field(default=0.0, ge=0.0, le=1.0)


class QSystemErrorModel(BaseModel):
    """Model for simulating error for a specific QSystem via Selene.

    Args:
        seed: Random seed for the error model.
        name: Name of the QSystem error model.
    """

    type: Literal["QSystemErrorModel"] = "QSystemErrorModel"

    seed: int | None = Field(default=None)
    name: str = "alpha"


class StatevectorSimulator(BaseModel):
    """Statevector simulator built on a QuEST backend.

    Args:
        seed: Random seed for the simulation engine.
    """

    type: Literal["StatevectorSimulator"] = "StatevectorSimulator"

    seed: int | None = Field(default=None)


class StabilizerSimulator(BaseModel):
    """Stabilizer simulator built on a Stim backend.
    As Stim is a stabilizer simulator, it can only simulate Clifford operations.
    We provide an angle threshold parameter for users to decide how far angles
    can be away from pi/2 rotations on the bloch sphere before they are considered invalid.
    This is to avoid numerical instability, or to inject approximations.

    Args:
        seed: Random seed for the simulation engine.
        angle_threshold: How far angles can be away from pi/2 rotations on the bloch sphere
          before they are considered invalid.
    """

    type: Literal["StabilizerSimulator"] = "StabilizerSimulator"

    seed: int | None = Field(default=None)
    angle_threshold: float = Field(default=1e-8, gt=0.0)


class MatrixProductStateSimulator(BaseModel):
    """Matrix Product State simulator, built on Quantinuum's Lean
    (low-entanglement approximation engine) backend.

    Args:
        seed: Random seed for the simulation engine.
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

    type: Literal["MatrixProductStateSimulator"] = "MatrixProductStateSimulator"

    seed: int | None = Field(default=None)
    backend: Literal["auto", "cpu", "cuda"] = "auto"
    precision: Literal[32, 64] = 32
    chi: int | None = Field(default=None, gt=0)
    truncation_fidelity: float | None = Field(default=None, gt=0, le=1)
    zero_threshold: float | None = Field(default=None, gt=0, le=1)

    @model_validator(mode="after")
    def check_valid_config(self) -> Self:
        """Validate the configuration for the emulator."""
        if self.backend == "cpu" and self.chi is not None and self.chi > 256:
            raise ValueError("CPU backend does not support chi > 256.")
        if self.chi and self.truncation_fidelity:
            raise ValueError("Cannot set both chi and truncation_fidelity.")
        return self


class CoinflipSimulator(BaseModel):
    """'Coinflip' simulator.

    Doesn't maintain any quantum state and picks a random boolean value for each measurement.

    Args:
        seed: Random seed for the simulation engine.
        bias: The bias of the coin flip. This value is the probability that any given measurement
          will return True.
    """

    type: Literal["CoinflipSimulator"] = "CoinflipSimulator"

    seed: int | None = Field(default=None)
    bias: float = Field(default=0.5, ge=0.0, le=1.0)


class ClassicalReplaySimulator(BaseModel):
    """'Classical Replay' simulator.

    This simulator allows a user to predefine the results of measurements for each shot.
    No quantum operations are performed.

    Args:
        seed: Random seed for the simulation engine.
        measurements: A list of lists of booleans, where each inner list represents the boolean
          measurement results for a single shot."""

    type: Literal["ClassicalReplaySimulator"] = "ClassicalReplaySimulator"

    seed: int | None = Field(default=None)
    measurements: list[list[bool]] = Field(default_factory=list[list[bool]])
