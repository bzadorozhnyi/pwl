from sqladmin import ModelView

from models.family import Family, FamilyMember


class FamilyAdmin(ModelView, model=Family):
    name = "Family"
    name_plural = "Families"
    icon = "fa-solid fa-house"

    column_list = [Family.id]
    column_details_list = [Family.id, Family.members, Family.tasks]

    column_labels = {
        Family.id: "ID",
        Family.members: "Members",
        Family.tasks: "Tasks",
    }

    column_sortable_list = [Family.id]
    column_searchable_list = [Family.id]

    form_excluded_columns = ["members", "tasks"]


class FamilyMemberAdmin(ModelView, model=FamilyMember):
    name = "Family Member"
    name_plural = "Family Members"
    icon = "fa-solid fa-user-group"

    column_list = [FamilyMember.family_id, FamilyMember.user_id, FamilyMember.role]
    column_details_list = [
        FamilyMember.family_id,
        FamilyMember.user_id,
        FamilyMember.role,
        FamilyMember.family,
        FamilyMember.user,
    ]

    column_labels = {
        FamilyMember.family_id: "Family ID",
        FamilyMember.user_id: "User ID",
        FamilyMember.role: "Role",
        FamilyMember.family: "Family",
        FamilyMember.user: "User",
    }

    column_sortable_list = [
        FamilyMember.family_id,
        FamilyMember.user_id,
        FamilyMember.role,
    ]
    column_searchable_list = [FamilyMember.family_id, FamilyMember.user_id]
