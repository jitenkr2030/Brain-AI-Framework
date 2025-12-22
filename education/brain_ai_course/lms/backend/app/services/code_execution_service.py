"""
Interactive Code Execution Service
Handles real-time code execution for Brain AI examples in the browser
"""

import asyncio
import docker
import tempfile
import os
import json
import uuid
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from fastapi import WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from dataclasses import dataclass
from enum import Enum
import logging

from app.database import get_db
from app.models.user import User
from app.models.lms_models import Lesson, Progress
from app.services.brain_ai_service import BrainAIService

logger = logging.getLogger(__name__)

class ExecutionStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"

class ExecutionLanguage(Enum):
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    RUST = "rust"
    GO = "go"
    JAVA = "java"
    CSHARP = "csharp"

@dataclass
class CodeExecutionRequest:
    code: str
    language: ExecutionLanguage
    lesson_id: int
    user_id: int
    dependencies: List[str] = None
    timeout: int = 30  # seconds
    memory_limit: int = 256  # MB
    cpu_limit: float = 1.0

@dataclass
class CodeExecutionResult:
    execution_id: str
    status: ExecutionStatus
    output: str
    error: Optional[str] = None
    execution_time: float = 0.0
    memory_used: int = 0
    stdout: str = ""
    stderr: str = ""
    timestamp: datetime = None

class CodeExecutionManager:
    """Manages code execution environments and WebSocket connections"""
    
    def __init__(self):
        self.docker_client = docker.from_env()
        self.active_sessions: Dict[str, WebSocket] = {}
        self.execution_queue: List[CodeExecutionRequest] = []
        self.running_executions: Dict[str, CodeExecutionResult] = {}
        self.brain_ai_service = BrainAIService()
        
    async def execute_code(
        self, 
        request: CodeExecutionRequest, 
        websocket: WebSocket,
        db: Session
    ) -> CodeExecutionResult:
        """Execute code in isolated Docker container"""
        execution_id = str(uuid.uuid4())
        
        try:
            # Update progress for lesson
            await self._update_lesson_progress(request.user_id, request.lesson_id, db)
            
            # Create execution result
            result = CodeExecutionResult(
                execution_id=execution_id,
                status=ExecutionStatus.PENDING,
                output="",
                timestamp=datetime.utcnow()
            )
            
            self.running_executions[execution_id] = result
            
            # Send initial status to client
            await websocket.send_json({
                "type": "execution_start",
                "execution_id": execution_id,
                "status": "pending"
            })
            
            # Execute code based on language
            if request.language == ExecutionLanguage.PYTHON:
                result = await self._execute_python_code(request, result, websocket)
            elif request.language == ExecutionLanguage.JAVASCRIPT:
                result = await self._execute_javascript_code(request, result, websocket)
            else:
                result.error = f"Language {request.language} not yet supported"
                result.status = ExecutionStatus.FAILED
            
            # Store result for history
            await self._store_execution_history(request, result, db)
            
            # Send final result
            await websocket.send_json({
                "type": "execution_complete",
                "execution_id": execution_id,
                "status": result.status.value,
                "output": result.output,
                "error": result.error,
                "execution_time": result.execution_time,
                "stdout": result.stdout,
                "stderr": result.stderr
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Code execution error: {e}")
            result.status = ExecutionStatus.FAILED
            result.error = str(e)
            await websocket.send_json({
                "type": "execution_error",
                "execution_id": execution_id,
                "error": str(e)
            })
            return result
        
        finally:
            # Clean up
            if execution_id in self.running_executions:
                del self.running_executions[execution_id]
    
    async def _execute_python_code(
        self, 
        request: CodeExecutionRequest, 
        result: CodeExecutionResult,
        websocket: WebSocket
    ) -> CodeExecutionResult:
        """Execute Python code with Brain AI integration"""
        result.status = ExecutionStatus.RUNNING
        start_time = time.time()
        
        # Create temporary directory for execution
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create the Python script
            script_content = self._create_python_script(request)
            script_path = os.path.join(temp_dir, "main.py")
            
            with open(script_path, 'w') as f:
                f.write(script_content)
            
            # Create requirements.txt if needed
            if request.dependencies:
                req_path = os.path.join(temp_dir, "requirements.txt")
                with open(req_path, 'w') as f:
                    for dep in request.dependencies:
                        f.write(f"{dep}\n")
            
            # Prepare Docker container
            container_config = {
                'image': 'python:3.9-slim',
                'command': ['python', '/workspace/main.py'],
                'volumes': {temp_dir: {'bind': '/workspace', 'mode': 'rw'}},
                'mem_limit': f"{request.memory_limit}m",
                'cpu_period': 100000,
                'cpu_quota': int(request.cpu_limit * 100000),
                'detach': False,
                'stdout': True,
                'stderr': True,
                'stream': True
            }
            
            try:
                # Run container with timeout
                container = self.docker_client.containers.run(**container_config)
                
                # Stream output to WebSocket
                output_lines = []
                for line in container.logs(stream=True, decode=True):
                    line_str = line.decode('utf-8').strip()
                    if line_str:
                        output_lines.append(line_str)
                        # Send live output to client
                        await websocket.send_json({
                            "type": "execution_output",
                            "output": line_str
                        })
                
                result.output = "\n".join(output_lines)
                result.stdout = result.output
                result.status = ExecutionStatus.COMPLETED
                result.execution_time = time.time() - start_time
                
            except docker.errors.ContainerError as e:
                result.error = f"Container error: {e.stderr.decode('utf-8') if e.stderr else str(e)}"
                result.stderr = result.error
                result.status = ExecutionStatus.FAILED
                result.execution_time = time.time() - start_time
                
            except Exception as e:
                result.error = f"Execution error: {str(e)}"
                result.status = ExecutionStatus.FAILED
                result.execution_time = time.time() - start_time
        
        return result
    
    async def _execute_javascript_code(
        self, 
        request: CodeExecutionRequest, 
        result: CodeExecutionResult,
        websocket: WebSocket
    ) -> CodeExecutionResult:
        """Execute JavaScript/Node.js code"""
        result.status = ExecutionStatus.RUNNING
        start_time = time.time()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create Node.js script
            script_content = self._create_javascript_script(request)
            script_path = os.path.join(temp_dir, "main.js")
            
            with open(script_path, 'w') as f:
                f.write(script_content)
            
            container_config = {
                'image': 'node:18-alpine',
                'command': ['node', '/workspace/main.js'],
                'volumes': {temp_dir: {'bind': '/workspace', 'mode': 'rw'}},
                'mem_limit': f"{request.memory_limit}m",
                'cpu_period': 100000,
                'cpu_quota': int(request.cpu_limit * 100000),
                'detach': False,
                'stdout': True,
                'stderr': True,
                'stream': True
            }
            
            try:
                container = self.docker_client.containers.run(**container_config)
                
                output_lines = []
                for line in container.logs(stream=True, decode=True):
                    line_str = line.decode('utf-8').strip()
                    if line_str:
                        output_lines.append(line_str)
                        await websocket.send_json({
                            "type": "execution_output",
                            "output": line_str
                        })
                
                result.output = "\n".join(output_lines)
                result.stdout = result.output
                result.status = ExecutionStatus.COMPLETED
                result.execution_time = time.time() - start_time
                
            except Exception as e:
                result.error = str(e)
                result.stderr = result.error
                result.status = ExecutionStatus.FAILED
                result.execution_time = time.time() - start_time
        
        return result
    
    def _create_python_script(self, request: CodeExecutionRequest) -> str:
        """Create Python script with Brain AI integration"""
        brain_ai_integration = """
# Brain AI Framework Integration
try:
    import sys
    sys.path.append('/opt/brain-ai')
    
    # Import Brain AI components
    from brain_ai import MemorySystem, LearningEngine, ReasoningEngine
    from brain_ai.utils import setup_logger
    
    BRAIN_AI_AVAILABLE = True
    logger = setup_logger("code_execution")
    
except ImportError:
    BRAIN_AI_AVAILABLE = False
    print("Warning: Brain AI framework not available in this environment")
    MemorySystem = None
    LearningEngine = None
    ReasoningEngine = None
    logger = None

"""
        
        student_code = request.code
        
        # Wrap student code with Brain AI context
        wrapped_code = f"""
import json
import time
from datetime import datetime

# Code execution started at {datetime.utcnow().isoformat()}
start_time = time.time()

{brain_ai_integration}

# Student Code Below:
# ====================
{student_code}
# ====================

# Code execution completed
end_time = time.time()
execution_time = end_time - start_time

print(f"\\nExecution completed in {{execution_time:.3f}} seconds")
print(f"Memory usage: {self._get_memory_usage()}MB")

"""
        return wrapped_code
    
    def _create_javascript_script(self, request: CodeExecutionRequest) -> str:
        """Create JavaScript script with Brain AI integration"""
        brain_ai_integration = """
// Brain AI Framework Integration
const fs = require('fs');
const path = require('path');

// Try to load Brain AI components
let BrainAI = null;
try {
    BrainAI = require('/opt/brain-ai');
    console.log('Brain AI framework loaded successfully');
} catch (error) {
    console.log('Warning: Brain AI framework not available');
}

// Brain AI Context
const brainAIContext = {
    available: !!BrainAI,
    memorySystem: BrainAI ? new BrainAI.MemorySystem() : null,
    learningEngine: BrainAI ? new BrainAI.LearningEngine() : null,
    reasoningEngine: BrainAI ? new BrainAI.ReasoningEngine() : null
};
"""
        
        student_code = request.code
        
        wrapped_code = f"""
// Code execution started at {datetime.utcnow().isoformat()}
const startTime = Date.now();

{brain_ai_integration}

// Student Code Below:
// ====================
{student_code}
// ====================

// Code execution completed
const endTime = Date.now();
const executionTime = (endTime - startTime) / 1000;

console.log(`\\nExecution completed in {{executionTime.toFixed(3)}} seconds`);
console.log('Memory usage:', process.memoryUsage().heapUsed / 1024 / 1024, 'MB');

"""
        return wrapped_code
    
    async def _update_lesson_progress(self, user_id: int, lesson_id: int, db: Session):
        """Update progress when user runs code"""
        try:
            # Get or create progress record
            progress = db.query(Progress).filter(
                Progress.user_id == user_id,
                Progress.lesson_id == lesson_id
            ).first()
            
            if not progress:
                progress = Progress(
                    user_id=user_id,
                    lesson_id=lesson_id,
                    status="in_progress",
                    progress_percentage=25.0
                )
                db.add(progress)
            else:
                # Update progress based on activity
                current_progress = progress.progress_percentage
                progress.progress_percentage = min(current_progress + 10.0, 100.0)
                if progress.progress_percentage >= 100.0:
                    progress.status = "completed"
                    progress.completion_date = datetime.utcnow()
                else:
                    progress.status = "in_progress"
                
                progress.last_accessed = datetime.utcnow()
            
            db.commit()
            
        except Exception as e:
            logger.error(f"Error updating lesson progress: {e}")
            db.rollback()
    
    async def _store_execution_history(self, request: CodeExecutionRequest, result: CodeExecutionResult, db: Session):
        """Store execution history for analytics"""
        try:
            # Store execution record for analytics and history
            # This would be implemented with a dedicated ExecutionHistory model
            logger.info(f"Code execution completed: {result.execution_id} in {result.execution_time:.3f}s")
            
        except Exception as e:
            logger.error(f"Error storing execution history: {e}")
    
    def _get_memory_usage(self) -> int:
        """Get current memory usage in MB"""
        try:
            import psutil
            process = psutil.Process()
            return int(process.memory_info().rss / 1024 / 1024)
        except:
            return 0
    
    async def handle_websocket_connection(self, websocket: WebSocket, user_id: int):
        """Handle WebSocket connection for real-time code execution"""
        await websocket.accept()
        
        try:
            while True:
                # Receive code execution request
                data = await websocket.receive_json()
                
                if data.get("type") == "execute_code":
                    # Parse execution request
                    request = CodeExecutionRequest(
                        code=data["code"],
                        language=ExecutionLanguage(data["language"]),
                        lesson_id=data["lesson_id"],
                        user_id=user_id,
                        dependencies=data.get("dependencies", []),
                        timeout=data.get("timeout", 30),
                        memory_limit=data.get("memory_limit", 256),
                        cpu_limit=data.get("cpu_limit", 1.0)
                    )
                    
                    # Execute code
                    result = await self.execute_code(request, websocket, None)  # db would be passed here
                    
                elif data.get("type") == "get_brain_ai_examples":
                    # Send available Brain AI examples for this lesson
                    examples = await self._get_brain_ai_examples_for_lesson(data["lesson_id"])
                    await websocket.send_json({
                        "type": "brain_ai_examples",
                        "examples": examples
                    })
                
        except WebSocketDisconnect:
            logger.info(f"WebSocket disconnected for user {user_id}")
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
            await websocket.close()
    
    async def _get_brain_ai_examples_for_lesson(self, lesson_id: int) -> List[Dict[str, Any]]:
        """Get Brain AI examples available for a specific lesson"""
        # This would integrate with the Brain AI framework
        examples = [
            {
                "id": "memory_example_001",
                "name": "Basic Memory System",
                "description": "Create a simple memory system using vectors",
                "code": """
from brain_ai import MemorySystem

# Initialize memory system
memory = MemorySystem()

# Add some memories
memory.add_memory("Learning Python basics", "I learned about variables and functions")
memory.add_memory("AI concepts", "Neural networks mimic brain structure")

# Query similar memories
similar = memory.query("learning")
print("Similar memories:", similar)
""",
                "language": "python",
                "difficulty": "beginner"
            },
            {
                "id": "learning_example_001",
                "name": "Simple Learning Algorithm",
                "description": "Implement basic incremental learning",
                "code": """
from brain_ai import LearningEngine

# Initialize learning engine
learning = LearningEngine()

# Train on some data
training_data = [
    {"input": "hello", "output": "greeting"},
    {"input": "hi", "output": "greeting"},
    {"input": "bye", "output": "farewell"}
]

for item in training_data:
    learning.train(item["input"], item["output"])

# Test learning
result = learning.predict("good morning")
print("Prediction:", result)
""",
                "language": "python",
                "difficulty": "intermediate"
            }
        ]
        
        return examples

# Global instance
code_execution_manager = CodeExecutionManager()