"""rename UserDB to User

Revision ID: 85d68070e2c6
Revises: 194d3095b205
Create Date: 2025-08-18 16:00:08.139666

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "85d68070e2c6"
down_revision: Union[str, Sequence[str], None] = "194d3095b205"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.rename_table("userdb", "user")


def downgrade() -> None:
    """Downgrade schema."""
    op.rename_table("user", "userdb")
