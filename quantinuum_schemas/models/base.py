"""Base model definition for use in other models."""

from typing import (
    TYPE_CHECKING,
    Dict,
    List,
    Union,
)

from pydantic import BaseModel as PydanticBaseModel
from pydantic import ConfigDict, Field
from typing_extensions import Annotated


class BaseModel(PydanticBaseModel):
    """Custom Pydantic Base Model for the service."""

    model_config = ConfigDict(use_enum_values=True, extra="ignore")

if TYPE_CHECKING:
    Int64 = int
else:
    # We can only serialise int64s with orjson/msgpack.
    Int64 = Annotated[int, Field(gt=-(2**63), lt=2**63)]

# KwargTypes matches the type annotation of the same name from pytket.utils.results.
KwargTypes = Union[str, Int64, float, None]
Kwargs = Dict[str, KwargTypes]

BasicTypes = Union[
    str, Int64, float, bool, None, List[str], List[Int64], List[float], List[bool]
]
