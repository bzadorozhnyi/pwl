import uuid

import factory
import pytest

from models.family import Family, FamilyMember, FamilyRole


@pytest.fixture
def family_factory(db_session):
    class FamilyFactory(factory.alchemy.SQLAlchemyModelFactory):
        class Meta:
            model = Family
            sqlalchemy_session = db_session.sync_session

        id = factory.LazyFunction(uuid.uuid4)

    return FamilyFactory


@pytest.fixture
def family_member_factory(db_session, family_factory, user_factory):
    class FamilyMemberFactory(factory.alchemy.SQLAlchemyModelFactory):
        class Meta:
            model = FamilyMember
            sqlalchemy_session = db_session.sync_session

        family_id = factory.LazyAttribute(lambda o: family_factory().id)
        user_id = factory.LazyAttribute(lambda o: user_factory().id)

        role = FamilyRole.MEMBER

    return FamilyMemberFactory
