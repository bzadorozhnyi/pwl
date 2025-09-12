from sqladmin import ModelView

from models.shopping_list import ShoppingList


class ShoppingListAdmin(ModelView, model=ShoppingList):
    name = "Shopping List"
    name_plural = "Shopping Lists"
    icon = "fa-solid fa-list"

    column_list = [
        ShoppingList.id,
        ShoppingList.name,
        ShoppingList.family_id,
        ShoppingList.creator_id,
        ShoppingList.created_at,
        ShoppingList.updated_at,
    ]

    column_details_list = [
        ShoppingList.id,
        ShoppingList.name,
        ShoppingList.family_id,
        ShoppingList.creator_id,
        ShoppingList.created_at,
        ShoppingList.updated_at,
    ]

    column_labels = {
        ShoppingList.id: "ID",
        ShoppingList.name: "Name",
        ShoppingList.family_id: "Family",
        ShoppingList.creator_id: "Creator",
        ShoppingList.created_at: "Created At",
        ShoppingList.updated_at: "Updated At",
    }

    column_searchable_list = [ShoppingList.name]
    column_sortable_list = [
        ShoppingList.created_at,
        ShoppingList.updated_at,
        ShoppingList.name,
    ]
