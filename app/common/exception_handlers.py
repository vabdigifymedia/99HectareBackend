import re
from fastapi import Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from app.common.exceptions import AppException


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "detail": exc.detail},
    )


async def integrity_exception_handler(
    request: Request, exc: IntegrityError
) -> JSONResponse:
    error_msg = str(exc.orig) if hasattr(exc, "orig") and exc.orig else str(exc)
    detail = "Database integrity constraint violated."

    # Handle foreign key violations
    if "foreign key constraint" in error_msg.lower():
        match = re.search(r"Key \((.*?)\)=\((.*?)\) is not present in table \"(.*?)\"", error_msg)
        if match:
            field, val, table = match.groups()
            detail = f"Referenced {field} '{val}' does not exist in table '{table}'."
        else:
            detail = "Referenced entity does not exist."
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"success": False, "detail": detail},
        )

    # Handle unique violations
    if "unique constraint" in error_msg.lower():
        match = re.search(r"Key \((.*?)\)=\((.*?)\) already exists", error_msg)
        if match:
            field, val = match.groups()
            detail = f"Record with {field} '{val}' already exists."
        else:
            detail = "Record with this unique value already exists."
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"success": False, "detail": detail},
        )

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"success": False, "detail": detail},
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"success": False, "detail": "Internal server error"},
    )

