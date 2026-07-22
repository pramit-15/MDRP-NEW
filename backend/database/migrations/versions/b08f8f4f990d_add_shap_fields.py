"""Add SHAP explanation fields

Revision ID: b08f8f4f990d
Revises: a07e7f3e880c
Create Date: 2026-06-27 12:18:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'b08f8f4f990d'
down_revision: Union[str, None] = 'a07e7f3e880c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add new JSONB columns with empty dict as default
    op.add_column('prediction_explanations', sa.Column('feature_importance', postgresql.JSONB(astext_type=sa.Text()), server_default='{}', nullable=False))
    op.add_column('prediction_explanations', sa.Column('top_features', postgresql.JSONB(astext_type=sa.Text()), server_default='{}', nullable=False))
    op.add_column('prediction_explanations', sa.Column('explanation_summary', postgresql.JSONB(astext_type=sa.Text()), server_default='{}', nullable=False))
    op.add_column('prediction_explanations', sa.Column('positive_contributors', postgresql.JSONB(astext_type=sa.Text()), server_default='{}', nullable=False))
    op.add_column('prediction_explanations', sa.Column('negative_contributors', postgresql.JSONB(astext_type=sa.Text()), server_default='{}', nullable=False))
    op.add_column('prediction_explanations', sa.Column('expected_value', postgresql.JSONB(astext_type=sa.Text()), server_default='{}', nullable=False))
    op.add_column('prediction_explanations', sa.Column('base_value', postgresql.JSONB(astext_type=sa.Text()), server_default='{}', nullable=False))
    
    # Add generated_at
    op.add_column('prediction_explanations', sa.Column('generated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True))


def downgrade() -> None:
    op.drop_column('prediction_explanations', 'generated_at')
    op.drop_column('prediction_explanations', 'base_value')
    op.drop_column('prediction_explanations', 'expected_value')
    op.drop_column('prediction_explanations', 'negative_contributors')
    op.drop_column('prediction_explanations', 'positive_contributors')
    op.drop_column('prediction_explanations', 'explanation_summary')
    op.drop_column('prediction_explanations', 'top_features')
    op.drop_column('prediction_explanations', 'feature_importance')
