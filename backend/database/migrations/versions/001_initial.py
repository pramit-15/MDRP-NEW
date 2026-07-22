"""Initial migration

Revision ID: 001_initial
Revises: 
Create Date: 2026-06-26 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create users table
    op.create_table('users',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('clerk_id', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_clerk_id'), 'users', ['clerk_id'], unique=True)

    # Create predictions table
    op.create_table('predictions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('heart_risk', sa.Float(), nullable=False),
        sa.Column('diabetes_risk', sa.Float(), nullable=False),
        sa.Column('kidney_risk', sa.Float(), nullable=False),
        sa.Column('health_condition', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('scores_detail', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('clinical_scores', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('inputs_used', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('used_defaults', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_predictions_user_id'), 'predictions', ['user_id'], unique=False)

    # Create prediction_explanations table
    op.create_table('prediction_explanations',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('prediction_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('shap_values', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['prediction_id'], ['predictions.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('prediction_id')
    )

    # Create uploaded_reports table
    op.create_table('uploaded_reports',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('prediction_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('filename', sa.String(), nullable=False),
        sa.Column('parsed_data', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['prediction_id'], ['predictions.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('prediction_id')
    )


def downgrade() -> None:
    op.drop_table('uploaded_reports')
    op.drop_table('prediction_explanations')
    op.drop_index(op.f('ix_predictions_user_id'), table_name='predictions')
    op.drop_table('predictions')
    op.drop_index(op.f('ix_users_clerk_id'), table_name='users')
    op.drop_table('users')
