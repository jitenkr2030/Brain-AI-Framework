"""
Brain AI SaaS Database Management
Async database connection with connection pooling and health checks
"""

import asyncpg
import asyncio
from typing import Optional, List, Dict, Any
from contextlib import asynccontextmanager
import logging
from datetime import datetime

from app.config import get_database_url, settings
from app.models import (
    Tenant, User, Project, Memory, LearningEvent, 
    APIUsage, Subscription
)

logger = logging.getLogger(__name__)


class Database:
    """Database connection manager with connection pooling"""
    
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None
        self._initialized = False
    
    async def connect(self):
        """Create connection pool"""
        if self.pool:
            return
            
        try:
            self.pool = await asyncpg.create_pool(
                host=settings.DB_HOST,
                port=settings.DB_PORT,
                user=settings.DB_USER,
                password=settings.DB_PASSWORD,
                database=settings.DB_NAME,
                min_size=settings.DB_POOL_MIN_SIZE,
                max_size=settings.DB_POOL_MAX_SIZE,
                command_timeout=60,
                server_settings={
                    'application_name': 'brain-ai-saas',
                    'jit': 'off',  # Disable JIT for stability
                }
            )
            self._initialized = True
            logger.info("✅ Database connection pool created")
        except Exception as e:
            logger.error(f"❌ Failed to create database pool: {e}")
            raise
    
    async def disconnect(self):
        """Close connection pool"""
        if self.pool:
            await self.pool.close()
            self.pool = None
            self._initialized = False
            logger.info("🛑 Database connection pool closed")
    
    @asynccontextmanager
    async def get_connection(self):
        """Get database connection from pool"""
        if not self.pool:
            await self.connect()
        async with self.pool.acquire() as connection:
            try:
                yield connection
            except Exception as e:
                logger.error(f"Database connection error: {e}")
                raise
    
    async def health_check(self) -> bool:
        """Check database health"""
        try:
            async with self.get_connection() as conn:
                await conn.fetchval("SELECT 1")
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False
    
    async def execute(self, query: str, *args):
        """Execute a query and return the result"""
        async with self.get_connection() as conn:
            return await conn.execute(query, *args)
    
    async def fetch(self, query: str, *args):
        """Fetch all rows from a query"""
        async with self.get_connection() as conn:
            return await conn.fetch(query, *args)
    
    async def fetchrow(self, query: str, *args):
        """Fetch single row from a query"""
        async with self.get_connection() as conn:
            return await conn.fetchrow(query, *args)
    
    async def fetchval(self, query: str, *args):
        """Fetch single value from a query"""
        async with self.get_connection() as conn:
            return await conn.fetchval(query, *args)
    
    async def transaction(self):
        """Get a database transaction"""
        return self.get_connection()


# Global database instance
db = Database()


async def create_tables():
    """Create all database tables"""
    logger.info("🏗️ Creating database tables...")
    
    # Schema creation SQL
    create_schema_sql = """
    -- Enable required extensions
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
    CREATE EXTENSION IF NOT EXISTS "pg_trgm";
    
    -- Create tenants schema for multi-tenancy
    CREATE SCHEMA IF NOT EXISTS tenants;
    
    -- Tenants table
    CREATE TABLE IF NOT EXISTS tenants (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        name VARCHAR(255) NOT NULL,
        slug VARCHAR(100) UNIQUE NOT NULL,
        plan VARCHAR(50) NOT NULL CHECK (plan IN ('free', 'starter', 'professional', 'enterprise')),
        api_key VARCHAR(255) UNIQUE NOT NULL,
        status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'suspended', 'cancelled')),
        settings JSONB DEFAULT '{}',
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );
    
    -- Users table
    CREATE TABLE IF NOT EXISTS users (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
        email VARCHAR(255) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        role VARCHAR(50) DEFAULT 'user' CHECK (role IN ('admin', 'user', 'viewer')),
        first_name VARCHAR(100),
        last_name VARCHAR(100),
        is_active BOOLEAN DEFAULT TRUE,
        last_login TIMESTAMP WITH TIME ZONE,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );
    
    -- Projects table
    CREATE TABLE IF NOT EXISTS projects (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
        name VARCHAR(255) NOT NULL,
        description TEXT,
        settings JSONB DEFAULT '{}',
        memory_count INTEGER DEFAULT 0,
        api_call_count INTEGER DEFAULT 0,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );
    
    -- Memory items (Brain AI memories)
    CREATE TABLE IF NOT EXISTS memories (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
        project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
        pattern_signature VARCHAR(255) NOT NULL,
        memory_type VARCHAR(50) NOT NULL CHECK (memory_type IN ('episodic', 'semantic', 'procedural', 'working', 'associative')),
        content JSONB NOT NULL,
        context JSONB DEFAULT '{}',
        strength FLOAT DEFAULT 0.5 CHECK (strength >= 0.0 AND strength <= 1.0),
        access_count INTEGER DEFAULT 0,
        last_accessed TIMESTAMP WITH TIME ZONE,
        tags TEXT[] DEFAULT '{}',
        confidence FLOAT DEFAULT 0.5 CHECK (confidence >= 0.0 AND confidence <= 1.0),
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );
    
    -- Learning events
    CREATE TABLE IF NOT EXISTS learning_events (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
        memory_id UUID REFERENCES memories(id) ON DELETE CASCADE,
        event_type VARCHAR(100) NOT NULL,
        feedback_type VARCHAR(50),
        outcome JSONB,
        confidence FLOAT,
        metadata JSONB DEFAULT '{}',
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );
    
    -- API usage tracking
    CREATE TABLE IF NOT EXISTS api_usage (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
        endpoint VARCHAR(255) NOT NULL,
        method VARCHAR(10) NOT NULL,
        status_code INTEGER NOT NULL,
        response_time_ms INTEGER,
        request_size_bytes INTEGER,
        response_size_bytes INTEGER,
        user_agent TEXT,
        ip_address INET,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );
    
    -- Subscriptions table
    CREATE TABLE IF NOT EXISTS subscriptions (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
        stripe_subscription_id VARCHAR(255) UNIQUE,
        plan VARCHAR(50) NOT NULL,
        status VARCHAR(50) NOT NULL,
        current_period_start TIMESTAMP WITH TIME ZONE,
        current_period_end TIMESTAMP WITH TIME ZONE,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );
    """
    
    # Indexes creation SQL
    create_indexes_sql = """
    -- Performance indexes
    CREATE INDEX IF NOT EXISTS idx_tenants_slug ON tenants(slug);
    CREATE INDEX IF NOT EXISTS idx_tenants_api_key ON tenants(api_key);
    CREATE INDEX IF NOT EXISTS idx_users_tenant_id ON users(tenant_id);
    CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
    CREATE INDEX IF NOT EXISTS idx_memories_tenant_project ON memories(tenant_id, project_id);
    CREATE INDEX IF NOT EXISTS idx_memories_pattern ON memories(pattern_signature);
    CREATE INDEX IF NOT EXISTS idx_memories_type ON memories(memory_type);
    CREATE INDEX IF NOT EXISTS idx_memories_tags ON memories USING GIN(tags);
    CREATE INDEX IF NOT EXISTS idx_learning_events_tenant ON learning_events(tenant_id);
    CREATE INDEX IF NOT EXISTS idx_api_usage_tenant ON api_usage(tenant_id);
    CREATE INDEX IF NOT EXISTS idx_api_usage_created ON api_usage(created_at);
    """
    
    # Triggers creation SQL
    create_triggers_sql = """
    -- Updated at trigger function
    CREATE OR REPLACE FUNCTION update_updated_at_column()
    RETURNS TRIGGER AS $$
    BEGIN
        NEW.updated_at = NOW();
        RETURN NEW;
    END;
    $$ language 'plpgsql';
    
    -- Create triggers for updated_at
    DROP TRIGGER IF EXISTS update_tenants_updated_at ON tenants;
    CREATE TRIGGER update_tenants_updated_at 
        BEFORE UPDATE ON tenants 
        FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    
    DROP TRIGGER IF EXISTS update_users_updated_at ON users;
    CREATE TRIGGER update_users_updated_at 
        BEFORE UPDATE ON users 
        FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    
    DROP TRIGGER IF EXISTS update_projects_updated_at ON projects;
    CREATE TRIGGER update_projects_updated_at 
        BEFORE UPDATE ON projects 
        FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    
    DROP TRIGGER IF EXISTS update_memories_updated_at ON memories;
    CREATE TRIGGER update_memories_updated_at 
        BEFORE UPDATE ON memories 
        FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    
    DROP TRIGGER IF EXISTS update_subscriptions_updated_at ON subscriptions;
    CREATE TRIGGER update_subscriptions_updated_at 
        BEFORE UPDATE ON subscriptions 
        FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    """
    
    try:
        async with db.get_connection() as conn:
            # Create schema
            await conn.execute(create_schema_sql)
            logger.info("✅ Database schema created")
            
            # Create indexes
            await conn.execute(create_indexes_sql)
            logger.info("✅ Database indexes created")
            
            # Create triggers
            await conn.execute(create_triggers_sql)
            logger.info("✅ Database triggers created")
            
        logger.info("🎉 Database setup completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Database setup failed: {e}")
        raise


def get_database() -> Database:
    """Get database instance"""
    return db


# Connection cleanup on application shutdown
async def cleanup_database():
    """Cleanup database connections"""
    await db.disconnect()
