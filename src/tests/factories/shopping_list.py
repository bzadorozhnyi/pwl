import uuid
from datetime import datetime

import factory
import pytest

from models.shopping_list import ShoppingList


@pytest.fixture
def shopping_list_factory(
    db_session, family_factory, family_member_factory, user_factory
):
    class ShoppingListFactory(factory.alchemy.SQLAlchemyModelFactory):
        class Meta:
            model = ShoppingList
            sqlalchemy_session = db_session.sync_session

        id = factory.LazyFunction(uuid.uuid4)
        name = factory.Faker("sentence", nb_words=4)
        creator_id = None
        family_id = factory.LazyAttribute(lambda o: family_factory().id)

        created_at = factory.LazyFunction(datetime.now)
        updated_at = factory.LazyFunction(datetime.now)

        @factory.post_generation
        def set_creator(self, create, extracted, **kwargs):
            if self.creator_id is not None:
                return
            creator = user_factory()
            family_member_factory(user_id=creator.id, family_id=self.family_id)

            self.creator_id = creator.id

    return ShoppingListFactory


@pytest.fixture
def shopping_list_create_payload_factory(
    family_factory,
):
    class ShoppingListCreatePayloadFactory(factory.DictFactory):
        name = factory.Faker("sentence", nb_words=4)
        family_id = factory.LazyAttribute(lambda o: family_factory().id)

    return ShoppingListCreatePayloadFactory
