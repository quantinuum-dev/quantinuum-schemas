"""Base model definition for use in other models."""

from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Type,
    TypeVar,
    Union,
)

import orjson
from pydantic import BaseModel as PydanticBaseModel
from pydantic import ConfigDict, Field
from pydantic_extra_types.color import Color
from typing_extensions import Annotated


def orjson_dumps(obj: Any, *, default: Optional[Callable[[Any], Any]] = None) -> str:
    """Override orjson.dumps to return a str for compatibility.
    Also handle specific types such as pydantic.color.Color."""

    def default_with_extra_classes(obj: Any) -> Any:
        """Handle extra classes that do not have a default serialisation form.
        This is only used if we don't pass `default` into orjson_dumps, or pass default=None.
        """
        if isinstance(obj, Color):
            return obj.as_hex()
        raise TypeError

    if default is None:
        default = default_with_extra_classes
    # orjson.dumps returns bytes, to match standard json.dumps we need to decode
    return orjson.dumps(obj, default=default).decode()


SerializableType = TypeVar("SerializableType", bound="BaseModel")


class BaseModel(PydanticBaseModel):
    """Custom Pydantic Base Model for the service."""

    model_config = ConfigDict(use_enum_values=True, extra="ignore")

    def to_serializable(self) -> Dict[str, Any]:
        """Obtain orjson serializable form of the model.

        Note: msgpack requires that several types such as UUID and
        datetime are registered with the serializer/deserializer.
        """
        # Dumping by alias lets us be more flexible about field names,
        # but requires our calls to .model_dump to provide the same arguments for
        # consistency.
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_serializable(
        cls: Type[SerializableType], jsonable: Dict[str, Any]
    ) -> SerializableType:
        """Construct the class from a dict and perform validation.

        Exists for compatibility with older nexus_dataclasses API.
        """
        return cls(**jsonable)


class Missing(PydanticBaseModel):
    """Missing represents that the value should not be included
    in json serialization.
    """


MISSING_VALUE = Missing()
T = TypeVar("T")
Patch = Union[Optional[T], Missing]


class PatchBaseModel(BaseModel):
    """Custom Pydantic Base Model associated with patch requests.

    Will include None values when serializing and exclude defaults
    which should be set to be MISSING_VALUE.
    """

    def to_serializable(self) -> Dict[str, Any]:
        """Obtain orjson serializable form of the model.

        Note: msgpack requires that several types such as UUID and
        datetime are registered with the serializer/deserializer.
        """
        # Dumping by alias lets us be more flexible about field names,
        # but requires our calls to .model_dump to provide the same arguments for
        # consistency.
        return self.model_dump(exclude_none=False, exclude_defaults=True, by_alias=True)


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