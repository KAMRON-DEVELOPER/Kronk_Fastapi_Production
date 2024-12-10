from typing import Annotated

from app.core.config import settings
from app.core.header_credentials import HeaderCredentials, header_dependency
from fastapi import Depends, Security
from fastapi_jwt import JwtAuthorizationCredentials

jwtAccessAuthCredentialsDependency = Annotated[
    JwtAuthorizationCredentials,
    Security(dependency=settings.jwtAccessBearer),
]
jwtRefreshAuthCredentialsDependency = Annotated[
    JwtAuthorizationCredentials,
    Security(dependency=settings.jwtRefreshBearer),
]
headerCredentialsDependency = Annotated[
    HeaderCredentials,
    Depends(dependency=header_dependency),
]
