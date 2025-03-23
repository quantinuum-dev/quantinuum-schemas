"""Validation classes for Quantinuum Systems results."""

from typing import Annotated

from pydantic import StringConstraints


QShotValType = int | bool | float
QSysShotItemValue = QShotValType | list[QShotValType]

QSysShotItem = tuple[
    Annotated[str, StringConstraints(max_length=256)], QSysShotItemValue
]
QSysShot = list[QSysShotItem]
QSysResult = list[QSysShot]
