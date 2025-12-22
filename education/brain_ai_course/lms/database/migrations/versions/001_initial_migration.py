"""Initial migration - Create all LMS tables

Revision ID: 001_initial
Revises: 
Create Date: 2024-12-21 00:00:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create enum types
    op.execute("""
        CREATE TYPE user_role AS ENUM ('student', 'instructor', 'admin', 'enterprise_admin')
    """)
    op.execute("""
        CREATE TYPE course_level AS ENUM ('foundation', 'intermediate', 'advanced', 'expert')
    """)
    op.execute("""
        CREATE TYPE course_category AS ENUM (
            'brain_ai_fundamentals', 'memory_systems', 'learning_engines',
            'industry_applications', 'enterprise_deployment', 'research_advanced'
        )
    """)
    op.execute("""
        CREATE TYPE lesson_type AS ENUM ('video', 'interactive_lab', 'quiz', 'assignment', 'reading')
    """)
    op.execute("""
        CREATE TYPE payment_status AS ENUM ('pending', 'processing', 'succeeded', 'failed', 'refunded', 'cancelled')
    """)
    op.execute("""
        CREATE TYPE subscription_status AS ENUM ('active', 'inactive', 'cancelled', 'expired', 'past_due')
    """)
    op.execute("""
        CREATE TYPE enrollment_status AS ENUM ('active', 'completed', 'paused', 'cancelled')
    """)

    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('username', sa.String(100), nullable=False, unique=True),
        sa.Column('full_name', sa.String(200), nullable=True),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('avatar_url', sa.String(500), nullable=True),
        sa.Column('role', sa.Enum('student', 'instructor', 'admin', 'enterprise_admin', name='user_role'), nullable=False, default='student'),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('is_verified', sa.Boolean(), nullable=False, default=False),
        sa.Column('stripe_customer_id', sa.String(100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)

    # Create courses table
    op.create_table(
        'courses',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('slug', sa.String(255), nullable=False, unique=True),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('short_description', sa.String(500), nullable=True),
        sa.Column('thumbnail_url', sa.String(500), nullable=True),
        sa.Column('level', sa.Enum('foundation', 'intermediate', 'advanced', 'expert', name='course_level'), nullable=False),
        sa.Column('category', sa.Enum('brain_ai_fundamentals', 'memory_systems', 'learning_engines', 'industry_applications', 'enterprise_deployment', 'research_advanced', name='course_category'), nullable=False),
        sa.Column('duration_hours', sa.Integer(), nullable=False),
        sa.Column('difficulty_rating', sa.Float(), nullable=False, default=1.0),
        sa.Column('price_usd', sa.Float(), nullable=False, default=0.0),
        sa.Column('learning_outcomes', postgresql.JSON(), nullable=True),
        sa.Column('prerequisites', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('syllabus', postgresql.JSON(), nullable=True),
        sa.Column('has_interactive_labs', sa.Boolean(), nullable=False, default=False),
        sa.Column('has_certification', sa.Boolean(), nullable=False, default=False),
        sa.Column('has_live_sessions', sa.Boolean(), nullable=False, default=False),
        sa.Column('has_community_access', sa.Boolean(), nullable=False, default=True),
        sa.Column('is_published', sa.Boolean(), nullable=False, default=False),
        sa.Column('is_featured', sa.Boolean(), nullable=False, default=False),
        sa.Column('instructor_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.ForeignKeyConstraint(['instructor_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_courses_slug'), 'courses', ['slug'], unique=True)
    op.create_index(op.f('ix_courses_level'), 'courses', ['level'], unique=False)
    op.create_index(op.f('ix_courses_category'), 'courses', ['category'], unique=False)

    # Create modules table
    op.create_table(
        'modules',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('course_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('order_index', sa.Integer(), nullable=False, default=0),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_modules_course_id'), 'modules', ['course_id'], unique=False)

    # Create lessons table
    op.create_table(
        'lessons',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('module_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('type', sa.Enum('video', 'interactive_lab', 'quiz', 'assignment', 'reading', name='lesson_type'), nullable=False),
        sa.Column('content', postgresql.JSON(), nullable=True),
        sa.Column('video_url', sa.String(500), nullable=True),
        sa.Column('duration_minutes', sa.Integer(), nullable=True),
        sa.Column('order_index', sa.Integer(), nullable=False, default=0),
        sa.Column('is_free_preview', sa.Boolean(), nullable=False, default=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.ForeignKeyConstraint(['module_id'], ['modules.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_lessons_module_id'), 'lessons', ['module_id'], unique=False)

    # Create course_instructors association table
    op.create_table(
        'course_instructors',
        sa.Column('course_id', sa.Integer(), nullable=False),
        sa.Column('instructor_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['instructor_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('course_id', 'instructor_id')
    )

    # Create enrollments table
    op.create_table(
        'enrollments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('course_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.Enum('active', 'completed', 'paused', 'cancelled', name='enrollment_status'), nullable=False, default='active'),
        sa.Column('enrolled_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('progress_percentage', sa.Float(), nullable=False, default=0.0),
        sa.Column('stripe_payment_id', sa.String(100), nullable=True),
        sa.Column('amount_paid', sa.Float(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'course_id', name='uq_user_course_enrollment')
    )
    op.create_index(op.f('ix_enrollments_user_id'), 'enrollments', ['user_id'], unique=False)
    op.create_index(op.f('ix_enrollments_course_id'), 'enrollments', ['course_id'], unique=False)

    # Create progress table
    op.create_table(
        'progress',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('enrollment_id', sa.Integer(), nullable=False),
        sa.Column('lesson_id', sa.Integer(), nullable=False),
        sa.Column('is_completed', sa.Boolean(), nullable=False, default=False),
        sa.Column('watch_time_seconds', sa.Integer(), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.ForeignKeyConstraint(['enrollment_id'], ['enrollments.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['lesson_id'], ['lessons.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('enrollment_id', 'lesson_id', name='uq_enrollment_lesson_progress')
    )
    op.create_index(op.f('ix_progress_enrollment_id'), 'progress', ['enrollment_id'], unique=False)

    # Create payments table
    op.create_table(
        'payments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('course_id', sa.Integer(), nullable=True),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('currency', sa.String(10), nullable=False, default='usd'),
        sa.Column('status', sa.Enum('pending', 'processing', 'succeeded', 'failed', 'refunded', 'cancelled', name='payment_status'), nullable=False, default='pending'),
        sa.Column('stripe_payment_intent_id', sa.String(100), nullable=True),
        sa.Column('stripe_session_id', sa.String(100), nullable=True),
        sa.Column('metadata', postgresql.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_payments_user_id'), 'payments', ['user_id'], unique=False)
    op.create_index(op.f('ix_payments_stripe_payment_intent_id'), 'payments', ['stripe_payment_intent_id'], unique=True)

    # Create subscriptions table
    op.create_table(
        'subscriptions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('plan_type', sa.String(50), nullable=False),
        sa.Column('status', sa.Enum('active', 'inactive', 'cancelled', 'expired', 'past_due', name='subscription_status'), nullable=False, default='active'),
        sa.Column('stripe_subscription_id', sa.String(100), nullable=True),
        sa.Column('stripe_price_id', sa.String(100), nullable=True),
        sa.Column('current_period_start', sa.DateTime(timezone=True), nullable=True),
        sa.Column('current_period_end', sa.DateTime(timezone=True), nullable=True),
        sa.Column('cancel_at_period_end', sa.Boolean(), nullable=False, default=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_subscriptions_user_id'), 'subscriptions', ['user_id'], unique=False)

    # Create certificates table
    op.create_table(
        'certificates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('course_id', sa.Integer(), nullable=False),
        sa.Column('certificate_number', sa.String(100), nullable=False, unique=True),
        sa.Column('issued_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('pdf_url', sa.String(500), nullable=True),
        sa.Column('verification_url', sa.String(500), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_certificates_user_id'), 'certificates', ['user_id'], unique=False)
    op.create_index(op.f('ix_certificates_certificate_number'), 'certificates', ['certificate_number'], unique=True)


def downgrade() -> None:
    # Drop tables in reverse order due to foreign key constraints
    op.drop_table('certificates')
    op.drop_table('subscriptions')
    op.drop_table('payments')
    op.drop_table('progress')
    op.drop_table('enrollments')
    op.drop_table('course_instructors')
    op.drop_table('lessons')
    op.drop_table('modules')
    op.drop_table('courses')
    op.drop_table('users')

    # Drop enum types
    op.execute("DROP TYPE enrollment_status CASCADE")
    op.execute("DROP TYPE subscription_status CASCADE")
    op.execute("DROP TYPE payment_status CASCADE")
    op.execute("DROP TYPE lesson_type CASCADE")
    op.execute("DROP TYPE course_category CASCADE")
    op.execute("DROP TYPE course_level CASCADE")
    op.execute("DROP TYPE user_role CASCADE")
