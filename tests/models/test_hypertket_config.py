"""Test hypertket config model."""

from quantinuum_schemas.models.hypertket_config import (
    DualStrat,
    HyperTketConfig,
    QubitReuseConfig,
)


def test_instantiate() -> None:
    """Test instantiation of HyperTketConfig."""
    HyperTketConfig()


def test_enum_serialization() -> None:
    """Test serialization of DualStrat."""
    config = HyperTketConfig(
        qubit_reuse_config=QubitReuseConfig(dual_circuit_strategy=DualStrat.AUTO)
    )

    serialised = config.model_dump()

    HyperTketConfig.model_validate(serialised)
