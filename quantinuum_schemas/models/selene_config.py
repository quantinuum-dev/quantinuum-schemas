"""Additional configuration models for the Selene emulator."""

from pydantic import BaseModel, Field


class SimpleRuntime(BaseModel):
    """A 'simple' runtime for the Selene emulator.
    Does not emulate the runtime (e.g. ion transport) of any specific Quantinuum System.
    """

    seed: int | None = Field(default=None)
    """Random seed for the runtime."""


class HeliosRuntime(BaseModel):
    """A Selene runtime that emulates the Helios system, including ion transport."""

    seed: int | None = Field(default=None)
    """Random seed for the runtime."""


class IdealErrorModel(BaseModel):
    """Model for simulating ideal error in quantum systems via Selene.

    All operations provided by the runtime will be executed as-is, without any
    errors."""

    seed: int | None = Field(default=None)
    """Random seed for the error model."""


class DepolarizingErrorModel(BaseModel):
    """Model for simulating depolarizing error in quantum systems
    via Selene."""

    seed: int | None = Field(default=None)
    """Random seed for the error model."""

    p_1q: float = Field(default=0.0, ge=0.0, le=1.0)
    """The error probability for single-qubit gates."""
    p_2q: float = Field(default=0.0, ge=0.0, le=1.0)
    """ The error probability for two-qubit gates."""
    p_meas: float = Field(default=0.0, ge=0.0, le=1.0)
    """The error probability for measurement operations."""
    p_init: float = Field(default=0.0, ge=0.0, le=1.0)
    """The error probability for initialization operations."""
