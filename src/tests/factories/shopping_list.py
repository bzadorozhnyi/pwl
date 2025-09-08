import factory
import pytest


@pytest.fixture
def shopping_list_create_payload_factory(
    family_factory,
):
    class ShoppingListCreatePayloadFactory(factory.DictFactory):
        name = factory.Faker("sentence", nb_words=4)
        family_id = factory.LazyAttribute(lambda o: family_factory().id)

    return ShoppingListCreatePayloadFactory
