"""
Simple Persistent Memory
Key-value storage for simple persistent data storage.
"""

from typing import Dict, Any, Optional, List, Union
from datetime import datetime
from dataclasses import dataclass, asdict
import json
import hashlib
import sqlite3
import asyncio
from pathlib import Path
from loguru import logger

from storage.persistence import PersistenceManager


@dataclass
class KeyValueEntry:
    """Represents a key-value storage entry"""
    key: str
    value: Any
    data_type: str
    created_at: datetime
    updated_at: datetime
    access_count: int
    metadata: Dict[str, Any]
    version: int = 1
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "key": self.key,
            "value": self.value,
            "data_type": self.data_type,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "access_count": self.access_count,
            "metadata": self.metadata,
            "version": self.version
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'KeyValueEntry':
        return cls(
            key=data["key"],
            value=data["value"],
            data_type=data["data_type"],
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            access_count=data["access_count"],
            metadata=data["metadata"],
            version=data.get("version", 1)
        )


class KeyValueStore:
    """
    Simple Key-Value Persistent Storage
    
    Provides simple key-value storage with:
    - Automatic type detection and serialization
    - Version management
    - Access tracking
    - Metadata support
    - Basic querying capabilities
    """
    
    def __init__(self, persistence_manager: PersistenceManager):
        self.persistence_manager = persistence_manager
        self.db_path = Path("brain_ai_kv.db")
        
        # In-memory cache for fast access
        self._cache: Dict[str, KeyValueEntry] = {}
        
        # Index for efficient searching
        self._key_index: Dict[str, List[str]] = {}  # pattern -> keys
        self._type_index: Dict[str, List[str]] = {}  # type -> keys
        
        # Statistics
        self.stats = {
            "total_operations": 0,
            "get_operations": 0,
            "set_operations": 0,
            "delete_operations": 0,
            "cache_hits": 0,
            "cache_misses": 0
        }
    
    async def initialize(self):
        """Initialize the key-value store"""
        logger.info("💾 Initializing key-value store...")
        
        try:
            # Initialize database
            await self._init_database()
            
            # Load existing data
            await self._load_data()
            
            # Build indices
            await self._build_indices()
            
            logger.info("✅ Key-value store initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize key-value store: {e}")
            raise
    
    async def set(
        self, 
        key: str, 
        value: Any, 
        metadata: Optional[Dict[str, Any]] = None,
        data_type: Optional[str] = None
    ) -> bool:
        """
        Store a key-value pair
        
        Args:
            key: Storage key
            value: Value to store
            metadata: Optional metadata
            data_type: Optional data type hint
            
        Returns:
            True if successful
        """
        try:
            self.stats["total_operations"] += 1
            self.stats["set_operations"] += 1
            
            # Detect data type if not provided
            if data_type is None:
                data_type = self._detect_data_type(value)
            
            # Serialize value
            serialized_value = self._serialize_value(value, data_type)
            
            # Get current entry or create new
            current_time = datetime.now()
            if key in self._cache:
                entry = self._cache[key]
                entry.value = serialized_value
                entry.updated_at = current_time
                entry.access_count = 0  # Reset on update
                entry.version += 1
                if metadata:
                    entry.metadata.update(metadata)
            else:
                entry = KeyValueEntry(
                    key=key,
                    value=serialized_value,
                    data_type=data_type,
                    created_at=current_time,
                    updated_at=current_time,
                    access_count=0,
                    metadata=metadata or {}
                )
            
            # Update cache
            self._cache[key] = entry
            
            # Update indices
            self._update_indices(key, entry)
            
            # Persist to database
            await self._persist_entry(entry)
            
            logger.debug(f"Stored key-value pair: {key}")
            return True
            
        except Exception as e:
            logger.error(f"Error setting key-value pair {key}: {e}")
            return False
    
    async def get(self, key: str, default: Any = None) -> Any:
        """
        Retrieve a value by key
        
        Args:
            key: Storage key
            default: Default value if key not found
            
        Returns:
            Stored value or default
        """
        try:
            self.stats["total_operations"] += 1
            self.stats["get_operations"] += 1
            
            # Check cache first
            if key in self._cache:
                entry = self._cache[key]
                entry.access_count += 1
                self.stats["cache_hits"] += 1
                
                # Update access tracking in database
                await self._update_access_count(key)
                
                return self._deserialize_value(entry.value, entry.data_type)
            else:
                self.stats["cache_misses"] += 1
                
                # Try to load from database
                entry = await self._load_entry(key)
                if entry:
                    self._cache[key] = entry
                    entry.access_count += 1
                    
                    # Update indices
                    self._update_indices(key, entry)
                    
                    return self._deserialize_value(entry.value, entry.data_type)
                else:
                    logger.debug(f"Key not found: {key}")
                    return default
            
        except Exception as e:
            logger.error(f"Error getting key {key}: {e}")
            return default
    
    async def delete(self, key: str) -> bool:
        """
        Delete a key-value pair
        
        Args:
            key: Key to delete
            
        Returns:
            True if successful
        """
        try:
            self.stats["total_operations"] += 1
            self.stats["delete_operations"] += 1
            
            # Remove from cache
            if key in self._cache:
                del self._cache[key]
            
            # Remove from indices
            self._remove_from_indices(key)
            
            # Remove from database
            await self._delete_entry(key)
            
            logger.debug(f"Deleted key-value pair: {key}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting key {key}: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """
        Check if a key exists
        
        Args:
            key: Key to check
            
        Returns:
            True if key exists
        """
        try:
            return key in self._cache or await self._entry_exists(key)
        except Exception as e:
            logger.error(f"Error checking key existence {key}: {e}")
            return False
    
    async def keys(self, pattern: Optional[str] = None) -> List[str]:
        """
        Get all keys, optionally filtered by pattern
        
        Args:
            pattern: Optional key pattern to filter by
            
        Returns:
            List of matching keys
        """
        try:
            all_keys = set(self._cache.keys())
            
            # Add keys from database that aren't in cache
            db_keys = await self._get_all_keys()
            all_keys.update(db_keys)
            
            # Filter by pattern if provided
            if pattern:
                import fnmatch
                matching_keys = []
                for key in all_keys:
                    if fnmatch.fnmatch(key, pattern):
                        matching_keys.append(key)
                return sorted(matching_keys)
            else:
                return sorted(list(all_keys))
                
        except Exception as e:
            logger.error(f"Error getting keys: {e}")
            return []
    
    async def get_by_type(self, data_type: str) -> Dict[str, Any]:
        """
        Get all entries of a specific data type
        
        Args:
            data_type: Data type to filter by
            
        Returns:
            Dictionary of key-value pairs
        """
        try:
            result = {}
            
            # Get from cache
            for key, entry in self._cache.items():
                if entry.data_type == data_type:
                    result[key] = self._deserialize_value(entry.value, entry.data_type)
            
            # Get from database
            db_entries = await self._get_entries_by_type(data_type)
            for entry_data in db_entries:
                key = entry_data["key"]
                if key not in result:  # Don't override cache entries
                    entry = KeyValueEntry.from_dict(entry_data)
                    result[key] = self._deserialize_value(entry.value, entry.data_type)
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting entries by type {data_type}: {e}")
            return {}
    
    async def search(self, query: str, case_sensitive: bool = False) -> Dict[str, Any]:
        """
        Search for keys/values containing query string
        
        Args:
            query: Search query
            case_sensitive: Whether search is case sensitive
            
        Returns:
            Dictionary of matching key-value pairs
        """
        try:
            result = {}
            query_lower = query.lower() if not case_sensitive else query
            
            # Search in cache
            for key, entry in self._cache.items():
                if case_sensitive:
                    if query in key or query in str(entry.value):
                        result[key] = self._deserialize_value(entry.value, entry.data_type)
                else:
                    if query_lower in key.lower() or query_lower in str(entry.value).lower():
                        result[key] = self._deserialize_value(entry.value, entry.data_type)
            
            # Search in database (only for entries not in cache)
            db_matches = await self._search_in_database(query, case_sensitive)
            for entry_data in db_matches:
                key = entry_data["key"]
                if key not in result:
                    entry = KeyValueEntry.from_dict(entry_data)
                    result[key] = self._deserialize_value(entry.value, entry.data_type)
            
            return result
            
        except Exception as e:
            logger.error(f"Error searching for '{query}': {e}")
            return {}
    
    async def get_metadata(self, key: str) -> Dict[str, Any]:
        """
        Get metadata for a key
        
        Args:
            key: Storage key
            
        Returns:
            Metadata dictionary
        """
        try:
            if key in self._cache:
                return self._cache[key].metadata
            
            # Load from database
            entry = await self._load_entry(key)
            return entry.metadata if entry else {}
            
        except Exception as e:
            logger.error(f"Error getting metadata for {key}: {e}")
            return {}
    
    async def update_metadata(self, key: str, metadata: Dict[str, Any]) -> bool:
        """
        Update metadata for a key
        
        Args:
            key: Storage key
            metadata: New metadata
            
        Returns:
            True if successful
        """
        try:
            if key in self._cache:
                self._cache[key].metadata.update(metadata)
                await self._persist_entry(self._cache[key])
                return True
            
            # Load, update, and persist
            entry = await self._load_entry(key)
            if entry:
                entry.metadata.update(metadata)
                await self._persist_entry(entry)
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error updating metadata for {key}: {e}")
            return False
    
    async def clear(self) -> bool:
        """
        Clear all data from the store
        
        Returns:
            True if successful
        """
        try:
            # Clear cache
            self._cache.clear()
            self._key_index.clear()
            self._type_index.clear()
            
            # Clear database
            await self._clear_database()
            
            logger.info("🧹 Cleared all key-value data")
            return True
            
        except Exception as e:
            logger.error(f"Error clearing key-value store: {e}")
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get store statistics"""
        
        cache_hit_rate = (
            self.stats["cache_hits"] / max(1, self.stats["cache_hits"] + self.stats["cache_misses"])
        ) * 100
        
        return {
            **self.stats,
            "cache_size": len(self._cache),
            "cache_hit_rate_percent": cache_hit_rate,
            "index_sizes": {
                "key_index": len(self._key_index),
                "type_index": len(self._type_index)
            }
        }
    
    def _detect_data_type(self, value: Any) -> str:
        """Detect the data type of a value"""
        
        if value is None:
            return "null"
        elif isinstance(value, bool):
            return "bool"
        elif isinstance(value, int):
            return "int"
        elif isinstance(value, float):
            return "float"
        elif isinstance(value, str):
            return "str"
        elif isinstance(value, list):
            return "list"
        elif isinstance(value, dict):
            return "dict"
        elif isinstance(value, tuple):
            return "tuple"
        elif isinstance(value, set):
            return "set"
        else:
            return "object"
    
    def _serialize_value(self, value: Any, data_type: str) -> Any:
        """Serialize value for storage"""
        
        if data_type in ["str", "int", "float", "bool"]:
            return value
        elif data_type == "null":
            return None
        elif data_type in ["list", "dict", "tuple", "set", "object"]:
            return json.dumps(value, default=str)
        else:
            return str(value)
    
    def _deserialize_value(self, serialized_value: Any, data_type: str) -> Any:
        """Deserialize value from storage"""
        
        try:
            if data_type in ["str", "int", "float", "bool"]:
                return serialized_value
            elif data_type == "null":
                return None
            elif data_type in ["list", "dict", "tuple", "set"]:
                return json.loads(serialized_value)
            else:
                return serialized_value
                
        except (json.JSONDecodeError, TypeError):
            # Fallback to string representation
            return str(serialized_value)
    
    def _update_indices(self, key: str, entry: KeyValueEntry):
        """Update search indices"""
        
        # Key pattern index (simple pattern extraction)
        pattern = self._extract_key_pattern(key)
        if pattern not in self._key_index:
            self._key_index[pattern] = []
        if key not in self._key_index[pattern]:
            self._key_index[pattern].append(key)
        
        # Type index
        if entry.data_type not in self._type_index:
            self._type_index[entry.data_type] = []
        if key not in self._type_index[entry.data_type]:
            self._type_index[entry.data_type].append(key)
    
    def _remove_from_indices(self, key: str):
        """Remove key from indices"""
        
        # Remove from key pattern index
        for pattern_keys in self._key_index.values():
            if key in pattern_keys:
                pattern_keys.remove(key)
        
        # Remove from type index
        for type_keys in self._type_index.values():
            if key in type_keys:
                type_keys.remove(key)
    
    def _extract_key_pattern(self, key: str) -> str:
        """Extract a searchable pattern from key"""
        
        # Simple pattern extraction - split by underscores and take components
        parts = key.split('_')
        if len(parts) >= 2:
            return f"{parts[0]}_{parts[1]}"
        else:
            return parts[0] if parts else key
    
    async def _init_database(self):
        """Initialize SQLite database"""
        
        def create_table(conn):
            conn.execute("""
                CREATE TABLE IF NOT EXISTS key_value_entries (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    data_type TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    access_count INTEGER DEFAULT 0,
                    metadata TEXT DEFAULT '{}',
                    version INTEGER DEFAULT 1
                )
            """)
            
            # Create indices for better performance
            conn.execute("CREATE INDEX IF NOT EXISTS idx_data_type ON key_value_entries(data_type)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_created_at ON key_value_entries(created_at)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_access_count ON key_value_entries(access_count)")
        
        await self.persistence_manager.execute_sql(create_table)
    
    async def _load_data(self):
        """Load existing data from database"""
        
        async def load_entries(conn):
            cursor = conn.execute("SELECT * FROM key_value_entries")
            rows = cursor.fetchall()
            
            for row in rows:
                data = {
                    "key": row[0],
                    "value": row[1],
                    "data_type": row[2],
                    "created_at": row[3],
                    "updated_at": row[4],
                    "access_count": row[5],
                    "metadata": json.loads(row[6] or "{}"),
                    "version": row[7]
                }
                
                entry = KeyValueEntry.from_dict(data)
                self._cache[entry.key] = entry
        
        await self.persistence_manager.execute_sql(load_entries)
    
    async def _build_indices(self):
        """Build search indices"""
        
        for key, entry in self._cache.items():
            self._update_indices(key, entry)
    
    async def _persist_entry(self, entry: KeyValueEntry):
        """Persist entry to database"""
        
        async def save_entry(conn):
            conn.execute("""
                INSERT OR REPLACE INTO key_value_entries 
                (key, value, data_type, created_at, updated_at, access_count, metadata, version)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                entry.key,
                entry.value,
                entry.data_type,
                entry.created_at.isoformat(),
                entry.updated_at.isoformat(),
                entry.access_count,
                json.dumps(entry.metadata),
                entry.version
            ))
        
        await self.persistence_manager.execute_sql(save_entry)
    
    async def _load_entry(self, key: str) -> Optional[KeyValueEntry]:
        """Load entry from database"""
        
        async def get_entry(conn):
            cursor = conn.execute(
                "SELECT * FROM key_value_entries WHERE key = ?",
                (key,)
            )
            row = cursor.fetchone()
            
            if row:
                data = {
                    "key": row[0],
                    "value": row[1],
                    "data_type": row[2],
                    "created_at": row[3],
                    "updated_at": row[4],
                    "access_count": row[5],
                    "metadata": json.loads(row[6] or "{}"),
                    "version": row[7]
                }
                return KeyValueEntry.from_dict(data)
            return None
        
        return await self.persistence_manager.execute_sql(get_entry)
    
    async def _delete_entry(self, key: str):
        """Delete entry from database"""
        
        async def delete(conn):
            conn.execute("DELETE FROM key_value_entries WHERE key = ?", (key,))
        
        await self.persistence_manager.execute_sql(delete)
    
    async def _entry_exists(self, key: str) -> bool:
        """Check if entry exists in database"""
        
        async def check_exists(conn):
            cursor = conn.execute(
                "SELECT 1 FROM key_value_entries WHERE key = ? LIMIT 1",
                (key,)
            )
            return cursor.fetchone() is not None
        
        return await self.persistence_manager.execute_sql(check_exists)
    
    async def _get_all_keys(self) -> List[str]:
        """Get all keys from database"""
        
        async def get_keys(conn):
            cursor = conn.execute("SELECT key FROM key_value_entries")
            return [row[0] for row in cursor.fetchall()]
        
        return await self.persistence_manager.execute_sql(get_keys)
    
    async def _get_entries_by_type(self, data_type: str) -> List[Dict[str, Any]]:
        """Get entries by data type from database"""
        
        async def get_by_type(conn):
            cursor = conn.execute(
                "SELECT * FROM key_value_entries WHERE data_type = ?",
                (data_type,)
            )
            rows = cursor.fetchall()
            
            results = []
            for row in rows:
                results.append({
                    "key": row[0],
                    "value": row[1],
                    "data_type": row[2],
                    "created_at": row[3],
                    "updated_at": row[4],
                    "access_count": row[5],
                    "metadata": json.loads(row[6] or "{}"),
                    "version": row[7]
                })
            return results
        
        return await self.persistence_manager.execute_sql(get_by_type)
    
    async def _search_in_database(self, query: str, case_sensitive: bool) -> List[Dict[str, Any]]:
        """Search in database for matching entries"""
        
        async def search(conn):
            if case_sensitive:
                cursor = conn.execute("""
                    SELECT * FROM key_value_entries 
                    WHERE key LIKE ? OR value LIKE ?
                """, (f"%{query}%", f"%{query}%"))
            else:
                cursor = conn.execute("""
                    SELECT * FROM key_value_entries 
                    WHERE LOWER(key) LIKE LOWER(?) OR LOWER(value) LIKE LOWER(?)
                """, (f"%{query}%", f"%{query}%"))
            
            rows = cursor.fetchall()
            
            results = []
            for row in rows:
                results.append({
                    "key": row[0],
                    "value": row[1],
                    "data_type": row[2],
                    "created_at": row[3],
                    "updated_at": row[4],
                    "access_count": row[5],
                    "metadata": json.loads(row[6] or "{}"),
                    "version": row[7]
                })
            return results
        
        return await self.persistence_manager.execute_sql(search)
    
    async def _update_access_count(self, key: str):
        """Update access count in database"""
        
        async def update_count(conn):
            conn.execute("""
                UPDATE key_value_entries 
                SET access_count = access_count + 1 
                WHERE key = ?
            """, (key,))
        
        await self.persistence_manager.execute_sql(update_count)
    
    async def _clear_database(self):
        """Clear all data from database"""
        
        async def clear(conn):
            conn.execute("DELETE FROM key_value_entries")
        
        await self.persistence_manager.execute_sql(clear)