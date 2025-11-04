from typing import Any, Dict

def success_response(message: str, data: Any = None) -> Dict:
    response = {
        "status": "success",
        "message": message
    }
    if data is not None:
        response["data"] = data
    return response

def created_response(message: str, data: Any = None) -> Dict:
    response = {
        "status": "created",
        "message": message
    }
    if data is not None:
        response["data"] = data
    return response

def error_response(message: str, error_code: str = None) -> Dict:
    response = {
        "status": "error",
        "message": message
    }
    if error_code:
        response["error_code"] = error_code
    return response