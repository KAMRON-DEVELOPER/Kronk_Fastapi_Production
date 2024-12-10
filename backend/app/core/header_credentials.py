from fastapi import Request


class HeaderCredentials:
    def __init__(self, temporary_token: str | None):
        self.temporary_token: str | None = temporary_token


def header_dependency(request: Request):
    temporary_token: str | None = request.headers.get("temporary-token")
    return HeaderCredentials(temporary_token=temporary_token)
