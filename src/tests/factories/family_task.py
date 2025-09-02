import uuid
from datetime import datetime

import factory
import pytest

from models.family_task import FamilyTask


@pytest.fixture
def family_task_factory(
    db_session, family_factory, family_member_factory, user_factory
):
    class FamilyTaskFactory(factory.alchemy.SQLAlchemyModelFactory):
        class Meta:
            model = FamilyTask
            sqlalchemy_session = db_session.sync_session

        id = factory.LazyFunction(uuid.uuid4)
        title = factory.Faker("sentence", nb_words=4)
        done = False
        created_at = factory.LazyFunction(datetime.now)
        updated_at = factory.LazyFunction(datetime.now)

        family_id = factory.LazyAttribute(lambda o: family_factory().id)

        creator_id = None
        assignee_id = None

        @factory.post_generation
        def set_creator(self, create, extracted, **kwargs):
            if self.creator_id is not None:
                return
            creator = user_factory()
            family_member_factory(user_id=creator.id, family_id=self.family_id)

            self.creator_id = creator.id

        @factory.post_generation
        def set_assignee(self, create, extracted, **kwargs):
            if self.assignee_id is not None:
                return
            assignee = user_factory()
            family_member_factory(user_id=assignee.id, family_id=self.family_id)

            self.assignee_id = assignee.id

    return FamilyTaskFactory


@pytest.fixture
def family_task_create_payload_factory(
    family_factory, user_factory, family_member_factory
):
    class FamilyTaskCreatePayloadFactory(factory.DictFactory):
        family_id = factory.LazyAttribute(lambda o: family_factory().id)
        title = factory.Faker("sentence", nb_words=4)
        assignee_id = None

        @factory.post_generation
        def set_assignee(self, create, extracted, **kwargs):
            if self["assignee_id"] is not None:
                return
            assignee = user_factory()
            family_member_factory(user_id=assignee.id, family_id=self["family_id"])
            self["assignee_id"] = str(assignee.id)

    return FamilyTaskCreatePayloadFactory


@pytest.fixture
def family_task_update_payload_factory(
    user_factory, family_factory, family_member_factory
):
    class FamilyTaskUpdatePayloadFactory(factory.DictFactory):
        assignee_id = None
        title = factory.Faker("sentence", nb_words=4)
        done = factory.Faker("pybool")

        @factory.post_generation
        def set_assignee(self, create, extracted, **kwargs):
            if self["assignee_id"] is not None:
                return
            assignee = user_factory()
            family = family_factory()
            family_member_factory(user_id=assignee.id, family_id=family.id)
            self["assignee_id"] = str(assignee.id)

    return FamilyTaskUpdatePayloadFactory
