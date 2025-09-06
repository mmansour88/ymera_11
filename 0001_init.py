from alembic import op
import sqlalchemy as sa
revision = '0001_init'
down_revision = None
branch_labels = None
depends_on = None
def upgrade():
    op.create_table('users',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('email', sa.String(255), unique=True, index=True),
        sa.Column('password_hash', sa.String(255)),
        sa.Column('role', sa.String(50), server_default='user'),
        sa.Column('created_at', sa.DateTime),
    )
    op.create_table('teams',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String(100), unique=True),
        sa.Column('head_agent_id', sa.Integer, nullable=True),
    )
    op.create_table('agents',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String(100), unique=True),
        sa.Column('specialization', sa.String(100)),
        sa.Column('team_id', sa.Integer, sa.ForeignKey('teams.id'), nullable=True),
        sa.Column('active', sa.Boolean, server_default=sa.text('true'))
    )
    op.create_table('tasks',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('title', sa.String(200)),
        sa.Column('description', sa.Text),
        sa.Column('status', sa.String(50), server_default='queued'),
        sa.Column('team_id', sa.Integer, sa.ForeignKey('teams.id'), nullable=True),
        sa.Column('created_at', sa.DateTime),
        sa.Column('updated_at', sa.DateTime)
    )
    op.create_table('reports',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('task_id', sa.Integer, sa.ForeignKey('tasks.id')),
        sa.Column('summary', sa.Text),
        sa.Column('flag', sa.String(20), server_default='green'),
        sa.Column('created_at', sa.DateTime)
    )
    op.create_table('ratings',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('agent_id', sa.Integer, sa.ForeignKey('agents.id')),
        sa.Column('dimension', sa.String(100)),
        sa.Column('score', sa.Float),
        sa.Column('created_at', sa.DateTime)
    )
def downgrade():
    op.drop_table('ratings'); op.drop_table('reports'); op.drop_table('tasks'); op.drop_table('agents'); op.drop_table('teams'); op.drop_table('users')
