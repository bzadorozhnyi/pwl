from sqladmin import ModelView

from models.verify_token import VerifyToken


class VerifyTokenAdmin(ModelView, model=VerifyToken):
    name = "Verify Token"
    name_plural = "Verify Tokens"
    icon = "fa-solid fa-key"

    column_list = [
        VerifyToken.id,
        VerifyToken.user_id,
        VerifyToken.email,
        VerifyToken.token,
        VerifyToken.created_at,
    ]

    column_details_list = [
        VerifyToken.id,
        VerifyToken.user_id,
        VerifyToken.email,
        VerifyToken.token,
        VerifyToken.created_at,
    ]

    column_labels = {
        VerifyToken.id: "ID",
        VerifyToken.user_id: "User",
        VerifyToken.email: "Email",
        VerifyToken.token: "Token",
        VerifyToken.created_at: "Created At",
    }

    column_searchable_list = [VerifyToken.email, VerifyToken.token]
    column_sortable_list = [VerifyToken.created_at, VerifyToken.email]
