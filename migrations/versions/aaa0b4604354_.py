"""empty message

Revision ID: aaa0b4604354
Revises: a05ed97bab59
Create Date: 2019-11-27 18:26:05.862930

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'aaa0b4604354'
down_revision = 'a05ed97bab59'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('credit_report_accounts', schema=None) as batch_op:
        batch_op.add_column(sa.Column('client_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('email', sa.String(length=255), nullable=False))
        batch_op.create_unique_constraint('_email_uc', ['email'])
        batch_op.create_foreign_key('fk_client', 'clients', ['client_id'], ['id'])

    with op.batch_alter_table('credit_report_data', schema=None) as batch_op:
        batch_op.add_column(sa.Column('account_id', sa.Integer(), nullable=True))
        # batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key('fk_credit_report_data', 'credit_report_accounts', ['account_id'], ['id'])
        batch_op.drop_column('candidate_id')

    with op.batch_alter_table('scrape_tasks', schema=None) as batch_op:
        batch_op.add_column(sa.Column('account_id', sa.Integer(), nullable=True))
        # batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key('fk_credit_report_data', 'credit_report_accounts', ['account_id'], ['id'])
        batch_op.drop_column('candidate_id')
        batch_op.drop_column('description')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('scrape_tasks', schema=None) as batch_op:
        batch_op.add_column(sa.Column('description', sa.VARCHAR(length=128), nullable=True))
        batch_op.add_column(sa.Column('candidate_id', sa.INTEGER(), nullable=True))
        batch_op.drop_constraint('fk_credit_report_data', type_='foreignkey')
        batch_op.create_foreign_key(None, 'candidates', ['candidate_id'], ['id'])
        batch_op.drop_column('account_id')

    with op.batch_alter_table('credit_report_data', schema=None) as batch_op:
        batch_op.add_column(sa.Column('candidate_id', sa.INTEGER(), nullable=True))
        batch_op.drop_constraint('fk_credit_report_data', type_='foreignkey')
        batch_op.create_foreign_key(None, 'candidates', ['candidate_id'], ['id'])
        batch_op.drop_column('account_id')

    with op.batch_alter_table('credit_report_accounts', schema=None) as batch_op:
        batch_op.drop_constraint('fk_client', type_='foreignkey')
        batch_op.drop_constraint('_email_uc', type_='unique')
        batch_op.drop_column('email')
        batch_op.drop_column('client_id')

    # ### end Alembic commands ###
