"""Configuration options for HyperTKET compilation."""

from enum import Enum
from typing import Annotated, Literal, Optional, Union

from pydantic import Field

from .base import BaseModel


class RewriteSearchConfig(BaseModel):
    """Configuration for compilation passes that search for a circuit rewrite."""

    enable_rewrite_search: bool = True


class BruteForceOrderConfig(BaseModel):
    """Performs all possible ordering and then estimates
    the ordering with the minimal number of qubits."""

    ordering_method: Literal["BruteForceOrder"] = "BruteForceOrder"


class ConstrainedOptOrderConfig(BaseModel):
    """Orders causal cones using a Constrained Programming
    Satisfiability (CP-SAT) model."""

    ordering_method: Literal["ConstrainedOptOrder"] = "ConstrainedOptOrder"
    time_limit: Annotated[int, Field(ge=0)] = (
        600  # Not clear from OR-Tools docs if this can be 0.
    )
    n_threads: Annotated[int, Field(ge=1)] = 1
    hint: Optional[list[int]] = None


class LocalGreedyOrderConfig(BaseModel):
    """Ordering config for LocalGreedyOrder."""

    ordering_method: Literal["LocalGreedyOrder"] = "LocalGreedyOrder"


class LocalGreedyFirstNodeSearchOrderConfig(BaseModel):
    """Ordering config for LocalGreedyFirstNodeSearchOrder."""

    ordering_method: Literal["LocalGreedyFirstNodeSearchOrder"] = (
        "LocalGreedyFirstNodeSearchOrder"
    )


class CustomOrderConfig(BaseModel):
    """Ordering config for CustomOrder."""

    ordering_method: Literal["CustomOrder"] = "CustomOrder"
    order: list[int]


class DefaultOrderConfig(BaseModel):
    """Switches the Ordering Method used depending
    on the number of Qubits in the Circuit. The
    following specifies the ordering method for
    a specific circuit width.

    * BruteForceOrder: n_qubits <= 9;
    * ConstrainedOptOrder: 9 < n_qubits <= 30;
    * LocalGreedyFirstNodeSearchOrder: 30 < n_qubits <= 1000;
    * LocalGreedyOrder: n_qubits > 1000."""

    ordering_method: Literal["DefaultOrder"] = "DefaultOrder"


OrderingConfig = Union[
    BruteForceOrderConfig,
    ConstrainedOptOrderConfig,
    LocalGreedyOrderConfig,
    LocalGreedyFirstNodeSearchOrderConfig,
    CustomOrderConfig,
    DefaultOrderConfig,
]


class DualStrat(Enum):
    """Strategy for dual circuit compilation.

    * DUAL peforms qubit reuse compilation on
    the dual of the circuit.
    * SINGLE disables use of the dual circuit
    during qubit reuse compilation.
    * AUTO performs qubit reuse compilation
    on both the circuit and its dual. The output
    circuit with the minimal number of qubits is
    returned.
    """

    SINGLE = 0
    DUAL = 1
    AUTO = 2


class QubitReuseConfig(BaseModel):
    """Configuration for qubit reuse compilation pass.
    The DefaultOrderingConfig and DualStart.Auto are
    specified by default."""

    enable_qubit_reuse: bool = False
    ordering_config: Annotated[
        OrderingConfig, Field(discriminator="ordering_method")
    ] = DefaultOrderConfig()
    min_qubits: Optional[Annotated[int, Field(ge=0)]] = None
    dual_circuit_strategy: Optional[DualStrat] = DualStrat.AUTO


class LeakageDetectionConfig(BaseModel):
    """Configuration for the leakage detection gadget compilation pass."""

    enable_leakage_detection: int
    n_device_qubits: int


class HyperTketConfig(BaseModel):
    """Configuration for HyperTKET compilation."""

    rewrite_search_config: RewriteSearchConfig = RewriteSearchConfig()
    qubit_reuse_config: Optional[QubitReuseConfig] = None
    leakage_detection_config: Optional[LeakageDetectionConfig] = None
