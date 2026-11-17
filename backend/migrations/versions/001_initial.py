from alembic import op
import sqlalchemy as sa

revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('users', sa.Column('id', sa.Integer(), primary_key=True), sa.Column('name', sa.String(200), nullable=False), sa.Column('email', sa.String(320), nullable=False, unique=True), sa.Column('role', sa.String(20), nullable=False))
    op.create_table('courses', sa.Column('id', sa.Integer(), primary_key=True), sa.Column('name', sa.String(200), nullable=False))
    op.create_table('enrollments', sa.Column('id', sa.Integer(), primary_key=True), sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False), sa.Column('course_id', sa.Integer(), sa.ForeignKey('courses.id'), nullable=False), sa.Column('role', sa.String(20), nullable=False), sa.UniqueConstraint('user_id', 'course_id'))
    op.create_table('assignments', sa.Column('id', sa.Integer(), primary_key=True), sa.Column('course_id', sa.Integer(), sa.ForeignKey('courses.id'), nullable=False), sa.Column('title', sa.String(200), nullable=False), sa.Column('description_md', sa.Text(), nullable=False), sa.Column('side_panel_md', sa.Text(), nullable=False), sa.Column('starter_code', sa.JSON(), nullable=False), sa.Column('enabled_languages', sa.JSON(), nullable=False), sa.Column('intellisense_enabled', sa.Boolean(), nullable=False), sa.Column('paste_enabled', sa.Boolean(), nullable=False), sa.Column('due_at', sa.DateTime(timezone=True), nullable=True))


def downgrade():
    op.drop_table('assignments')
    op.drop_table('enrollments')
    op.drop_table('courses')
    op.drop_table('users')
