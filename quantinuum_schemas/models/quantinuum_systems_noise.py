"""Validation classes for Quantinuum Systems noise models."""

from typing import Optional, Tuple, Union
from typing_extensions import Self

from pydantic import AliasChoices, Field, model_validator

from .base import BaseModel


_KEYS_1Q_PAULI = {"X", "Y", "Z"}
_KEYS_1Q_EMISSION = _KEYS_1Q_PAULI | {"L"}
_KEYS_2Q_PAULI = {
    "IX",
    "IY",
    "IZ",
    "XI",
    "XX",
    "XY",
    "XZ",
    "YI",
    "YX",
    "YY",
    "YZ",
    "ZI",
    "ZX",
    "ZY",
    "ZZ",
}
_KEYS_2Q_EMISSION = _KEYS_2Q_PAULI | {
    "IL",
    "XL",
    "YL",
    "ZL",
    "LI",
    "LX",
    "LY",
    "LZ",
    "LL",
}


def _validate_distribution(
    name: str, distribution: dict[str, float], keys: set[str]
) -> None:
    """
    Validate that the distribution keys are in the allowed set and that
    all values are between 0 and 1.
    """
    for k, v in distribution.items():
        assert k in keys, (
            f"{name} keys must be a subset of {keys}, "
            f"but an invalid entry was provided with key '{k}'"
        )
        assert 0 <= v <= 1, (
            f"{name} values must be between 0 and 1, but {k}={v} was provided"
        )
    if distribution:  # If non-empty
        sum_values = sum(distribution.values())
        assert abs(1 - sum_values) < 1e-9, (
            f"{name} values must sum to 1 +/- 1e-9, but the provided values sum to {sum_values}"
        )


class HeliosErrorParams(BaseModel):
    """
    Error model configuration for emulation of Quantinuum's Helios System.

    parameters:
        p_init: Probability of error during preparation. Alias: p_prep.
        p_meas_0: Probability of flipping 0 to 1 during measurement.
        p_meas_1: Probability of flipping 1 to 0 during measurement.
        p1: Probability of error after single-qubit gates.
        p2: Probability of error after two-qubit gates.
        p1_emission_ratio: Emission ratio for single-qubit gates.
        p2_emission_ratio: The proportion of two-qubit errors that are emission faults.
        p1_pauli_model: The pauli model for single-qubit gates, e.g.
          `{"X": 0.1,"Y": 0.2,"Z": 0.3}`.
        p1_emission_model: The emission model for single-qubit gates, e.g.
          `{"X": 0.1,"Y": 0.2,"Z": 0.3}`.
        p2_pauli_model: The pauli model for two-qubit gates, e.g.
          `{"XX": 0.2, "YZ": 0.3, "ZI": 0.4}`.
        p2_emission_model: The emission model for two-qubit gates, e.g.
          `{"XX": 0.2, "YZ": 0.3, "ZI": 0.4}`.
        p_prep_leak_ratio: Preparation leakage ratio.
        p1_seepage_prob: Probability of a leaked qubit being seeped (released from leakage) for
          single-qubit.
        p2_seepage_prob: Probability of a leaked qubit being seeped (released from leakage) for
          two-qubit.
        scale: Overall scaling factor.
        memory_scale: Memory scaling factor.
        init_scale: Initial scaling factor. Alias: prep_scale.
        meas_scale: Measurement scaling factor.
        p1_scale: Single-qubit gate scaling factor.
        p2_scale: Two-qubit gate scaling factor.
        emission_scale: Emission scaling factor.
        przz_a: Scaling parameters for RZZ gate error rate - coefficient a.
        przz_b: Scaling parameters for RZZ gate error rate - coefficient b.
        przz_c: Scaling parameters for RZZ gate error rate - coefficient c.
        przz_d: Scaling parameters for RZZ gate error rate - coefficient d.
        przz_power: Power parameter for RZZ error scaling.
        p_crosstalk_meas: Probability of crosstalk during measurement operations.
          Alias: p_meas_crosstalk.
        p_crosstalk_init: Probability of crosstalk during initialization operations.
          Alias: p_prep_crosstalk.
        noiseless_gates: List of gates to be treated as noiseless.
        coherent_dephasing: Whether to include coherent dephasing.
        coherent_to_incoherent_factor: Coherent to incoherent conversion factor.
        leak2depolar: Replace leakage with general noise.
        p_meas_crosstalk_scale: Measurement crosstalk rescale factor.
        p_prep_crosstalk_scale: Preparation crosstalk rescale factor.
        crosstalk_per_gate: Whether to apply crosstalk on a per-gate basis.
        linear_dephasing_rate: Linear rate for idle noise.
          Alias: p_idle_linear_rate.
        quadratic_dephasing_rate: Quadratic rate for idle noise.
          Alias: p_idle_quadratic_rate.
        p2_idle: Stochastic idle noise after each two-qubit gate.
        p_idle_linear_model: Pauli model for linear idle noise in a comma-delimited format.
    """

    p_init: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        validation_alias=AliasChoices("p_init", "p_prep"),
        serialization_alias="p_prep",
    )
    p_meas_0: float = Field(default=0.0, ge=0.0, le=1.0)
    p_meas_1: float = Field(default=0.0, ge=0.0, le=1.0)
    p1: float = Field(default=0.0, ge=0.0, le=1.0)
    p2: float = Field(default=0.0, ge=0.0, le=1.0)
    p1_emission_ratio: float = Field(default=0.0, ge=0.0, le=1.0)
    p2_emission_ratio: float = Field(default=0.0, ge=0.0, le=1.0)
    p1_pauli_model: dict[str, float] = Field(default_factory=dict)
    p1_emission_model: dict[str, float] = Field(default_factory=dict)
    p2_pauli_model: dict[str, float] = Field(default_factory=dict)
    p2_emission_model: dict[str, float] = Field(default_factory=dict)
    p_prep_leak_ratio: float = Field(default=0.0, ge=0.0, le=1.0)
    p1_seepage_prob: float = Field(default=0.0, ge=0.0, le=1.0)
    p2_seepage_prob: float = Field(default=0.0, ge=0.0, le=1.0)
    scale: float = Field(default=1.0, ge=0.0)
    memory_scale: float = Field(default=1.0, ge=0.0)
    init_scale: float = Field(
        default=1.0,
        ge=0.0,
        validation_alias=AliasChoices("init_scale", "prep_scale"),
        serialization_alias="prep_scale",
    )
    meas_scale: float = Field(default=1.0, ge=0.0)
    p1_scale: float = Field(default=1.0, ge=0.0)
    p2_scale: float = Field(default=1.0, ge=0.0)
    emission_scale: float = Field(default=1.0, ge=0.0)
    przz_a: float | None = None
    przz_b: float | None = None
    przz_c: float | None = None
    przz_d: float | None = None
    przz_power: float = 1.0
    p_crosstalk_meas: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        validation_alias=AliasChoices("p_crosstalk_meas", "p_meas_crosstalk"),
        serialization_alias="p_meas_crosstalk",
    )
    p_crosstalk_init: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        validation_alias=AliasChoices("p_crosstalk_init", "p_prep_crosstalk"),
        serialization_alias="p_prep_crosstalk",
    )
    noiseless_gates: list[str] = Field(default_factory=list)
    coherent_dephasing: bool = True
    coherent_to_incoherent_factor: float = 1.5
    leak2depolar: bool = False
    p_meas_crosstalk_scale: float = 1.0
    p_prep_crosstalk_scale: float = 1.0
    crosstalk_per_gate: bool | None = None
    linear_dephasing_rate: float = Field(
        default=0.0,
        ge=0.0,
        validation_alias=AliasChoices("linear_dephasing_rate", "p_idle_linear_rate"),
        serialization_alias="p_idle_linear_rate",
    )
    quadratic_dephasing_rate: float = Field(
        default=0.0,
        ge=0.0,
        validation_alias=AliasChoices(
            "quadratic_dephasing_rate", "p_idle_quadratic_rate"
        ),
        serialization_alias="p_idle_quadratic_rate",
    )
    p2_idle: float = Field(default=0.0, ge=0.0)
    p_idle_linear_model: dict[str, float] = Field(default_factory=dict)

    @model_validator(mode="after")
    def check_valid_config(self) -> Self:
        """Validate the error model configuration."""
        _validate_distribution("p1_pauli_model", self.p1_pauli_model, _KEYS_1Q_PAULI)
        _validate_distribution(
            "p1_emission_model", self.p1_emission_model, _KEYS_1Q_EMISSION
        )
        _validate_distribution(
            "p_idle_linear_model", self.p_idle_linear_model, _KEYS_1Q_EMISSION
        )
        _validate_distribution("p2_pauli_model", self.p2_pauli_model, _KEYS_2Q_PAULI)
        _validate_distribution(
            "p2_emission_model", self.p2_emission_model, _KEYS_2Q_EMISSION
        )

        przz_params = [self.przz_a, self.przz_b, self.przz_c, self.przz_d]
        if not (
            all(x is None for x in przz_params)
            or all(x is not None for x in przz_params)
        ):
            raise ValueError(
                "When setting przz_x, you must either set the four of them, or none."
            )
        return self


class UserErrorParams(BaseModel):
    """User provided error values that override machine values for
    emulation of Quantinuum Systems hardware.

    See the Quantinuum Systems documentation for details of each parameter.


    Args:
        p1: Probability of a fault occurring during a 1-qubit gate.
        p2: Probability of a fault occurring during a 2-qubit gate.
        p_meas:
          Probability of a bit flip being applied to a measurement. Either a float or a tuple of
          2 floats. If it is a single float then that error rate is used to
          bitflip both 0 and 1 measurement results. If a tuple is supplied, the first element is
          the probability a bit flip is applied if a 0 result occurs during measurement while the
          second error rate if a 1 is measured.
        p_init: Probability of a fault occurring during initialization of a qubit.
        p_crosstalk_meas: Probability of a crosstalk measurement fault occurring.
        p_crosstalk_init: Probability of a cross-talk fault occurring during initialization of a
          qubit.
        p1_emission_ratio: Fraction of p1 that is spontaneous emission for a single qubit instead
          of asymmetric depolarizing noise.
        p2_emission_ratio: Fraction of p2 that is spontaneous emission for a 1- qubit in a 2-qubit
          gate instead of asymmetric depolarizing noise.
        quadratic_dephasing_rate: The frequency, f, in applying RZ(fd)during transport and idling.
        linear_dephasing_rate: The probability of applying Z with p=rd where r is rate and
          d is duration. This models the memory error. Note both the quadratic and linear term
          can be applied in the same simulation.
        coherent_to_incoherent_factor: A multiplier on the quadratic term when running stabilizer
          simulations to attempt to account for increases in error due to coherent
          effects in the circuit.
        coherent_dephasing: A boolean value determining whether quadratic dephasing is applied.
        transport_dephasing: A boolean affecting whether memory noise is applied during transport.
        idle_dephasing: A boolean affecting if memory noise is applied due to qubit idling.
        przz_a: Parameter a in parameterized angle scaling. See Emulator User Guide for details.
        przz_b: Parameter b in parameterized angle scaling. See Emulator User Guide for details.
        przz_c: Parameter c in parameterized angle scaling. See Emulator User Guide for details.
        przz_d: Parameter d in parameterized angle scaling. See Emulator User Guide for details.
        przz_power: Polynomial power in parameterized angle scaling. See Emulator User Guide for
          details.
        scale: Scale all error rates in the model linearly.
        p1_scale: Scale the probability of a fault occurring during a 1-qubit gate.
        p2_scale: Scale the probability of a fault occurring during a 2-qubit gate.
        meas_scale: Scale the probability of a fault occurring during measurement.
        init_scale: Scale the probability of a fault occurring during initialization of a qubit.
        memory_scale: Linearly scale the probability of dephasing causing a fault.
        emission_scale: Scale the probability that a spontaneous emission event happens during a
          1- or 2-qubit gate.
        crosstalk_scale: Scale the probability that measurement or initialization crosstalk events
          get applied to qubits.
          During mid-circuit measurement and reset (initialization), crosstalk noise can occur
          that effectively measures other qubits in the trap or cause them to leak.
        leakage_scale: Scale the probability that a leakage even happens during 1- or 2-qubit
          gates as well as during initialization or crosstalk; on the device half the time,
          spontaneous emission leads to a leakage event.

    """

    # Physical Noise
    p1: Optional[float] = None
    p2: Optional[float] = None
    p_meas: Optional[Union[float, Tuple[float, float]]] = None
    p_init: Optional[float] = None
    p_crosstalk_meas: Optional[float] = None
    p_crosstalk_init: Optional[float] = None
    p1_emission_ratio: Optional[float] = None
    p2_emission_ratio: Optional[float] = None
    # Dephasing Noise
    quadratic_dephasing_rate: Optional[float] = None
    linear_dephasing_rate: Optional[float] = None
    coherent_to_incoherent_factor: Optional[float] = None
    coherent_dephasing: Optional[bool] = None
    transport_dephasing: Optional[bool] = None
    idle_dephasing: Optional[bool] = None
    # Arbitrary Angle Noise Scaling
    przz_a: Optional[float] = None
    przz_b: Optional[float] = None
    przz_c: Optional[float] = None
    przz_d: Optional[float] = None
    przz_power: Optional[float] = None
    # Scaling
    scale: Optional[float] = None
    p1_scale: Optional[float] = None
    p2_scale: Optional[float] = None
    meas_scale: Optional[float] = None
    init_scale: Optional[float] = None
    memory_scale: Optional[float] = None
    emission_scale: Optional[float] = None
    crosstalk_scale: Optional[float] = None
    leakage_scale: Optional[float] = None
