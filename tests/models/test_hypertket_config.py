"""Test hypertket config model."""

from quantinuum_schemas.models.hypertket_config import HyperTketConfig


def test_instantiate() -> None:
    """Test instantiation of HyperTketConfig."""
    HyperTketConfig()
