from sqladmin import ModelView

from core.jwt import AuthJWTService
from models.user import User


class UserAdmin(ModelView, model=User):
    column_list = [
        User.id,
        User.email,
        User.username,
        User.first_name,
        User.last_name,
        User.created_at,
        User.updated_at,
        User.is_admin,
    ]

    column_searchable_list = [
        User.email,
        User.username,
        User.first_name,
        User.last_name,
    ]

    column_sortable_list = [User.created_at, User.updated_at, User.email, User.username]

    async def on_model_change(self, data: dict, model: User, is_created: bool, request):
        """Intercept data before saving to hash the password"""
        password = data.get("password")

        if is_created:
            # when creating a user, password is required → hash it
            if not password:
                raise ValueError("Password is required for new users")
            data["password"] = AuthJWTService().get_password_hash(password)
        else:
            # when updating — only if a new password is entered
            if password and password != model.password:
                data["password"] = AuthJWTService().get_password_hash(password)

        return data
