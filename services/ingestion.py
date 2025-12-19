"""
Event Ingestion Service
Handles the ingestion of events and data into the brain system.
"""

from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import asyncio
import json
from loguru import logger

from core.encoder import Encoder
from core.memory import MemoryStore, MemoryType
from storage.persistence import PersistenceManager


class IngestionSource(Enum):
    """Sources of ingested data"""
    API = "api"
    WEBHOOK = "webhook"
    FILE = "file"
    DATABASE = "database"
    MESSAGE_QUEUE = "message_queue"
    STREAM = "stream"
    SCHEDULED = "scheduled"


class IngestionStatus(Enum):
    """Status of ingestion operations"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    FILTERED = "filtered"


@dataclass
class IngestionEvent:
    """Represents an ingestion event"""
    id: str
    source: IngestionSource
    data: Dict[str, Any]
    metadata: Dict[str, Any]
    timestamp: datetime
    status: IngestionStatus = IngestionStatus.PENDING
    processed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    memory_ids: List[str] = None


class IngestionService:
    """
    Event Ingestion Service
    
    Handles the ingestion of various types of events and data:
    - API endpoints
    - Webhook data
    - File uploads
    - Database changes
    - Message queue messages
    - Stream data
    - Scheduled events
    """
    
    def __init__(self, persistence_manager: PersistenceManager):
        self.persistence_manager = persistence_manager
        self.encoder = None
        self.memory_store = None
        
        # Ingestion pipeline
        self.ingestion_queue: List[IngestionEvent] = []
        self.processed_events: List[IngestionEvent] = []
        
        # Ingestion hooks
        self.pre_processors: List[Callable] = []
        self.post_processors: List[Callable] = []
        self.filters: List[Callable] = []
        
        # Statistics
        self.stats = {
            "total_ingestions": 0,
            "successful_ingestions": 0,
            "failed_ingestions": 0,
            "filtered_ingestions": 0,
            "events_by_source": {},
            "average_processing_time": 0.0
        }
        
        # Configuration
        self.batch_size = 50
        self.processing_interval = 1.0
        self.max_queue_size = 1000
    
    def set_encoder(self, encoder: Encoder):
        """Set the pattern encoder"""
        self.encoder = encoder
    
    def set_memory_store(self, memory_store: MemoryStore):
        """Set the memory store"""
        self.memory_store = memory_store
    
    async def ingest_event(
        self,
        data: Dict[str, Any],
        source: IngestionSource,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Ingest a single event
        
        Args:
            data: Event data
            source: Source of the event
            metadata: Additional metadata
            
        Returns:
            Event ID
        """
        try:
            event_id = f"ing_{len(self.ingestion_queue)}_{datetime.now().timestamp()}"
            
            ingestion_event = IngestionEvent(
                id=event_id,
                source=source,
                data=data,
                metadata=metadata or {},
                timestamp=datetime.now()
            )
            
            # Add to queue
            await self._queue_event(ingestion_event)
            
            # Update statistics
            self.stats["total_ingestions"] += 1
            source_name = source.value
            self.stats["events_by_source"][source_name] = (
                self.stats["events_by_source"].get(source_name, 0) + 1
            )
            
            logger.debug(f"Queued ingestion event {event_id} from {source.value}")
            
            # Process immediately if queue is getting full
            if len(self.ingestion_queue) >= self.batch_size:
                await self._process_ingestion_batch()
            
            return event_id
            
        except Exception as e:
            logger.error(f"Error ingesting event: {e}")
            raise
    
    async def ingest_batch(
        self,
        events: List[Dict[str, Any]],
        source: IngestionSource,
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """
        Ingest multiple events in batch
        
        Args:
            events: List of event data
            source: Source of the events
            metadata: Additional metadata
            
        Returns:
            List of event IDs
        """
        try:
            event_ids = []
            
            for event_data in events:
                event_id = await self.ingest_event(event_data, source, metadata)
                event_ids.append(event_id)
            
            # Process the batch
            if len(self.ingestion_queue) >= self.batch_size:
                await self._process_ingestion_batch()
            
            logger.info(f"Batch ingested {len(event_ids)} events from {source.value}")
            return event_ids
            
        except Exception as e:
            logger.error(f"Error in batch ingestion: {e}")
            raise
    
    async def start_processing(self):
        """Start the ingestion processing background task"""
        asyncio.create_task(self._ingestion_processing_loop())
        logger.info("🚀 Started ingestion processing service")
    
    async def stop_processing(self):
        """Stop the ingestion processing background task"""
        # Process any remaining events
        if self.ingestion_queue:
            await self._process_ingestion_batch()
        logger.info("🛑 Stopped ingestion processing service")
    
    async def _ingestion_processing_loop(self):
        """Background loop for processing ingestion events"""
        while True:
            try:
                if self.ingestion_queue:
                    await self._process_ingestion_batch()
                
                await asyncio.sleep(self.processing_interval)
                
            except Exception as e:
                logger.error(f"Error in ingestion processing loop: {e}")
                await asyncio.sleep(5)  # Wait before retrying
    
    async def _process_ingestion_batch(self):
        """Process a batch of ingestion events"""
        if not self.ingestion_queue:
            return
        
        try:
            # Get batch of events
            batch = self.ingestion_queue[:self.batch_size]
            self.ingestion_queue = self.ingestion_queue[self.batch_size:]
            
            for event in batch:
                try:
                    await self._process_single_event(event)
                    self.processed_events.append(event)
                    
                except Exception as e:
                    logger.error(f"Error processing ingestion event {event.id}: {e}")
                    event.status = IngestionStatus.FAILED
                    event.error_message = str(e)
                    self.processed_events.append(event)
            
            # Keep processed events history manageable
            if len(self.processed_events) > 10000:
                self.processed_events = self.processed_events[-5000:]
            
            self.stats["successful_ingestions"] += len([
                event for event in batch if event.status == IngestionStatus.COMPLETED
            ])
            
        except Exception as e:
            logger.error(f"Error processing ingestion batch: {e}")
            # Put processed items back in queue for retry
            self.ingestion_queue = batch + self.ingestion_queue
    
    async def _process_single_event(self, event: IngestionEvent):
        """Process a single ingestion event"""
        
        start_time = datetime.now()
        
        try:
            event.status = IngestionStatus.PROCESSING
            
            # Apply pre-processors
            processed_data = await self._apply_pre_processors(event)
            
            # Apply filters
            if await self._apply_filters(event, processed_data):
                event.status = IngestionStatus.FILTERED
                self.stats["filtered_ingestions"] += 1
                return
            
            # Encode the event
            if not self.encoder:
                raise RuntimeError("Encoder not initialized")
            
            encoded_result = self.encoder.encode(processed_data)
            
            # Create memory from encoded event
            if not self.memory_store:
                raise RuntimeError("Memory store not initialized")
            
            memory_item = self.memory_store.create_memory_item(
                pattern_signature=encoded_result["pattern"]["signature"],
                content={
                    "original_data": processed_data,
                    "encoded_pattern": encoded_result["pattern"],
                    "ingestion_source": event.source.value
                },
                context=encoded_result["context"],
                memory_type=MemoryType.EPISODIC,
                tags=[event.source.value, "ingested"],
                strength=0.5,
                confidence=encoded_result["pattern"]["confidence"]
            )
            
            # Store the memory
            memory_id = await self.memory_store.store(memory_item)
            event.memory_ids = [memory_id]
            
            # Apply post-processors
            await self._apply_post_processors(event, memory_item)
            
            # Log the event
            await self._log_ingestion_event(event)
            
            event.status = IngestionStatus.COMPLETED
            event.processed_at = datetime.now()
            
            # Update processing time stats
            processing_time = (event.processed_at - start_time).total_seconds()
            self._update_processing_time_stats(processing_time)
            
        except Exception as e:
            event.status = IngestionStatus.FAILED
            event.error_message = str(e)
            self.stats["failed_ingestions"] += 1
            raise
    
    async def _queue_event(self, event: IngestionEvent):
        """Queue event for processing"""
        
        # Add to queue
        self.ingestion_queue.append(event)
        
        # Limit queue size
        if len(self.ingestion_queue) > self.max_queue_size:
            # Remove oldest events
            self.ingestion_queue = self.ingestion_queue[-self.max_queue_size:]
    
    async def _apply_pre_processors(self, event: IngestionEvent) -> Dict[str, Any]:
        """Apply pre-processing functions to event data"""
        
        processed_data = event.data.copy()
        
        for pre_processor in self.pre_processors:
            try:
                processed_data = await pre_processor(processed_data, event)
            except Exception as e:
                logger.warning(f"Pre-processor failed: {e}")
        
        return processed_data
    
    async def _apply_filters(self, event: IngestionEvent, data: Dict[str, Any]) -> bool:
        """Apply filters to determine if event should be processed"""
        
        for filter_func in self.filters:
            try:
                if await filter_func(event, data):
                    return True  # Event filtered out
            except Exception as e:
                logger.warning(f"Filter failed: {e}")
        
        return False  # Event not filtered
    
    async def _apply_post_processors(self, event: IngestionEvent, memory_item):
        """Apply post-processing functions"""
        
        for post_processor in self.post_processors:
            try:
                await post_processor(event, memory_item)
            except Exception as e:
                logger.warning(f"Post-processor failed: {e}")
    
    async def _log_ingestion_event(self, event: IngestionEvent):
        """Log ingestion event to database"""
        
        try:
            log_data = {
                "type": "ingestion_event",
                "event_id": event.id,
                "source": event.source.value,
                "status": event.status.value,
                "metadata": event.metadata,
                "memory_ids": event.memory_ids or [],
                "processing_time": (
                    (event.processed_at - event.timestamp).total_seconds() 
                    if event.processed_at else None
                ),
                "error": event.error_message
            }
            
            await self.persistence_manager.log_event(log_data)
            
        except Exception as e:
            logger.error(f"Error logging ingestion event: {e}")
    
    def _update_processing_time_stats(self, processing_time: float):
        """Update processing time statistics"""
        
        total_processed = self.stats["successful_ingestions"]
        if total_processed == 1:
            self.stats["average_processing_time"] = processing_time
        else:
            current_avg = self.stats["average_processing_time"]
            self.stats["average_processing_time"] = (
                (current_avg * (total_processed - 1) + processing_time) / total_processed
            )
    
    def add_pre_processor(self, processor: Callable):
        """Add a pre-processor function"""
        self.pre_processors.append(processor)
    
    def add_post_processor(self, processor: Callable):
        """Add a post-processor function"""
        self.post_processors.append(processor)
    
    def add_filter(self, filter_func: Callable):
        """Add a filter function"""
        self.filters.append(filter_func)
    
    def get_ingestion_statistics(self) -> Dict[str, Any]:
        """Get ingestion service statistics"""
        
        return {
            **self.stats,
            "queue_size": len(self.ingestion_queue),
            "processed_events_count": len(self.processed_events),
            "success_rate": (
                self.stats["successful_ingestions"] / max(1, self.stats["total_ingestions"])
            ) * 100,
            "filter_rate": (
                self.stats["filtered_ingestions"] / max(1, self.stats["total_ingestions"])
            ) * 100
        }
    
    def get_recent_events(self, hours: int = 24, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent ingestion events"""
        
        cutoff_time = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        cutoff_time = cutoff_time.replace(hour=23)  # Approximate 24 hours ago
        
        recent_events = [
            event for event in self.processed_events 
            if event.timestamp >= cutoff_time
        ][-limit:]
        
        return [
            {
                "id": event.id,
                "source": event.source.value,
                "status": event.status.value,
                "timestamp": event.timestamp.isoformat(),
                "processed_at": event.processed_at.isoformat() if event.processed_at else None,
                "memory_count": len(event.memory_ids) if event.memory_ids else 0,
                "error": event.error_message
            }
            for event in recent_events
        ]


# Default pre-processors

async def validate_data_preprocessor(data: Dict[str, Any], event: IngestionEvent) -> Dict[str, Any]:
    """Validate and clean input data"""
    
    # Ensure required fields exist
    if "timestamp" not in data:
        data["timestamp"] = datetime.now().isoformat()
    
    if "source" not in data:
        data["source"] = event.source.value
    
    # Clean data types
    for key, value in data.items():
        if key.endswith("_count") or key.endswith("_id"):
            try:
                if isinstance(value, str) and value.isdigit():
                    data[key] = int(value)
                elif isinstance(value, str) and value.replace(".", "").isdigit():
                    data[key] = float(value)
            except (ValueError, TypeError):
                pass  # Keep original value if conversion fails
    
    return data


async def enrich_metadata_preprocessor(data: Dict[str, Any], event: IngestionEvent) -> Dict[str, Any]:
    """Enrich data with additional metadata"""
    
    # Add processing metadata
    data["_ingestion"] = {
        "event_id": event.id,
        "ingested_at": datetime.now().isoformat(),
        "source": event.source.value,
        "metadata": event.metadata
    }
    
    return data


# Default filters

async def duplicate_filter(event: IngestionEvent, data: Dict[str, Any]) -> bool:
    """Filter out duplicate events"""
    
    # Simple duplicate detection based on content hash
    import hashlib
    content_str = json.dumps(data, sort_keys=True)
    content_hash = hashlib.md5(content_str.encode()).hexdigest()
    
    # Check against recently processed events
    for recent_event in event.__class__.__module__.split('.')[:10]:  # Limit scope
        if hasattr(recent_event, '_recent_hashes'):
            if content_hash in recent_event._recent_hashes:
                return True  # Filter out duplicate
            recent_event._recent_hashes.add(content_hash)
    
    return False  # Not a duplicate


async def low_quality_filter(event: IngestionEvent, data: Dict[str, Any]) -> bool:
    """Filter out low quality events"""
    
    # Filter out events with insufficient data
    if len(str(data)) < 10:  # Too small
        return True
    
    # Filter out events with only metadata
    data_keys = set(data.keys())
    exclude_keys = {"timestamp", "source", "_ingestion", "metadata"}
    meaningful_keys = data_keys - exclude_keys
    
    if len(meaningful_keys) == 0:
        return True
    
    return False  # Event has meaningful content