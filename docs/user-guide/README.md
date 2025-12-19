# 🧠 Brain-Inspired AI Framework

> An AI system that learns continuously, remembers permanently, and reasons without retraining.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🌟 Overview

The Brain-Inspired AI Framework is a production-grade, scalable AI system that emulates key principles of biological intelligence:

- **🧠 Persistent Memory**: Experiences are stored permanently and strengthen with use
- **🔄 Incremental Learning**: Continuous learning without retraining cycles
- **⚡ Sparse Activation**: Only relevant memories activate at any time
- **🎯 Reasoning Separation**: Thinking doesn't rewrite stored knowledge
- **🔁 Feedback Loop**: Experience drives memory strengthening/weakening

## 🎯 Key Principles

Unlike traditional AI that follows "Collect data → Train model → Freeze → Replace later", our framework operates on:

```
Experience → Memory → Local learning → Adaptation (forever)
```

### Core Rules:
- ❌ No repeated full retraining
- ❌ No "stateless intelligence"
- ✅ Persistent memory across sessions
- ✅ Incremental learning from feedback
- ✅ Reasoning separated from learning

## 🏗️ Architecture

```
┌────────────┐
│   Input    │  (events, signals, observations)
└─────┬──────┘
      ↓
┌────────────┐
│  Encoder   │  (pattern extraction)
└─────┬──────┘
      ↓
┌────────────┐
│  Memory    │◄────┐
└─────┬──────┘     │
      ↓            │
┌────────────┐     │
│  Learning  │─────┘
└─────┬──────┘
      ↓
┌────────────┐
│ Reasoning  │  (LLM / logic)
└─────┬──────┘
      ↓
┌────────────┐
│   Output   │
└─────┬──────┘
      ↓
┌────────────┐
│  Feedback  │ ───► Memory update
└────────────┘
```

## 📁 Project Structure

```
brain_ai/
├── app/
│   ├── main.py              # Application entry point
│   ├── config.py            # Configuration management
│   └── lifecycle.py         # Startup / shutdown logic
├── core/
│   ├── encoder.py           # Pattern & event encoding
│   ├── memory.py            # Long-term memory system
│   ├── learning.py          # Incremental learning rules
│   ├── routing.py           # Sparse activation logic
│   ├── reasoning.py         # Reasoning engine (LLM / rules)
│   └── feedback.py          # Experience processing
├── storage/
│   ├── key_value.py         # Simple persistent memory
│   ├── vector.py            # Semantic / similarity memory
│   ├── graph.py             # Associative memory
│   └── persistence.py       # DB abstraction layer
├── api/
│   ├── routes.py            # API endpoints
│   └── schemas.py           # Input / output contracts
├── services/
│   ├── ingestion.py         # Event ingestion
│   ├── scheduler.py         # Periodic learning loops
│   └── monitoring.py        # Logs, metrics, health checks
├── tests/
│   └── test_core_logic.py   # Core component tests
└── requirements.txt
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- SQLite (included with Python)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd brain_ai
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python app/main.py
   ```

5. **Access the API**
   - API Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/api/v1/health
   - System Status: http://localhost:8000/api/v1/status

## 💻 Usage Examples

### Basic Processing

```python
import asyncio
from app.lifecycle import get_brain_system

async def main():
    brain_system = get_brain_system()
    
    # Process input through the brain system
    result = await brain_system.process_input({
        "user_action": "click",
        "element": "submit_button",
        "session_id": "user123",
        "timestamp": "2025-12-18T22:54:22Z"
    })
    
    print(f"Processed {len(result['active_memories'])} active memories")
    print(f"Reasoning result: {result['reasoning_result']['result']}")

asyncio.run(main())
```

### Providing Feedback

```python
# Strengthen memory based on positive feedback
await brain_system.process_feedback(
    memory_id="memory_123",
    feedback_type="positive",
    outcome={
        "user_satisfaction": 0.9,
        "reward": 1.0,
        "confidence": 0.8
    }
)
```

### Getting Explanations

```python
# Explain a decision using memory
explanation = await brain_system.reasoning_engine.explain(
    decision="approve_action",
    active_memories=active_memories,
    context={
        "user_history": "positive",
        "risk_level": "low"
    }
)

print(f"Explanation: {explanation['explanation']}")
```

### Making Predictions

```python
# Predict future outcomes
prediction = await brain_system.reasoning_engine.predict(
    current_situation={"status": "stable", "trend": "positive"},
    active_memories=memories,
    time_horizon="near_term"
)

print(f"Prediction: {prediction['prediction']}")
```

## 🔧 API Endpoints

### Core Operations

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/process` | POST | Process input through brain pipeline |
| `/api/v1/feedback` | POST | Provide feedback to update memory |
| `/api/v1/explain` | POST | Get explanation for decisions |
| `/api/v1/predict` | POST | Make predictions based on memories |
| `/api/v1/plan` | POST | Create action plans |

### System Operations

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/status` | GET | Get system status and statistics |
| `/api/v1/health` | GET | Health check endpoint |
| `/api/v1/memories` | GET | List current memories |
| `/api/v1/test` | POST | Run system test |
| `/metrics` | GET | Prometheus metrics |

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=false
WORKERS=4

# Database Configuration
DATABASE_URL=sqlite:///./brain_ai.db
REDIS_URL=redis://localhost:6379/0

# AI & LLM Configuration
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-3.5-turbo
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Memory System Configuration
MEMORY_RETENTION_DAYS=365
MEMORY_MAX_SIZE=100000
MEMORY_SIMILARITY_THRESHOLD=0.7

# Learning Configuration
LEARNING_RATE=0.01
MIN_ACTIVATION_STRENGTH=0.1
FORGETTING_RATE=0.001

# Monitoring Configuration
ENABLE_METRICS=true
METRICS_PORT=9090
LOG_LEVEL=INFO
```

### Key Configuration Options

| Parameter | Description | Default |
|-----------|-------------|---------|
| `LEARNING_RATE` | Rate of memory strength updates | 0.01 |
| `MEMORY_SIMILARITY_THRESHOLD` | Threshold for memory retrieval | 0.7 |
| `MAX_ACTIVE_MEMORIES` | Maximum memories to activate | 10 |
| `TARGET_SPARSITY` | Target percentage of active memories | 0.05 |

## 🧪 Testing

### Run Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_core_logic.py

# Run with coverage
pytest --cov=core tests/

# Run in verbose mode
pytest -v tests/
```

### Test Structure

- **Unit Tests**: Individual component testing
- **Integration Tests**: Component interaction testing
- **API Tests**: Endpoint testing with FastAPI TestClient
- **Performance Tests**: Memory and speed benchmarking

## 📊 Monitoring & Metrics

### Built-in Metrics

The framework provides comprehensive metrics via `/metrics`:

```
# System Metrics
system_cpu_usage_percent
system_memory_usage_bytes
system_disk_usage_bytes

# Application Metrics
app_requests_total
app_requests_errors
app_request_duration_seconds

# Brain-specific Metrics
brain_memories_total
brain_learning_updates_total
brain_reasoning_requests_total
brain_activation_active_memories
```

### Health Checks

- **Database Health**: SQLite connectivity and table existence
- **Memory Store**: Memory count and access patterns
- **Service Status**: Background service health
- **System Resources**: CPU, memory, disk usage

## 🔄 Background Services

### Scheduler Tasks

| Task | Interval | Description |
|------|----------|-------------|
| Memory Consolidation | 1h | Apply time decay and optimize storage |
| System Health Check | 15m | Monitor system and component health |
| Data Cleanup | 1d | Remove old logs and temporary data |
| Performance Optimization | 6h | Optimize indices and parameters |
| Learning Updates | 30m | Process pending learning updates |

### Custom Tasks

```python
from services.scheduler import Scheduler

# Add custom scheduled task
scheduler.add_task(
    name="custom_analysis",
    function=my_analysis_function,
    interval="2h"
)
```

## 🛠️ Development

### Setup Development Environment

```bash
# Install development dependencies
pip install -r requirements.txt
pip install black isort mypy pytest-asyncio

# Setup pre-commit hooks
pre-commit install
```

### Code Style

```bash
# Format code
black brain_ai/
isort brain_ai/

# Type checking
mypy brain_ai/

# Linting
flake8 brain_ai/
```

### Adding New Components

1. **Create component** in appropriate module
2. **Add tests** in `tests/` directory
3. **Update API routes** if needed
4. **Add configuration** options
5. **Update documentation**

## 🎯 Use Cases

This framework is ideal for:

- **🤖 Adaptive Assistants**: Personal AI that learns user preferences
- **📊 Monitoring Systems**: Self-improving anomaly detection
- **🔍 Knowledge Engines**: Systems that accumulate domain expertise
- **⚡ Autonomous Workflows**: Self-optimizing process management
- **🎮 Adaptive Gaming**: NPCs that learn player behavior
- **💡 Decision Support**: Systems that improve decision quality over time

## 📈 Performance Characteristics

- **Memory Efficiency**: Sparse activation limits active memory to ~5%
- **Scalability**: Horizontal scaling through stateless APIs
- **Latency**: Sub-100ms response times for most operations
- **Throughput**: 100+ concurrent requests supported
- **Storage**: SQLite with optional PostgreSQL/MySQL backends

## 🛡️ Security Features

- **API Key Authentication**: Optional API key protection
- **Input Validation**: Pydantic-based request validation
- **Rate Limiting**: Configurable request rate limits
- **Data Encryption**: At-rest encryption for sensitive data
- **Audit Logging**: Comprehensive event logging

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guidelines
- Write comprehensive tests
- Update documentation
- Use type hints
- Add error handling
- Include logging

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [Project Wiki](link-to-wiki)
- **Issues**: [GitHub Issues](link-to-issues)
- **Discussions**: [GitHub Discussions](link-to-discussions)
- **Email**: support@brainai.dev

## 🙏 Acknowledgments

- Inspired by neuroscience research on memory consolidation
- Built on modern Python ecosystem (FastAPI, SQLAlchemy, etc.)
- Influenced by sparse coding and competitive neural networks

---

**🧠 "If an AI must be retrained to learn, it is not brain-inspired."**

*The Brain-Inspired AI Framework - Where Intelligence Lives Forever*