from datetime import datetime

import factory
import pytest

from core.jwt import AuthJWTService
from models.user import User, UserRole


@pytest.fixture
def user_factory(db_session):
    class BaseUserFactory(factory.alchemy.SQLAlchemyModelFactory):
        class Meta:
            model = User
            sqlalchemy_session = db_session.sync_session

        id = factory.Sequence(lambda n: n + 1)
        email = factory.Faker("email")
        full_name = factory.Faker("name")
        password = "password"
        created_at = factory.LazyFunction(datetime.now)
        updated_at = factory.LazyFunction(datetime.now)
        role = UserRole.USER

        @factory.post_generation
        def set_password(obj, create, extracted, **kwargs):
            raw_password = extracted or obj.password
            obj.password = AuthJWTService().get_password_hash(raw_password)

    return BaseUserFactory


@pytest.fixture
def user_create_payload_factory():
    class UserCreatePayloadFactory(factory.Factory):
        class Meta:
            model = dict

        email = factory.Faker("email")
        full_name = factory.Faker("name")
        password = factory.Faker("password")

    return UserCreatePayloadFactory
