import uuid
from datetime import datetime

import factory
import pytest

from models.verify_token import VerifyToken


@pytest.fixture
def verify_token_factory(db_session, user_factory):
    class VerifyTokenFactory(factory.alchemy.SQLAlchemyModelFactory):
        class Meta:
            model = VerifyToken
            sqlalchemy_session = db_session.sync_session

        id = factory.Sequence(lambda n: n + 1)
        user_id = factory.LazyAttribute(lambda o: user_factory().id)
        email = factory.Faker("email")
        token = factory.LazyFunction(uuid.uuid4)
        created_at = factory.LazyFunction(datetime.now)

    return VerifyTokenFactory
