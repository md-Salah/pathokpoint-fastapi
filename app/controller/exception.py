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


def forbidden_exception(resource_id: str, message: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail={
            "resource_id": resource_id,
            "message": message,
        },
    )

# Class based approach


class UnauthorizedException(HTTPException):
    def __init__(self, message: str):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"message": message},
            headers={"WWW-Authenticate": "Bearer"},
        )


class NotFoundException(HTTPException):
    def __init__(self, message: str, resource_id: str | None = None):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"resource_id": resource_id, "message": message},
        )


class BadRequestException(HTTPException):
    def __init__(self, message: str, resource_id: str | None = None):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"resource_id": resource_id, "message": message},
        )


class ForbiddenException(HTTPException):
    def __init__(self, message: str, resource_id: str | None = None):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"resource_id": resource_id, "message": message},
        )
