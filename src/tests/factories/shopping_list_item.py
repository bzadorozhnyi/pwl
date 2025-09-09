import factory
import pytest


@pytest.fixture
def shopping_list_item_create_payload_factory(
    shopping_list_factory,
):
    class ShoppingListItemCreatePayloadFactory(factory.DictFactory):
        name = factory.Faker("sentence", nb_words=4)
        shopping_list_id = factory.LazyAttribute(lambda o: shopping_list_factory().id)

    return ShoppingListItemCreatePayloadFactory
