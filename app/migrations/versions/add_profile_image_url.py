"""Add profile image URL to proz profiles

Revision ID: add_profile_image_url
Revises: previous_revision_id
Create Date: 2024-12-19 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'add_profile_image_url'
down_revision = 'your_previous_revision_id'  # Replace with your latest revision
branch_labels = None
depends_on = None

def upgrade():
    # Add profile_image_url column to proz_profiles table
    op.add_column('proz_profiles', 
                  sa.Column('profile_image_url', sa.String(length=500), nullable=True))

def downgrade():
    # Remove profile_image_url column
    op.drop_column('proz_profiles', 'profile_image_url')