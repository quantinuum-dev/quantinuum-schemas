"""Additional configuration models for the Selene emulator."""

from pydantic import BaseModel


class SimpleRuntime(BaseModel):
    """A 'simple' runtime for the Selene emulator.
    Does not emulate the runtime (e.g. ion transport) of any specific Quantinuum System.
    """


class HeliosRuntime(BaseModel):
    """A 'Helios' runtime for the Selene emulator.
    Emulates the runtime (e.g. ion transport) of the Helios Quantinuum System."""
