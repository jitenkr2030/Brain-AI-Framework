"""
Database Configuration for Brain AI LMS
Extends the existing Brain AI framework database configuration
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import psycopg2
from psycopg2.extras import RealDictCursor
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database URL configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://postgres:password@localhost:5432/brain_ai_lms"
)

# Create engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=os.getenv("SQL_DEBUG", "false").lower() == "true"
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class
Base = declarative_base()

def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """Create all database tables"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise

def drop_tables():
    """Drop all database tables (for development/testing)"""
    try:
        Base.metadata.drop_all(bind=engine)
        logger.info("Database tables dropped successfully")
    except Exception as e:
        logger.error(f"Error dropping database tables: {e}")
        raise

# Database utilities
class DatabaseManager:
    """Database management utilities"""
    
    @staticmethod
    def get_connection():
        """Get database connection using psycopg2"""
        try:
            conn = psycopg2.connect(DATABASE_URL)
            return conn
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            raise
    
    @staticmethod
    def execute_query(query: str, params: tuple = None):
        """Execute a query and return results"""
        conn = DatabaseManager.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, params)
                if query.strip().upper().startswith('SELECT'):
                    return cursor.fetchall()
                else:
                    conn.commit()
                    return cursor.rowcount
        except Exception as e:
            conn.rollback()
            logger.error(f"Query execution error: {e}")
            raise
        finally:
            conn.close()
    
    @staticmethod
    def test_connection():
        """Test database connection"""
        try:
            with engine.connect() as conn:
                result = conn.execute("SELECT 1")
                logger.info("Database connection test successful")
                return True
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False
    
    @staticmethod
    def get_table_info(table_name: str):
        """Get table information"""
        query = """
        SELECT column_name, data_type, is_nullable, column_default
        FROM information_schema.columns
        WHERE table_name = %s
        ORDER BY ordinal_position
        """
        return DatabaseManager.execute_query(query, (table_name,))
    
    @staticmethod
    def get_database_stats():
        """Get database statistics"""
        queries = {
            'total_tables': """
                SELECT COUNT(*) as count 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """,
            'total_users': "SELECT COUNT(*) as count FROM users",
            'total_courses': "SELECT COUNT(*) as count FROM courses",
            'total_enrollments': "SELECT COUNT(*) as count FROM course_enrollments"
        }
        
        stats = {}
        for key, query in queries.items():
            try:
                result = DatabaseManager.execute_query(query)
                stats[key] = result[0]['count'] if result else 0
            except Exception as e:
                logger.error(f"Error getting {key}: {e}")
                stats[key] = 0
        
        return stats

# Migration utilities
class MigrationManager:
    """Database migration management"""
    
    @staticmethod
    def create_migration_table():
        """Create migrations tracking table"""
        query = """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            id SERIAL PRIMARY KEY,
            version VARCHAR(255) UNIQUE NOT NULL,
            description TEXT,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            checksum VARCHAR(64)
        )
        """
        DatabaseManager.execute_query(query)
    
    @staticmethod
    def get_applied_migrations():
        """Get list of applied migrations"""
        MigrationManager.create_migration_table()
        query = "SELECT version FROM schema_migrations ORDER BY applied_at"
        result = DatabaseManager.execute_query(query)
        return [row['version'] for row in result]
    
    @staticmethod
    def mark_migration_applied(version: str, description: str = "", checksum: str = ""):
        """Mark a migration as applied"""
        MigrationManager.create_migration_table()
        query = """
        INSERT INTO schema_migrations (version, description, checksum)
        VALUES (%s, %s, %s)
        ON CONFLICT (version) DO NOTHING
        """
        DatabaseManager.execute_query(query, (version, description, checksum))

# Seed data utilities
class SeedData:
    """Database seed data management"""
    
    @staticmethod
    def create_admin_user():
        """Create default admin user"""
        from app.models.user import User, UserRole
        from app.utils.password import get_password_hash
        
        # Check if admin already exists
        existing_admin = DatabaseManager.execute_query(
            "SELECT id FROM users WHERE role = %s LIMIT 1",
            ('admin',)
        )
        
        if not existing_admin:
            admin_data = {
                'email': 'admin@brainai.com',
                'username': 'admin',
                'full_name': 'Brain AI Administrator',
                'hashed_password': get_password_hash('admin123'),
                'role': 'admin',
                'is_active': True,
                'is_verified': True
            }
            
            query = """
            INSERT INTO users (email, username, full_name, hashed_password, role, is_active, is_verified)
            VALUES (%(email)s, %(username)s, %(full_name)s, %(hashed_password)s, %(role)s, %(is_active)s, %(is_verified)s)
            """
            DatabaseManager.execute_query(query, admin_data)
            logger.info("Admin user created successfully")
    
    @staticmethod
    def create_sample_courses():
        """Create sample courses for testing"""
        courses = [
            {
                'title': 'Brain AI Fundamentals',
                'slug': 'brain-ai-fundamentals',
                'description': 'Introduction to brain-inspired artificial intelligence and memory systems.',
                'short_description': 'Learn the basics of brain-inspired AI',
                'level': 'foundation',
                'category': 'brain_ai_fundamentals',
                'duration_hours': 40,
                'difficulty_rating': 1.0,
                'price_usd': 2500.0,
                'learning_outcomes': [
                    'Understand brain-inspired AI concepts',
                    'Build simple memory systems',
                    'Implement basic learning algorithms'
                ],
                'prerequisites': [],
                'syllabus': {
                    'modules': [
                        {'title': 'Introduction to Brain AI', 'lessons': 5},
                        {'title': 'Memory Systems', 'lessons': 8},
                        {'title': 'Learning Algorithms', 'lessons': 7}
                    ]
                },
                'has_interactive_labs': True,
                'has_certification': True,
                'has_live_sessions': False,
                'has_community_access': True,
                'is_published': True,
                'is_featured': True
            },
            {
                'title': 'Advanced Memory Architectures',
                'slug': 'advanced-memory-architectures',
                'description': 'Deep dive into advanced memory systems and associative networks.',
                'short_description': 'Master advanced memory architectures',
                'level': 'advanced',
                'category': 'memory_systems',
                'duration_hours': 60,
                'difficulty_rating': 4.0,
                'price_usd': 3500.0,
                'learning_outcomes': [
                    'Design complex memory systems',
                    'Implement associative networks',
                    'Optimize memory performance'
                ],
                'prerequisites': ['brain-ai-fundamentals'],
                'syllabus': {
                    'modules': [
                        {'title': 'Vector Memory Systems', 'lessons': 10},
                        {'title': 'Associative Networks', 'lessons': 12},
                        {'title': 'Memory Optimization', 'lessons': 8}
                    ]
                },
                'has_interactive_labs': True,
                'has_certification': True,
                'has_live_sessions': True,
                'has_community_access': True,
                'is_published': True,
                'is_featured': True
            }
        ]
        
        for course_data in courses:
            # Check if course already exists
            existing = DatabaseManager.execute_query(
                "SELECT id FROM courses WHERE slug = %s",
                (course_data['slug'],)
            )
            
            if not existing:
                query = """
                INSERT INTO courses (
                    title, slug, description, short_description, level, category,
                    duration_hours, difficulty_rating, price_usd, learning_outcomes,
                    prerequisites, syllabus, has_interactive_labs, has_certification,
                    has_live_sessions, has_community_access, is_published, is_featured
                ) VALUES (
                    %(title)s, %(slug)s, %(description)s, %(short_description)s,
                    %(level)s, %(category)s, %(duration_hours)s, %(difficulty_rating)s,
                    %(price_usd)s, %(learning_outcomes)s, %(prerequisites)s,
                    %(syllabus)s, %(has_interactive_labs)s, %(has_certification)s,
                    %(has_live_sessions)s, %(has_community_access)s, %(is_published)s,
                    %(is_featured)s
                )
                """
                DatabaseManager.execute_query(query, course_data)
                logger.info(f"Created sample course: {course_data['title']}")

# Initialize database
def init_db():
    """Initialize database with tables and seed data"""
    try:
        # Test connection
        if DatabaseManager.test_connection():
            logger.info("Database connection successful")
            
            # Create tables
            create_tables()
            
            # Seed data
            SeedData.create_admin_user()
            SeedData.create_sample_courses()
            
            logger.info("Database initialization completed")
        else:
            raise Exception("Database connection failed")
            
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise

if __name__ == "__main__":
    init_db()