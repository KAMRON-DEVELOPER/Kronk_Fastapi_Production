import inspect
from typing import Union, get_args, get_origin

from fastapi import File, Form, UploadFile


def as_form(cls):
    """Decorator to make a Pydantic model usable with FastAPI's Form and File."""
    new_parameters = []

    for field_name, field_info in cls.__fields__.items():
        field_type = field_info.annotation  # typing.Optional[fastapi.datastructures.UploadFile] for Optional[UploadFile] and typing.Optional[str] for Optional[str]
        type_args = get_args(field_type)  # (fastapi.datastructures.UploadFile, NoneType) for Optional[UploadFile] and (str, NoneType) for Optional[str]
        is_optional: bool = get_origin(field_type) is Union and type(None) in type_args

        if is_optional or field_info.default is not None:
            param = Form(field_info.default if field_info.default is not None else None)
        elif field_info.required:
            param = Form(...)
        else:
            param = Form(None)

        if UploadFile in type_args:  # If field expects an upload file
            param = File(None) if is_optional else File(...)

        new_parameters.append(
            inspect.Parameter(
                field_name,
                inspect.Parameter.KEYWORD_ONLY,
                default=param,
                annotation=field_type,
            )
        )

    async def as_form_func(**kwargs):
        return cls(**kwargs)

    sig = inspect.signature(as_form_func)
    sig = sig.replace(parameters=new_parameters)
    as_form_func.__signature__ = sig
    setattr(cls, "as_form", as_form_func)
    return cls
