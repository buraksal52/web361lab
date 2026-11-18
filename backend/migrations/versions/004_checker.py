from alembic import op
import sqlalchemy as sa

revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('assignments', sa.Column('checker_enabled', sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column('assignments', sa.Column('check_rules', sa.JSON(), nullable=False, server_default='[]'))
    op.add_column('assignments', sa.Column('show_results_to_student', sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column('submissions', sa.Column('check_result', sa.JSON(), nullable=True))


def downgrade():
    op.drop_column('submissions', 'check_result')
    op.drop_column('assignments', 'show_results_to_student')
    op.drop_column('assignments', 'check_rules')
    op.drop_column('assignments', 'checker_enabled')
