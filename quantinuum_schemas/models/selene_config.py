"""Additional configuration models for the Selene emulator."""

from pydantic import BaseModel, Field


class SimpleRuntime(BaseModel):
    """A 'simple' runtime for the Selene emulator.

    Does not emulate the runtime (e.g. ion transport) of any specific Quantinuum System.

    Args:
        seed: Random seed for the runtime.
    """

    seed: int | None = Field(default=None)


class HeliosRuntime(BaseModel):
    """A Selene runtime that emulates the Helios system, including ion transport.


    Args:
        seed: Random seed for the runtime.
    """

    seed: int | None = Field(default=None)


class IdealErrorModel(BaseModel):
    """Model for simulating ideal error in quantum systems via Selene.

    All operations provided by the runtime will be executed as-is, without any
    errors.

    Args:
        seed: Random seed for the error model.
    """

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

    seed: int | None = Field(default=None)
    name: str = "alpha"
