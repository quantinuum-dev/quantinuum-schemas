"""Test backend info models."""

from quantinuum_schemas.models.backend_info import StoredBackendInfo, StoredDevice


def test_to_pyteket_backend() -> None:
    """Test conversion to pytket backend info."""
    gate_set = ["Measure", "Reset", "Rz", "PhasedX", "Barrier"]
    backend_info = StoredBackendInfo(
        name="Example Backend snapshot",
        device_name="Device name",
        version="0.123",
        device=StoredDevice(
            nodes=[],
            edges=[],
            n_nodes=20,
            fully_connected=True,
        ),
        gate_set=gate_set,
        n_cl_reg=0,
        supports_fast_feedforward=True,
        supports_reset=True,
        supports_midcircuit_measurement=True,
    ).to_pytket_backend_info()
    assert set(gate.name for gate in backend_info.gate_set) == set(gate_set)
