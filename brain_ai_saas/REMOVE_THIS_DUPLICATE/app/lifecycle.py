"""
Application Lifecycle Management
Handles startup and shutdown of the Brain-Inspired AI Framework.
"""

import asyncio
import signal
from typing import Dict, Any

from loguru import logger

from app.config import get_settings
from core.encoder import Encoder
from core.memory import MemoryStore
from core.learning import LearningEngine
from core.routing import SparseRouter
from core.reasoning import ReasoningEngine
from core.feedback import FeedbackProcessor
from storage.persistence import PersistenceManager
from services.scheduler import Scheduler
from services.monitoring import MetricsCollector


class BrainSystem:
    """Main brain-inspired AI system component"""
    
    def __init__(self):
        self.encoder: Encoder = None
        self.memory_store: MemoryStore = None
        self.learning_engine: LearningEngine = None
        self.sparse_router: SparseRouter = None
        self.reasoning_engine: ReasoningEngine = None
        self.feedback_processor: FeedbackProcessor = None
        self.persistence_manager: PersistenceManager = None
        self.scheduler: Scheduler = None
        self.metrics: MetricsCollector = None
        
        self._initialized = False
        self._shutdown_event = asyncio.Event()
    
    async def initialize(self):
        """Initialize all brain system components"""
        if self._initialized:
            return
        
        logger.info("🧠 Initializing Brain-Inspired AI System...")
        
        try:
            settings = get_settings()
            
            # Initialize storage layer first
            logger.info("💾 Initializing storage layer...")
            self.persistence_manager = PersistenceManager()
            await self.persistence_manager.initialize()
            
            # Initialize core components
            logger.info("🧠 Initializing core brain components...")
            
            self.encoder = Encoder()
            self.memory_store = MemoryStore(self.persistence_manager)
            self.learning_engine = LearningEngine(settings)
            self.sparse_router = SparseRouter()
            self.reasoning_engine = ReasoningEngine()
            self.feedback_processor = FeedbackProcessor(self.learning_engine)
            
            # Initialize services
            logger.info("⚙️ Initializing services...")
            self.scheduler = Scheduler(self)
            self.metrics = MetricsCollector()
            
            # Connect components
            self.memory_store.set_learning_engine(self.learning_engine)
            self.feedback_processor.set_memory_store(self.memory_store)
            
            # Start background services
            logger.info("🚀 Starting background services...")
            await self.scheduler.start()
            await self.metrics.start()
            
            self._initialized = True
            logger.info("✅ Brain-Inspired AI System initialized successfully!")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize brain system: {e}")
            raise
    
    async def shutdown(self):
        """Shutdown all brain system components"""
        if not self._initialized:
            return
        
        logger.info("🛑 Shutting down Brain-Inspired AI System...")
        
        try:
            # Stop background services first
            if self.scheduler:
                await self.scheduler.stop()
            
            if self.metrics:
                await self.metrics.stop()
            
            # Cleanup storage
            if self.persistence_manager:
                await self.persistence_manager.cleanup()
            
            self._initialized = False
            logger.info("✅ Brain-Inspired AI System shutdown complete")
            
        except Exception as e:
            logger.error(f"❌ Error during shutdown: {e}")
    
    async def process_input(self, raw_input: Dict[str, Any]) -> Dict[str, Any]:
        """Process input through the complete brain pipeline"""
        if not self._initialized:
            raise RuntimeError("Brain system not initialized")
        
        try:
            # 1. Encode input into patterns
            encoded_event = self.encoder.encode(raw_input)
            
            # 2. Retrieve relevant memories
            memories = await self.memory_store.retrieve(
                pattern=encoded_event["pattern"],
                context=encoded_event["context"]
            )
            
            # 3. Apply sparse routing
            active_memories = self.sparse_router.activate(
                memories, encoded_event["context"]
            )
            
            # 4. Reason with active memories
            reasoning_result = await self.reasoning_engine.reason(
                active_memories, encoded_event["context"]
            )
            
            # 5. Record metrics
            if self.metrics:
                self.metrics.record_memory_retrieval(len(memories))
                self.metrics.record_active_memories(len(active_memories))
            
            return {
                "encoded_event": encoded_event,
                "active_memories": active_memories,
                "reasoning_result": reasoning_result,
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"Error processing input: {e}")
            if self.metrics:
                self.metrics.record_error()
            raise
    
    async def process_feedback(
        self, 
        memory_id: str, 
        feedback_type: str, 
        outcome: Dict[str, Any]
    ) -> None:
        """Process feedback to update memory through learning"""
        if not self._initialized:
            raise RuntimeError("Brain system not initialized")
        
        try:
            await self.feedback_processor.process_feedback(
                memory_id, feedback_type, outcome
            )
            
            if self.metrics:
                self.metrics.record_learning_update()
                
        except Exception as e:
            logger.error(f"Error processing feedback: {e}")
            if self.metrics:
                self.metrics.record_error()
            raise
    
    async def wait_for_shutdown(self):
        """Wait for shutdown signal"""
        await self._shutdown_event.wait()
    
    def signal_shutdown(self):
        """Signal shutdown"""
        self._shutdown_event.set()


# Global brain system instance
_brain_system: BrainSystem = None


def get_brain_system() -> BrainSystem:
    """Get global brain system instance"""
    global _brain_system
    if _brain_system is None:
        _brain_system = BrainSystem()
    return _brain_system


async def start_brain_system():
    """Start the global brain system"""
    brain_system = get_brain_system()
    await brain_system.initialize()


async def shutdown_brain_system():
    """Shutdown the global brain system"""
    brain_system = get_brain_system()
    await brain_system.shutdown()


def setup_signal_handlers():
    """Setup signal handlers for graceful shutdown"""
    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}, initiating graceful shutdown...")
        brain_system = get_brain_system()
        brain_system.signal_shutdown()
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)