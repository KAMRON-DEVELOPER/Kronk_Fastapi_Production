from enum import Enum

from tortoise.models import Model

from tortoise import fields


class GenderEnum(str, Enum):
    MALE = "male"
    FEMALE = "female"


class CountryEnum(str, Enum):
    UZBEKISTAN = "Uzbekistan"
    UNITED_KINGDOM = "United Kingdom"
    UNITED_STATES = "United States"
    CANADA = "Canada"
    FRANCE = "France"
    GERMANY = "Germany"


class StateOrProvinceEnum(str, Enum):
    TASHKENT = "Tashkent"
    LONDON = "London"
    NEW_YORK = "New York"
    TORONTO = "Toronto"
    PARIS = "Paris"
    BERLIN = "Berlin"


class BaseModel(Model):
    id = fields.UUIDField(primary_key=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        abstract = True


class UserModel(BaseModel):
    first_name = fields.CharField(max_length=50, null=True)
    last_name = fields.CharField(max_length=50, null=True)
    username = fields.CharField(max_length=50, unique=True)
    email = fields.CharField(max_length=50, unique=True)
    password = fields.CharField(max_length=255)
    avatar = fields.CharField(max_length=255, null=True)
    banner = fields.CharField(max_length=255, null=True)
    banner_color = fields.CharField(max_length=6, null=True)
    birthdate = fields.DatetimeField(null=True)
    bio = fields.TextField(null=True)
    gender = fields.CharEnumField(enum_type=GenderEnum, null=True)
    country = fields.CharEnumField(enum_type=CountryEnum, null=True)
    state_or_province = fields.CharEnumField(enum_type=StateOrProvinceEnum, null=True)
    is_admin = fields.BooleanField(default=False)
    is_blocked = fields.BooleanField(default=False)

    class Meta:
        table = "user"

    class PydanticMeta:
        allow_cycles = True
        exclude = ("password",)

    def __str__(self):
        return f"🚧 <{self.__class__.__name__}: {self.username}>"

    def __repr__(self):
        return f"🚧 <{self.__class__.__name__}: {self.username}>"
