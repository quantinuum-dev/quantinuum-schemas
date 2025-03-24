"""Tests for result types."""

import pytest
from pydantic import BaseModel
from pydantic.error_wrappers import ValidationError

from quantinuum_schemas.models.result import QSysResult


def test_result_serialisation() -> None:
    """Test serialisation of result types."""

    class TestResultModel(BaseModel):
        """Test result model to check pydantic handling."""

        result: QSysResult

    test_result_1 = [
        [
            ["test_key_1", 1],
            ["test_key_2", [1, 2, 3]],
        ],
        [
            ["test_key_3", 1.0],
            ["test_key_4", [1.121341453, 2.7878993, 334.0000123]],
        ],
        [
            ["test_key_5", 1],
            ["test_key_6", [True, 0, False, 1]],
        ],
    ]

    test_result_model_instance = TestResultModel(result=test_result_1)  # type: ignore[arg-type]

    assert test_result_model_instance == TestResultModel.model_validate_json(
        test_result_model_instance.model_dump_json()
    )

    test_result_2 = [
        [
            ["test_key_1", "hello"],
            ["test_key_2", ["hi", "hrllo"]],
        ],
        [
            ["test_key_3", [[1.0, 2.0], [True, False]]],
        ],
    ]

    with pytest.raises(ValidationError):
        TestResultModel(result=test_result_2)  # type: ignore[arg-type]
