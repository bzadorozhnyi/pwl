from sqladmin import ModelView

from models.family_task import FamilyTask


class FamilyTaskAdmin(ModelView, model=FamilyTask):
    name = "Family Task"
    name_plural = "Family Tasks"
    icon = "fa-solid fa-tasks"

    column_list = [
        FamilyTask.id,
        FamilyTask.title,
        FamilyTask.family_id,
        FamilyTask.creator_id,
        FamilyTask.assignee_id,
        FamilyTask.done,
        FamilyTask.created_at,
        FamilyTask.updated_at,
    ]

    column_details_list = [
        FamilyTask.id,
        FamilyTask.title,
        FamilyTask.family,
        FamilyTask.creator,
        FamilyTask.assignee,
        FamilyTask.done,
        FamilyTask.created_at,
        FamilyTask.updated_at,
    ]

    column_labels = {
        FamilyTask.id: "ID",
        FamilyTask.title: "Title",
        FamilyTask.family_id: "Family",
        FamilyTask.creator_id: "Creator",
        FamilyTask.assignee_id: "Assignee",
        FamilyTask.done: "Done",
        FamilyTask.created_at: "Created At",
        FamilyTask.updated_at: "Updated At",
    }

    column_searchable_list = [FamilyTask.title]
    column_sortable_list = [
        FamilyTask.created_at,
        FamilyTask.updated_at,
        FamilyTask.title,
        FamilyTask.done,
    ]

    form_excluded_columns = ["created_at", "updated_at"]
