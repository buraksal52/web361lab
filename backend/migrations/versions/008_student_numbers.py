from alembic import op
import sqlalchemy as sa

revision = '008'
down_revision = '007'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('users', sa.Column('student_number', sa.String(9), nullable=True))
    op.create_unique_constraint('uq_users_student_number', 'users', ['student_number'])


def downgrade():
    op.drop_constraint('uq_users_student_number', 'users', type_='unique')
    op.drop_column('users', 'student_number')
