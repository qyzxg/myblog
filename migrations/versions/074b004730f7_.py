"""empty message

Revision ID: 074b004730f7
Revises: dccafe134b3c
Create Date: 2017-05-31 20:36:44.764286

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '074b004730f7'
down_revision = 'dccafe134b3c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('replies',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('body', sa.String(length=1000), nullable=True),
    sa.Column('created', sa.DateTime(), nullable=True),
    sa.Column('comment_id', sa.Integer(), nullable=True),
    sa.Column('author_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['author_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['comment_id'], ['comments.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_replies_created'), 'replies', ['created'], unique=False)
    op.create_index(op.f('ix_messages_created_at'), 'messages', ['created_at'], unique=False)
    op.create_index(op.f('ix_users_confirmed_on'), 'users', ['confirmed_on'], unique=False)
    op.create_index(op.f('ix_users_created_at'), 'users', ['created_at'], unique=False)
    op.create_index(op.f('ix_users_last_login'), 'users', ['last_login'], unique=False)
    op.create_index(op.f('ix_users_updated_at'), 'users', ['updated_at'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_users_updated_at'), table_name='users')
    op.drop_index(op.f('ix_users_last_login'), table_name='users')
    op.drop_index(op.f('ix_users_created_at'), table_name='users')
    op.drop_index(op.f('ix_users_confirmed_on'), table_name='users')
    op.drop_index(op.f('ix_messages_created_at'), table_name='messages')
    op.drop_index(op.f('ix_replies_created'), table_name='replies')
    op.drop_table('replies')
    # ### end Alembic commands ###
