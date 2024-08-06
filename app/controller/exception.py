from fastapi import HTTPException, status


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


class ConflictException(HTTPException):
    def __init__(self, message: str, resource_id: str | None = None):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail={"resource_id": resource_id, "message": message},
        )


class ServerErrorException(HTTPException):
    def __init__(self, message: str, resource_id: str | None = None):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"resource_id": resource_id, "message": message},
        )


class UnhandledException(HTTPException):
    def __init__(self, message: str = "Unknown error occured. Please try again later.", resource_id: str | None = None):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"resource_id": resource_id, "message": message},
        )
