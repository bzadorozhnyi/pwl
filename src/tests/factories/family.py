import uuid

import factory
import pytest

from models.family import Family, FamilyRole


@pytest.fixture
def family_factory(db_session, user_factory):
    class FamilyFactory(factory.alchemy.SQLAlchemyModelFactory):
        class Meta:
            model = Family
            sqlalchemy_session = db_session.sync_session

        id = factory.LazyFunction(uuid.uuid4)
        user_id = factory.LazyAttribute(lambda o: user_factory().id)
        role = FamilyRole.MEMBER

    return FamilyFactory
