"""
Alembic migration environment configuration
Brain AI LMS - Database Migration System
"""

import os
import sys
from logging.config import fileConfig

from sqlalchemy import pool, create_engine
from sqlalchemy.engine import Connection

from alembic import context

# Add the backend directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Import models and database configuration
from app.database import DATABASE_URL
from app.models.base import Base
from app.models.lms_models import (
    User, UserRole, Course, CourseLevel, CourseCategory,
    Lesson, LessonType, Module, Enrollment, Progress,
    Payment, PaymentStatus, Subscription, SubscriptionStatus,
    Certificate, UserCertification
)


# this is the Alembic Config object, which holds
# all alembic configuration settings
config = context.config

# Overwrite the sqlalchemy.url from environment
config.set_main_option('sqlalchemy.url', DATABASE_URL)

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here too.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    connectable = create_engine(
        DATABASE_URL,
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
