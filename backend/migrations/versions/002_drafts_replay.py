from alembic import op
import sqlalchemy as sa

revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('users', sa.Column('recording_consent_at', sa.DateTime(timezone=True), nullable=True))
    op.create_table('drafts',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('assignment_id', sa.Integer(), sa.ForeignKey('assignments.id'), nullable=False),
        sa.Column('student_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('initial_code', sa.JSON(), nullable=False), sa.Column('code', sa.JSON(), nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('paste_blocked_count', sa.Integer(), nullable=False),
        sa.Column('blur_count', sa.Integer(), nullable=False),
        sa.Column('max_insert_chars', sa.Integer(), nullable=False),
        sa.UniqueConstraint('assignment_id', 'student_id'))
    op.create_table('replay_events', sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('draft_id', sa.Integer(), sa.ForeignKey('drafts.id'), nullable=False),
        sa.Column('t_ms', sa.Integer(), nullable=False), sa.Column('kind', sa.String(30), nullable=False),
        sa.Column('payload', sa.JSON(), nullable=False))
    op.create_table('replay_batches', sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('draft_id', sa.Integer(), sa.ForeignKey('drafts.id'), nullable=False),
        sa.Column('batch_id', sa.String(36), nullable=False), sa.UniqueConstraint('draft_id', 'batch_id'))


def downgrade():
    op.drop_table('replay_batches')
    op.drop_table('replay_events')
    op.drop_table('drafts')
    op.drop_column('users', 'recording_consent_at')
