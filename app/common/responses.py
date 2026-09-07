from typing import Any, Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class SuccessResponse(BaseModel, Generic[T]):
    success: bool = True
    message: str = "Operation successful"
    data: T | None = None


class ErrorResponse(BaseModel):
    success: bool = False
    detail: str
