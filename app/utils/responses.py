from fastapi.responses import JSONResponse
from fastapi import status

def success_response(message: str, data: dict = None):
    response_data = {"success": True, "message": message}
    if data:
        response_data.update(data)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=response_data
    )

def created_response(message: str, data: dict = None):
    response_data = {"success": True, "message": message}
    if data:
        response_data.update(data)
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=response_data
    )

def error_response(message: str, status_code: int = 400):
    return JSONResponse(
        status_code=status_code,
        content={"success": False, "error": message}
    )