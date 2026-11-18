from alembic import op
import sqlalchemy as sa

revision = '005'
down_revision = '004'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('assignments', sa.Column('diagnostics_enabled', sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column('assignments', sa.Column('lint_rules', sa.JSON(), nullable=False, server_default='[]'))
    op.add_column('submissions', sa.Column('lint_report', sa.JSON(), nullable=True))


def downgrade():
    op.drop_column('submissions', 'lint_report')
    op.drop_column('assignments', 'lint_rules')
    op.drop_column('assignments', 'diagnostics_enabled')
