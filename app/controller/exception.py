from fastapi import HTTPException, status

def unauthorized_exception(message: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={
            "message": message,
        },
        headers={"WWW-Authenticate": "Bearer"},
    )
    
def not_found_exception(resource_id: str, message: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={
            "resource_id": resource_id,
            "message": message,
        },
    )

def bad_request_exception(resource_id: str, message: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail={
            "resource_id": resource_id,
            "message": message,
        },
    )
