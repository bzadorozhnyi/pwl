import factory
import pytest
from faker import Faker

faker = Faker()


@pytest.fixture
def ingredients_list_create_payload_factory(
    family_factory,
):
    class IngredientsListCreatePayloadFactory(factory.DictFactory):
        title = factory.Faker("sentence", nb_words=4)
        family_id = factory.LazyAttribute(lambda o: family_factory().id)

        @factory.post_generation
        def ingredients(self, create, extracted, **kwargs):
            count = extracted or 3
            self["ingredients"] = [
                {
                    "name": f"{faker.word()} {faker.random_int(1, 10)} {faker.random_element(['kg', 'g', 'ml'])}"
                }
                for _ in range(count)
            ]

    return IngredientsListCreatePayloadFactory
