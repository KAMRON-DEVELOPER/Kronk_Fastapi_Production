from app.users_app.models import BaseModel, UserModel

from tortoise import fields


class FollowModel(BaseModel):
    follower_id: fields.ForeignKeyRelation[UserModel] = fields.ForeignKeyField(model_name="users_app.UserModel", related_name="followings", to_field="id")
    following_id: fields.ForeignKeyRelation[UserModel] = fields.ForeignKeyField(model_name="users_app.UserModel", related_name="followers", to_field="id")

    class Meta:
        table = "follow"

    def __repr__(self):
        return f"🚧 <{self.__class__.__name__}: {self.id}>"
