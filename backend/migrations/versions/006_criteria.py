from alembic import op
import sqlalchemy as sa

revision = '006'
down_revision = '005'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('criteria',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('assignment_id', sa.Integer(), sa.ForeignKey('assignments.id'), nullable=False),
        sa.Column('kind', sa.String(10), nullable=False),
        sa.Column('label', sa.String(200), nullable=False),
        sa.Column('max_points', sa.Numeric(10, 2), nullable=False),
        sa.Column('check_rule_ref', sa.String(36), nullable=True),
        sa.Column('position', sa.Integer(), nullable=False))


def downgrade():
    op.drop_table('criteria')
