"""Validation classes for Aer noise models."""

from __future__ import annotations

from typing import Annotated, Any, List, Literal, Optional, Tuple, Union
from uuid import UUID, uuid4

from pydantic import Field, field_validator

from quantinuum_schemas.models.backend_info import Register

from .base import BaseModel


class QiskitBasicInstruction(BaseModel):
    """Validation model for qiskit instructions without params."""

    name: Literal["id", "x", "y", "z", "reset"]
    qubits: List[int]


class QiskitPauliInstruction(BaseModel):
    """Validation model for qiskit pauli string instructions."""

    name: Literal["pauli"] = "pauli"
    params: List[str]
    qubits: List[int]


class QiskitKrausInstruction(BaseModel):
    """Validation model for qiskit kraus operator instructions."""

    name: Literal["kraus"] = "kraus"
    # List of matrices of complex numbers
    params: List[List[List[List[float]]]]
    qubits: List[int]


QiskitInstruction = Annotated[
    Union[
        QiskitBasicInstruction,
        QiskitPauliInstruction,
        QiskitKrausInstruction,
    ],
    Field(discriminator="name"),
]


class AerQuantumError(BaseModel):
    """Validation model for qiskit-aer's QuantumError class."""

    type: Literal["qerror"] = "qerror"
    id: str = Field(default_factory=lambda: uuid4().hex)
    operations: Optional[List[str]] = Field(default_factory=lambda: [])
    instructions: List[List[QiskitInstruction]]
    probabilities: List[float] = Field(min_length=1)
    gate_qubits: List[List[int]]

    @field_validator("id")
    def validate_id(cls, value: Any) -> str:  # pylint: disable=no-self-argument
        """Ensure id is a v4 UUID in hex format."""
        return UUID(value, version=4).hex


class AerReadoutError(BaseModel):
    """Validation model for qiskit-aer's ReadoutError class."""

    type: Literal["roerror"] = "roerror"
    operations: Optional[List[str]] = Field(default_factory=lambda: ["measure"])
    probabilities: List[List[float]] = Field(min_length=1)
    gate_qubits: List[List[int]]


Error = Annotated[Union[AerQuantumError, AerReadoutError], Field(discriminator="type")]


class AerNoiseModel(BaseModel):
    """Validation model for qiskit-aer's NoiseModel class."""

    errors: List[Error]


class CrosstalkParams(BaseModel):
    """
    Based on pytket-qiskit's CrosstalkParams model.
    Stores various parameters for modelling crosstalk noise.
    """

    zz_crosstalks: dict[Tuple[Register, Register], float]
    single_q_phase_errors: dict[Register, float]
    two_q_induced_phase_errors: dict[Tuple[Register, Register], Tuple[Register, float]]
    non_markovian_noise: list[Tuple[Register, float, float]]
    virtual_z: bool
    N: float
    gate_times: dict[Tuple[str, Tuple[Register, ...]], float]
    phase_damping_error: dict[Register, float]
    amplitude_damping_error: dict[Register, float]
