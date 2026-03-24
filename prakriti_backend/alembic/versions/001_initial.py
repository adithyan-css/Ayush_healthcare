"""initial
Revision ID: 001
Revises:
Create Date: 2026-03-24 10:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
"""initial
Revision ID: 001
Revises: 
Create Date: 2026-03-24 10:00:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    pass

def downgrade() -> None:
    pass
