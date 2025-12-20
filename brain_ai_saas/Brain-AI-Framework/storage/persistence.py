"""
Database Abstraction Layer
Provides unified interface for persistent storage across different backends.
"""

from typing import Dict, Any, List, Optional, Callable, Awaitable
from abc import ABC, abstractmethod
from datetime import datetime
from contextlib import asynccontextmanager
import sqlite3
import json
import asyncio
from pathlib import Path
from loguru import logger

from app.config import get_settings


class DatabaseBackend(ABC):
    """Abstract database backend interface"""
    
    @abstractmethod
    async def connect(self):
        """Connect to the database"""
        pass
    
    @abstractmethod
    async def disconnect(self):
        """Disconnect from the database"""
        pass
    
    @abstractmethod
    async def execute(self, query: str, params: Optional[tuple] = None) -> Any:
        """Execute a query"""
        pass
    
    @abstractmethod
    async def execute_many(self, query: str, params_list: List[tuple]) -> Any:
        """Execute a query with multiple parameter sets"""
        pass
    
    @abstractmethod
    async def fetch_one(self, query: str, params: Optional[tuple] = None) -> Optional[Any]:
        """Fetch a single row"""
        pass
    
    @abstractmethod
    async def fetch_all(self, query: str, params: Optional[tuple] = None) -> List[Any]:
        """Fetch all rows"""
        pass


class SQLiteBackend(DatabaseBackend):
    """SQLite database backend"""
    
    def __init__(self, db_path: str):
        self.db_path = Path(db_path)
        self.connection_pool = []
        self.max_connections = 10
        
    async def connect(self):
        """Connect to SQLite database"""
        try:
            # Ensure directory exists
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Create initial connection to test
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            self.connection_pool.append(conn)
            
            logger.info(f"Connected to SQLite database: {self.db_path}")
            
        except Exception as e:
            logger.error(f"Failed to connect to SQLite: {e}")
            raise
    
    async def disconnect(self):
        """Disconnect from SQLite database"""
        try:
            for conn in self.connection_pool:
                conn.close()
            self.connection_pool.clear()
            logger.info("Disconnected from SQLite database")
            
        except Exception as e:
            logger.error(f"Error disconnecting from SQLite: {e}")
    
    async def _get_connection(self) -> sqlite3.Connection:
        """Get a connection from the pool"""
        if self.connection_pool:
            return self.connection_pool[0]
        else:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            self.connection_pool.append(conn)
            return conn
    
    async def execute(self, query: str, params: Optional[tuple] = None) -> Any:
        """Execute a query"""
        conn = await self._get_connection()
        try:
            cursor = conn.execute(query, params or ())
            conn.commit()
            return cursor
        except Exception as e:
            conn.rollback()
            logger.error(f"SQLite execute error: {e}")
            raise
    
    async def execute_many(self, query: str, params_list: List[tuple]) -> Any:
        """Execute a query with multiple parameter sets"""
        conn = await self._get_connection()
        try:
            cursor = conn.executemany(query, params_list)
            conn.commit()
            return cursor
        except Exception as e:
            conn.rollback()
            logger.error(f"SQLite execute_many error: {e}")
            raise
    
    async def fetch_one(self, query: str, params: Optional[tuple] = None) -> Optional[Any]:
        """Fetch a single row"""
        conn = await self._get_connection()
        try:
            cursor = conn.execute(query, params or ())
            row = cursor.fetchone()
            return dict(row) if row else None
        except Exception as e:
            logger.error(f"SQLite fetch_one error: {e}")
            raise
    
    async def fetch_all(self, query: str, params: Optional[tuple] = None) -> List[Any]:
        """Fetch all rows"""
        conn = await self._get_connection()
        try:
            cursor = conn.execute(query, params or ())
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"SQLite fetch_all error: {e}")
            raise


class PersistenceManager:
    """
    Database Abstraction Layer
    
    Provides unified interface for persistent storage:
    - Multiple backend support (SQLite, PostgreSQL, etc.)
    - Connection pooling
    - Transaction management
    - Migration support
    - Query caching
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.backend: Optional[DatabaseBackend] = None
        self.connected = False
        
        # Query cache
        self._query_cache: Dict[str, Dict[str, Any]] = {}
        self._cache_ttl = 300  # 5 minutes
        
        # Transaction management
        self._transaction_level = 0
        self._pending_queries: List[Callable] = []
        
        # Statistics
        self.stats = {
            "total_queries": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "transaction_count": 0,
            "error_count": 0
        }
    
    async def initialize(self):
        """Initialize the persistence manager"""
        logger.info("💾 Initializing persistence manager...")
        
        try:
            # Determine backend based on settings
            if self.settings.DATABASE_URL.startswith("sqlite"):
                self.backend = SQLiteBackend(self.settings.DATABASE_URL.replace("sqlite:///", ""))
            else:
                # TODO: Add PostgreSQL, MySQL backends
                logger.warning(f"Database backend not supported: {self.settings.DATABASE_URL}")
                # Fallback to SQLite
                self.backend = SQLiteBackend("brain_ai.db")
            
            # Connect to database
            await self.backend.connect()
            self.connected = True
            
            # Run migrations
            await self._run_migrations()
            
            logger.info("✅ Persistence manager initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize persistence manager: {e}")
            raise
    
    async def cleanup(self):
        """Cleanup resources"""
        try:
            if self.backend and self.connected:
                await self.backend.disconnect()
                self.connected = False
            logger.info("🧹 Persistence manager cleanup complete")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    async def execute_sql(self, sql_func: Callable[[sqlite3.Connection], Any]) -> Any:
        """
        Execute SQL function in a database transaction
        
        Args:
            sql_func: Function that takes a connection and returns a result
            
        Returns:
            Result from sql_func
        """
        if not self.connected:
            raise RuntimeError("Database not connected")
        
        self.stats["total_queries"] += 1
        
        try:
            # For SQLite backend
            if isinstance(self.backend, SQLiteBackend):
                conn = await self.backend._get_connection()
                return sql_func(conn)
            else:
                # For other backends, implement as needed
                raise NotImplementedError("Only SQLite backend implemented")
                
        except Exception as e:
            self.stats["error_count"] += 1
            logger.error(f"Database operation failed: {e}")
            raise
    
    # Memory storage methods
    
    async def store_memory(self, memory_data: Dict[str, Any]) -> bool:
        """Store a memory item"""
        try:
            # Ensure memory has required fields
            if "id" not in memory_data:
                memory_data["id"] = f"memory_{datetime.now().timestamp()}"
            
            async def store(conn):
                conn.execute("""
                    INSERT OR REPLACE INTO memories 
                    (id, pattern_signature, memory_type, content, context, 
                     strength, access_count, last_accessed, created_at, 
                     associations, tags, confidence, decay_rate, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    memory_data["id"],
                    memory_data.get("pattern_signature", ""),
                    memory_data.get("memory_type", "episodic"),
                    json.dumps(memory_data.get("content", {})),
                    json.dumps(memory_data.get("context", {})),
                    memory_data.get("strength", 0.5),
                    memory_data.get("access_count", 0),
                    memory_data.get("last_accessed", datetime.now().isoformat()),
                    memory_data.get("created_at", datetime.now().isoformat()),
                    json.dumps(memory_data.get("associations", [])),
                    json.dumps(memory_data.get("tags", [])),
                    memory_data.get("confidence", 0.5),
                    memory_data.get("decay_rate", 0.001),
                    datetime.now().isoformat()
                ))
            
            await self.execute_sql(store)
            return True
            
        except Exception as e:
            logger.error(f"Error storing memory: {e}")
            return False
    
    async def load_all_memories(self) -> List[Dict[str, Any]]:
        """Load all memories from storage"""
        try:
            async def load(conn):
                cursor = conn.execute("SELECT * FROM memories ORDER BY created_at DESC")
                rows = cursor.fetchall()
                
                memories = []
                for row in rows:
                    memory = {
                        "id": row[0],
                        "pattern_signature": row[1],
                        "memory_type": row[2],
                        "content": json.loads(row[3] or "{}"),
                        "context": json.loads(row[4] or "{}"),
                        "strength": row[5],
                        "access_count": row[6],
                        "last_accessed": row[7],
                        "created_at": row[8],
                        "associations": json.loads(row[9] or "[]"),
                        "tags": json.loads(row[10] or "[]"),
                        "confidence": row[11],
                        "decay_rate": row[12],
                        "updated_at": row[13]
                    }
                    memories.append(memory)
                
                return memories
            
            return await self.execute_sql(load)
            
        except Exception as e:
            logger.error(f"Error loading memories: {e}")
            return []
    
    async def delete_memory(self, memory_id: str) -> bool:
        """Delete a memory"""
        try:
            async def delete(conn):
                conn.execute("DELETE FROM memories WHERE id = ?", (memory_id,))
            
            await self.execute_sql(delete)
            return True
            
        except Exception as e:
            logger.error(f"Error deleting memory {memory_id}: {e}")
            return False
    
    # System state methods
    
    async def store_system_state(self, state_data: Dict[str, Any]) -> bool:
        """Store system state information"""
        try:
            async def store(conn):
                conn.execute("""
                    INSERT OR REPLACE INTO system_state (key, value, updated_at)
                    VALUES (?, ?, ?)
                """, (
                    state_data["key"],
                    json.dumps(state_data["value"]),
                    datetime.now().isoformat()
                ))
            
            await self.execute_sql(store)
            return True
            
        except Exception as e:
            logger.error(f"Error storing system state: {e}")
            return False
    
    async def load_system_state(self, key: str) -> Optional[Any]:
        """Load system state"""
        try:
            async def load(conn):
                cursor = conn.execute(
                    "SELECT value FROM system_state WHERE key = ?",
                    (key,)
                )
                row = cursor.fetchone()
                
                if row:
                    return json.loads(row[0])
                return None
            
            return await self.execute_sql(load)
            
        except Exception as e:
            logger.error(f"Error loading system state {key}: {e}")
            return None
    
    async def get_all_system_state(self) -> Dict[str, Any]:
        """Get all system state"""
        try:
            async def load_all(conn):
                cursor = conn.execute("SELECT key, value FROM system_state")
                rows = cursor.fetchall()
                
                state = {}
                for row in rows:
                    state[row[0]] = json.loads(row[1])
                
                return state
            
            return await self.execute_sql(load_all)
            
        except Exception as e:
            logger.error(f"Error loading all system state: {e}")
            return {}
    
    # Event log methods
    
    async def log_event(self, event_data: Dict[str, Any]) -> bool:
        """Log an event"""
        try:
            async def log(conn):
                conn.execute("""
                    INSERT INTO event_log 
                    (event_type, event_data, timestamp, source)
                    VALUES (?, ?, ?, ?)
                """, (
                    event_data.get("type", "unknown"),
                    json.dumps(event_data),
                    datetime.now().isoformat(),
                    event_data.get("source", "system")
                ))
            
            await self.execute_sql(log)
            return True
            
        except Exception as e:
            logger.error(f"Error logging event: {e}")
            return False
    
    async def get_events(
        self, 
        event_type: Optional[str] = None, 
        limit: int = 100,
        since: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Get events from log"""
        try:
            query = "SELECT * FROM event_log"
            params = []
            
            if event_type or since:
                query += " WHERE "
                conditions = []
                
                if event_type:
                    conditions.append("event_type = ?")
                    params.append(event_type)
                
                if since:
                    conditions.append("timestamp > ?")
                    params.append(since.isoformat())
                
                query += " AND ".join(conditions)
            
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            async def get_events(conn):
                cursor = conn.execute(query, params)
                rows = cursor.fetchall()
                
                events = []
                for row in rows:
                    events.append({
                        "id": row[0],
                        "event_type": row[1],
                        "event_data": json.loads(row[2]),
                        "timestamp": row[3],
                        "source": row[4]
                    })
                
                return events
            
            return await self.execute_sql(get_events)
            
        except Exception as e:
            logger.error(f"Error getting events: {e}")
            return []
    
    # Migration methods
    
    async def _run_migrations(self):
        """Run database migrations"""
        try:
            await self._create_tables()
            logger.info("✅ Database migrations completed")
        except Exception as e:
            logger.error(f"Error running migrations: {e}")
            raise
    
    async def _create_tables(self):
        """Create database tables"""
        
        async def create_tables(conn):
            # Memories table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id TEXT PRIMARY KEY,
                    pattern_signature TEXT NOT NULL,
                    memory_type TEXT NOT NULL DEFAULT 'episodic',
                    content TEXT NOT NULL DEFAULT '{}',
                    context TEXT NOT NULL DEFAULT '{}',
                    strength REAL NOT NULL DEFAULT 0.5,
                    access_count INTEGER NOT NULL DEFAULT 0,
                    last_accessed TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    associations TEXT NOT NULL DEFAULT '[]',
                    tags TEXT NOT NULL DEFAULT '[]',
                    confidence REAL NOT NULL DEFAULT 0.5,
                    decay_rate REAL NOT NULL DEFAULT 0.001,
                    updated_at TEXT NOT NULL
                )
            """)
            
            # System state table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS system_state (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            
            # Event log table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS event_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_type TEXT NOT NULL,
                    event_data TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    source TEXT NOT NULL DEFAULT 'system'
                )
            """)
            
            # Vector embeddings table (for semantic search)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS embeddings (
                    id TEXT PRIMARY KEY,
                    content_hash TEXT NOT NULL,
                    embedding TEXT NOT NULL,
                    metadata TEXT NOT NULL DEFAULT '{}',
                    created_at TEXT NOT NULL
                )
            """)
            
            # Create indices for better performance
            conn.execute("CREATE INDEX IF NOT EXISTS idx_memories_pattern ON memories(pattern_signature)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_memories_strength ON memories(strength)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_memories_created ON memories(created_at)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_events_timestamp ON event_log(timestamp)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_embeddings_content ON embeddings(content_hash)")
        
        await self.execute_sql(create_tables)
    
    # Utility methods
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on database"""
        try:
            async def check(conn):
                # Test basic connectivity
                cursor = conn.execute("SELECT 1")
                cursor.fetchone()
                
                # Check table existence
                cursor = conn.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name IN ('memories', 'system_state', 'event_log')
                """)
                tables = [row[0] for row in cursor.fetchall()]
                
                # Count records
                memory_count = conn.execute("SELECT COUNT(*) FROM memories").fetchone()[0]
                event_count = conn.execute("SELECT COUNT(*) FROM event_log").fetchone()[0]
                
                return {
                    "status": "healthy",
                    "tables": tables,
                    "memory_count": memory_count,
                    "event_count": event_count,
                    "backend": "sqlite"
                }
            
            return await self.execute_sql(check)
            
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "backend": "sqlite"
            }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get persistence manager statistics"""
        cache_hit_rate = (
            self.stats["cache_hits"] / max(1, self.stats["cache_hits"] + self.stats["cache_misses"])
        ) * 100
        
        return {
            **self.stats,
            "connected": self.connected,
            "backend_type": type(self.backend).__name__ if self.backend else "none",
            "cache_hit_rate_percent": cache_hit_rate,
            "transaction_level": self._transaction_level
        }
    
    @asynccontextmanager
    async def transaction(self):
        """Context manager for transactions"""
        self._transaction_level += 1
        self.stats["transaction_count"] += 1
        
        try:
            yield
        finally:
            self._transaction_level -= 1
    
    async def backup_database(self, backup_path: str) -> bool:
        """Create a backup of the database"""
        try:
            # This is a simplified backup - in production, use proper backup tools
            async def backup(conn):
                # Create backup connection
                import shutil
                if isinstance(self.backend, SQLiteBackend):
                    shutil.copy2(self.backend.db_path, backup_path)
                    return True
                return False
            
            return await self.execute_sql(backup)
            
        except Exception as e:
            logger.error(f"Database backup failed: {e}")
            return False
    
    async def restore_database(self, backup_path: str) -> bool:
        """Restore database from backup"""
        try:
            async def restore(conn):
                import shutil
                if isinstance(self.backend, SQLiteBackend):
                    # Close existing connection first
                    await self.backend.disconnect()
                    
                    # Restore backup
                    shutil.copy2(backup_path, self.backend.db_path)
                    
                    # Reconnect
                    await self.backend.connect()
                    return True
                return False
            
            return await self.execute_sql(restore)
            
        except Exception as e:
            logger.error(f"Database restore failed: {e}")
            return False