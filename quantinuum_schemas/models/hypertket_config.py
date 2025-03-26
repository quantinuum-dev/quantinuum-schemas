"""Configuration options for HyperTKET compilation."""

from enum import Enum
from typing import Annotated, Literal, Optional, Union

from pydantic import BaseModel, Field


class RewriteSearchConfig(BaseModel):
    """Configuration for compilation passes that search for a circuit rewrite."""

    enable_rewrite_search: bool = True


class BruteForceOrderConfig(BaseModel):
    """Ordering config for BruteForceOrder."""

    ordering_method: Literal["BruteForceOrder"] = "BruteForceOrder"


class ConstrainedOptOrderConfig(BaseModel):
    """Ordering config for ConstrainedOptOrder."""

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
    """Ordering config for DefaultOrder."""

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
    """Strategy for dual circuit compilation."""

    SINGLE = 0
    DUAL = 1
    AUTO = 2


class QubitReuseConfig(BaseModel):
    """Configuration for qubit reuse compilation pass."""

    enable_qubit_reuse: bool = False
    ordering_config: Annotated[
        OrderingConfig, Field(discriminator="ordering_method")
    ] = DefaultOrderConfig()
    min_qubits: Optional[Annotated[int, Field(ge=0)]] = None
    dual_circuit_strategy: Optional[DualStrat] = None


class HyperTketConfig(BaseModel):
    """Configuration for HyperTKET compilation."""

    rewrite_search_config: RewriteSearchConfig = RewriteSearchConfig()
    qubit_reuse_config: Optional[QubitReuseConfig] = None
