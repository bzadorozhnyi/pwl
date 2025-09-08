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
    ]

    column_searchable_list = [
        User.email,
        User.username,
        User.first_name,
        User.last_name,
    ]

    column_sortable_list = [User.created_at, User.updated_at, User.email, User.username]

    async def on_model_change(self, data: dict, model: User, is_created: bool, request):
        """Перехоплюємо дані перед збереженням, щоб хешувати пароль"""
        password = data.get("password")
        if password:
            data["password"] = AuthJWTService().get_password_hash(password)
        return data
