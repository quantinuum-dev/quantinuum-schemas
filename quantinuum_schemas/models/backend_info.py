"""Serialization classes for pytket BackendInfo."""

# pylint: disable=too-many-branches, too-many-statements, too-many-locals, too-many-instance-attributes
# pylint: disable=import-outside-toplevel, no-name-in-module

from __future__ import annotations

from logging import getLogger
from typing import Any, NewType, Optional

from pydantic import Field

from .base import BaseModel

logger = getLogger(__name__)

Register = NewType("Register", tuple[str, tuple[int, ...]])


class StoredNode(BaseModel):
    """Node in a quantum device's connectivity graph, along with its error rates."""

    unitid: Register
    average_error: Optional[float] = None
    readout_error: Optional[float] = None
    gate_errors: dict[str, float]
    # Give default values for migration purpose
    zero_state_readout_error: Optional[float] = Field(default=None)
    one_state_readout_error: Optional[float] = Field(default=None)


class StoredEdge(BaseModel):
    """Edge in a quantum device's connectivity graph, along with its error rates."""

    unitid_from: Register
    unitid_to: Register
    average_error: Optional[float] = None
    gate_errors: dict[str, float]


class StoredDevice(BaseModel):
    """Nodes and edges that together make up a quantum device's connectivity graph.

    Based on pytket.architecture.Architecture."""

    nodes: list[StoredNode]
    edges: list[StoredEdge]

    n_nodes: Optional[int] = 0
    fully_connected: Optional[bool] = None


class StoredBackendInfo(BaseModel):
    """Equivalent of pytket's BackendInfo, but in a form that it can be converted to and from JSON
    for storage in the Nexus database."""

    name: str
    device_name: Optional[str] = None
    version: str
    device: StoredDevice
    gate_set: list[str]
    n_cl_reg: Optional[int] = None
    supports_fast_feedforward: bool
    supports_reset: bool
    supports_midcircuit_measurement: bool
    misc: dict[str, Any] = Field(default={})
