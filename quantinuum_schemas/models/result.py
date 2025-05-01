"""Validation classes for Quantinuum Systems results.


Deprecated - please use HUGR's QSysResult instead.
"""

from typing import Annotated, TypeAlias

from pydantic import StringConstraints

QShotValType: TypeAlias = int | bool | float
QSysShotItemValue: TypeAlias = QShotValType | list[QShotValType]

QSysShotItem: TypeAlias = tuple[
    Annotated[str, StringConstraints(max_length=256)], QSysShotItemValue
]
QSysShot: TypeAlias = list[QSysShotItem]
QSysResult: TypeAlias = list[QSysShot]
