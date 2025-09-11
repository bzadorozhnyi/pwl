from sqladmin import ModelView

from models.shopping_list_item import ShoppingListItem


class ShoppingListItemAdmin(ModelView, model=ShoppingListItem):
    name = "Shopping List Item"
    name_plural = "Shopping List Items"
    icon = "fa-solid fa-box"

    column_list = [
        ShoppingListItem.id,
        ShoppingListItem.name,
        ShoppingListItem.shopping_list_id,
        ShoppingListItem.creator_id,
        ShoppingListItem.purchased,
        ShoppingListItem.created_at,
        ShoppingListItem.updated_at,
    ]

    column_details_list = [
        ShoppingListItem.id,
        ShoppingListItem.name,
        ShoppingListItem.shopping_list_id,
        ShoppingListItem.creator_id,
        ShoppingListItem.purchased,
        ShoppingListItem.created_at,
        ShoppingListItem.updated_at,
    ]

    column_labels = {
        ShoppingListItem.id: "ID",
        ShoppingListItem.name: "Name",
        ShoppingListItem.shopping_list_id: "Shopping List",
        ShoppingListItem.creator_id: "Creator",
        ShoppingListItem.purchased: "Purchased",
        ShoppingListItem.created_at: "Created At",
        ShoppingListItem.updated_at: "Updated At",
    }

    column_searchable_list = [ShoppingListItem.name]
    column_sortable_list = [
        ShoppingListItem.created_at,
        ShoppingListItem.updated_at,
        ShoppingListItem.name,
        ShoppingListItem.purchased,
    ]