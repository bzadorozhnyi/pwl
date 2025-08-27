from contextlib import asynccontextmanager
from contextvars import ContextVar

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from core.config import settings

engine = create_async_engine(settings.db_url, echo=True)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


# ContextVar ensures transaction state is isolated per task.
_transaction_active_ctx = ContextVar("_transaction_active", default=False)


class AsyncSessionProxy:
    """
    A proxy wrapper around AsyncSession that adds Django-like transaction management:
    - `session.transaction()` context manager for atomic blocks.
    - `commit()` behaves like Django ORM save():
        * inside a transaction → only flush.
        * outside → commit immediately.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    @asynccontextmanager
    async def transaction(self):
        """
        Transaction context manager (similar to Django's `transaction.atomic`).
        Rolls back automatically on error, commits on success.
        """
        token = _transaction_active_ctx.set(True)
        try:
            if self.session.in_transaction():
                yield
            else:
                async with self.session.begin():
                    yield

            await self.session.commit()
        except Exception:
            await self.session.rollback()
            raise
        finally:
            _transaction_active_ctx.reset(token)

    async def commit(self):
        """
        Commit immediately if outside a transaction,
        otherwise flush staged changes.
        """
        if not _transaction_active_ctx.get():
            await self.session.commit()
        else:
            await self.session.flush()

    async def rollback(self):
        """Rollback current transaction."""
        await self.session.rollback()

    def __getattr__(self, item):
        """Delegate unknown attributes to underlying AsyncSession."""
        return getattr(self.session, item)


async def get_session():
    async with async_session() as session:
        yield AsyncSessionProxy(session)
