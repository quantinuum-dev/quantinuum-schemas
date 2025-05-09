"""Validation classes for Quantinuum Systems noise models."""

from typing import Optional, Tuple, Union

from pydantic import BaseModel


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
