from alembic import op
import sqlalchemy as sa

revision = '007'
down_revision = '006'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('assignments', sa.Column('show_criteria_to_student', sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column('submissions', sa.Column('rubric_snapshot', sa.JSON(), nullable=True))
    op.create_table('evaluations',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('submission_id', sa.Integer(), sa.ForeignKey('submissions.id'), nullable=False, unique=True),
        sa.Column('suggested_points', sa.Numeric(12, 2), nullable=False),
        sa.Column('final_points', sa.Numeric(12, 2), nullable=False),
        sa.Column('feedback', sa.Text(), nullable=False),
        sa.Column('graded_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('source_submitted_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('criteria_snapshot', sa.JSON(), nullable=False))
    op.create_table('criterion_results',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('evaluation_id', sa.Integer(), sa.ForeignKey('evaluations.id'), nullable=False),
        sa.Column('criterion_id', sa.String(36), nullable=False),
        sa.Column('auto_result', sa.Boolean(), nullable=True),
        sa.Column('teacher_override', sa.Boolean(), nullable=True),
        sa.Column('points', sa.Numeric(10, 2), nullable=False),
        sa.Column('position', sa.Integer(), nullable=False),
        sa.UniqueConstraint('evaluation_id', 'criterion_id'))


def downgrade():
    op.drop_table('criterion_results')
    op.drop_table('evaluations')
    op.drop_column('submissions', 'rubric_snapshot')
    op.drop_column('assignments', 'show_criteria_to_student')
