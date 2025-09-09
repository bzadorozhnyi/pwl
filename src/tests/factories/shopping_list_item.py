import uuid

import factory
import pytest

from models.shopping_list_item import ShoppingListItem


@pytest.fixture
def shopping_list_item_factory(
    db_session,
    family_factory,
    family_member_factory,
    user_factory,
    shopping_list_factory,
):
    class ShoppingListItemFactory(factory.alchemy.SQLAlchemyModelFactory):
        class Meta:
            model = ShoppingListItem
            sqlalchemy_session = db_session.sync_session

        id = factory.LazyFunction(uuid.uuid4)
        name = factory.Faker("sentence", nb_words=4)
        purchased = factory.Faker("pybool")

        creator_id = None
        shopping_list_id = None

        @factory.post_generation
        def set_creator(self, create, extracted, **kwargs):
            if self.creator_id is not None:
                return

            creator = user_factory()
            family = family_factory()
            family_member_factory(user_id=creator.id, family_id=family.id)

            self.creator_id = creator.id

        @factory.post_generation
        def set_shopping_list(self, create, extracted, **kwargs):
            if self.shopping_list_id is not None:
                return

            if self.creator_id is None:
                creator = user_factory()
                family = family_factory()
                family_member_factory(user_id=creator.id, family_id=family.id)

                self.creator_id = creator.id

            shopping_list = shopping_list_factory(creator_id=self.creator_id)
            self.shopping_list_id = shopping_list.id

    return ShoppingListItemFactory


@pytest.fixture
def shopping_list_item_create_payload_factory(
    shopping_list_factory,
):
    class ShoppingListItemCreatePayloadFactory(factory.DictFactory):
        name = factory.Faker("sentence", nb_words=4)
        shopping_list_id = factory.LazyAttribute(lambda o: shopping_list_factory().id)

    return ShoppingListItemCreatePayloadFactory
