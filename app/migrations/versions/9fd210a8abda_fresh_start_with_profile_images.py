"""Fresh start with profile images

Revision ID: 9fd210a8abda
Revises: 
Create Date: 2024-12-19 XX:XX:XX.XXXXXX

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '9fd210a8abda'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Drop old tables with CASCADE to handle foreign key constraints
    op.execute('DROP TABLE IF EXISTS review CASCADE')
    op.execute('DROP TABLE IF EXISTS prozprofile CASCADE')
    op.execute('DROP TABLE IF EXISTS specialty CASCADE')
    op.execute('DROP TABLE IF EXISTS proz_specialty CASCADE')
    
    # Create new tables
    
    # Create proz_profiles table
    op.create_table('proz_profiles',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('first_name', sa.String(length=100), nullable=False),
        sa.Column('last_name', sa.String(length=100), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('phone_number', sa.String(length=20), nullable=True),
        sa.Column('profile_image_url', sa.String(length=500), nullable=True),
        sa.Column('bio', sa.Text(), nullable=True),
        sa.Column('location', sa.String(length=255), nullable=True),
        sa.Column('years_experience', sa.Integer(), nullable=True),
        sa.Column('hourly_rate', sa.Float(), nullable=True),
        sa.Column('availability', sa.String(length=50), nullable=True),
        sa.Column('education', sa.Text(), nullable=True),
        sa.Column('certifications', sa.Text(), nullable=True),
        sa.Column('website', sa.String(length=255), nullable=True),
        sa.Column('linkedin', sa.String(length=255), nullable=True),
        sa.Column('preferred_contact_method', sa.String(length=50), nullable=True),
        sa.Column('verification_status', sa.String(length=20), nullable=True),
        sa.Column('is_featured', sa.Boolean(), nullable=True),
        sa.Column('rating', sa.Float(), nullable=True),
        sa.Column('review_count', sa.Integer(), nullable=True),
        sa.Column('email_verified', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_proz_profiles_email'), 'proz_profiles', ['email'], unique=True)
    op.create_index(op.f('ix_proz_profiles_id'), 'proz_profiles', ['id'], unique=False)

    # Create specialties table
    op.create_table('specialties',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_specialties_id'), 'specialties', ['id'], unique=False)

    # Create proz_specialty junction table
    op.create_table('proz_specialty',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('proz_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('specialty_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['proz_id'], ['proz_profiles.id'], ),
        sa.ForeignKeyConstraint(['specialty_id'], ['specialties.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_proz_specialty_id'), 'proz_specialty', ['id'], unique=False)

    # Create reviews table
    op.create_table('reviews',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('proz_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('client_name', sa.String(length=100), nullable=False),
        sa.Column('client_email', sa.String(length=255), nullable=True),
        sa.Column('rating', sa.Integer(), nullable=False),
        sa.Column('review_text', sa.Text(), nullable=True),
        sa.Column('is_approved', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['proz_id'], ['proz_profiles.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_reviews_id'), 'reviews', ['id'], unique=False)


def downgrade():
    # Drop new tables
    op.drop_index(op.f('ix_reviews_id'), table_name='reviews')
    op.drop_table('reviews')
    op.drop_index(op.f('ix_proz_specialty_id'), table_name='proz_specialty')
    op.drop_table('proz_specialty')
    op.drop_index(op.f('ix_specialties_id'), table_name='specialties')
    op.drop_table('specialties')
    op.drop_index(op.f('ix_proz_profiles_id'), table_name='proz_profiles')
    op.drop_index(op.f('ix_proz_profiles_email'), table_name='proz_profiles')
    op.drop_table('proz_profiles')