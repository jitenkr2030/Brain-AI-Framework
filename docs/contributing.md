# Contributing Guide

Welcome to the Brain AI Framework project! This guide will help you understand how to contribute effectively to our open-source community.

## 📋 Table of Contents

- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Contribution Types](#contribution-types)
- [Code Standards](#code-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)
- [Pull Request Process](#pull-request-process)
- [Community Guidelines](#community-guidelines)
- [Release Process](#release-process)
- [Recognition](#recognition)

## 🚀 Getting Started

Thank you for your interest in contributing to Brain AI! We're excited to have you join our community of developers working on revolutionary brain-inspired AI technology.

### Why Contribute?

- **Impact**: Your contributions will help shape the future of AI technology
- **Learning**: Work with cutting-edge AI concepts and algorithms
- **Community**: Join a passionate community of AI researchers and developers
- **Recognition**: Get acknowledged in our contributors hall of fame
- **Career**: Build your portfolio with open-source contributions

### Ways to Contribute

- **Code Contributions**: Bug fixes, new features, performance improvements
- **Documentation**: Improve guides, examples, and API documentation
- **Testing**: Write tests, report bugs, verify fixes
- **Design**: UI/UX improvements, architecture design
- **Community**: Help other users, moderate forums, organize events

## ⚙️ Development Setup

### Prerequisites

Before you start contributing, make sure you have:

- **Git**: Version control system
- **Python 3.8+**: For core framework development
- **Node.js 14+**: For JavaScript SDK development
- **Java 8+**: For Java SDK development
- **Docker**: For containerized development
- **Code Editor**: VS Code, PyCharm, or your preferred editor

### Fork and Clone

1. **Fork the repository**:
   ```bash
   # Visit https://github.com/brain-ai/framework
   # Click "Fork" button
   ```

2. **Clone your fork**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/framework.git
   cd framework
   ```

3. **Add upstream remote**:
   ```bash
   git remote add upstream https://github.com/brain-ai/framework.git
   ```

### Environment Setup

1. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

2. **Install Node.js dependencies**:
   ```bash
   npm install
   ```

3. **Set up pre-commit hooks**:
   ```bash
   pre-commit install
   ```

4. **Run tests to verify setup**:
   ```bash
   python -m pytest tests/
   npm test
   ```

### Development Workflow

```bash
# Create a new branch for your feature
git checkout -b feature/your-feature-name

# Make your changes
# ... edit files ...

# Run tests
python -m pytest tests/

# Commit your changes
git add .
git commit -m "feat: add your feature description"

# Push to your fork
git push origin feature/your-feature-name

# Create a pull request on GitHub
```

## 🤝 Contribution Types

### 🐛 Bug Fixes

Bug fixes are always welcome! When reporting or fixing bugs:

**Bug Report Template**:
```markdown
## Bug Description
A clear description of the bug

## Environment
- Brain AI Framework version: [e.g., 1.0.0]
- Programming language: [e.g., Python 3.11]
- Operating System: [e.g., Ubuntu 22.04]

## Steps to Reproduce
1. Step one
2. Step two
3. See error

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Error Messages
Complete error message and stack trace

## Additional Context
Screenshots, code examples, etc.
```

**Fix Example**:
```python
# Before (buggy code)
def store_memory(content, type, metadata=None):
    if not content:
        raise ValueError("Content is required")  # Bug: no validation
    return memory_id

# After (fixed code)
def store_memory(content, type, metadata=None):
    if not content:
        raise ValueError("Content is required")
    
    if not isinstance(content, (dict, str, list)):
        raise ValueError("Content must be dict, str, or list")  # Bug fix
    
    return memory_id
```

### ✨ New Features

When proposing new features, consider:

**Feature Request Template**:
```markdown
## Feature Description
A clear description of the feature

## Problem Statement
What problem does this solve?

## Proposed Solution
How would you implement this?

## Alternative Solutions
What other approaches did you consider?

## Additional Context
Screenshots, mockups, or examples
```

**Feature Implementation Example**:
```python
# New feature: Batch memory operations
class BatchMemoryOperations:
    def __init__(self, sdk: BrainAISDK):
        self.sdk = sdk
    
    async def store_memories_batch(self, memories: List[Dict]) -> List[str]:
        """Store multiple memories in a single operation"""
        if len(memories) > 100:
            raise ValueError("Maximum 100 memories per batch")
        
        tasks = [
            self.sdk.store_memory(**memory) 
            for memory in memories
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and return valid IDs
        return [r for r in results if isinstance(r, str)]
```

### 📚 Documentation Improvements

Documentation is crucial for adoption! Help us improve:

- **API Documentation**: Add missing parameters, examples
- **Tutorial Guides**: Create step-by-step tutorials
- **Code Examples**: Add practical use cases
- **Troubleshooting**: Document common issues and solutions

**Documentation Example**:
```markdown
## Memory Storage

Store different types of memories in the brain:

```python
# Episodic memory - specific events
await sdk.store_memory(
    content="I met Alice at the conference yesterday",
    type="episodic",
    metadata={"importance": 0.8}
)

# Semantic memory - general knowledge
await sdk.store_memory(
    content="Python is a programming language created by Guido van Rossum",
    type="semantic"
)

# Procedural memory - how-to knowledge
await sdk.store_memory(
    content="To install Python: pip install python",
    type="procedural"
)
```

**Parameters:**
- `content`: The content to store (dict, str, or list)
- `type`: Memory type ('episodic', 'semantic', 'procedural', 'emotional')
- `metadata`: Optional metadata dictionary
```

### 🧪 Testing Contributions

Help us maintain high code quality by:

**Test Example**:
```python
# tests/test_memory_operations.py
import pytest
from brain_ai import BrainAISDK, BrainAIConfig

@pytest.mark.asyncio
async def test_store_memory_validation():
    """Test memory storage validation"""
    config = BrainAIConfig("http://localhost:8000")
    sdk = BrainAISDK(config)
    
    # Test invalid content types
    with pytest.raises(ValueError):
        await sdk.store_memory(None, "semantic")
    
    with pytest.raises(ValueError):
        await sdk.store_memory(123, "semantic")
    
    # Test valid content types
    result = await sdk.store_memory("test content", "semantic")
    assert isinstance(result, str)
    assert len(result) > 0

@pytest.mark.asyncio
async def test_batch_memory_operations():
    """Test batch memory operations"""
    config = BrainAIConfig("http://localhost:8000")
    sdk = BrainAISDK(config)
    
    batch_ops = BatchMemoryOperations(sdk)
    memories = [
        {"content": f"Memory {i}", "type": "semantic"}
        for i in range(5)
    ]
    
    result = await batch_ops.store_memories_batch(memories)
    assert len(result) == 5
    assert all(isinstance(id, str) for id in result)
```

## 📏 Code Standards

### Python Style Guide

We follow **PEP 8** with some additional guidelines:

```python
# Good Python code style
import asyncio
from typing import List, Dict, Optional, Union
from brain_ai import BrainAISDK, BrainAIConfig

class MemoryManager:
    """Manages memory operations for Brain AI."""
    
    def __init__(self, config: BrainAIConfig) -> None:
        self.config = config
        self.sdk = BrainAISDK(config)
    
    async def store_memory(
        self,
        content: Union[str, Dict, List],
        memory_type: str,
        metadata: Optional[Dict] = None
    ) -> str:
        """
        Store a memory in the brain.
        
        Args:
            content: The content to store
            memory_type: Type of memory ('episodic', 'semantic', etc.)
            metadata: Optional metadata dictionary
            
        Returns:
            Memory ID string
            
        Raises:
            ValueError: If content is invalid
            ConnectionError: If unable to connect to Brain AI server
        """
        if not content:
            raise ValueError("Content cannot be empty")
        
        if memory_type not in ['episodic', 'semantic', 'procedural', 'emotional']:
            raise ValueError(f"Invalid memory type: {memory_type}")
        
        memory_data = {
            'content': content,
            'type': memory_type,
            'metadata': metadata or {},
            'timestamp': asyncio.get_event_loop().time()
        }
        
        return await self.sdk.store_memory(**memory_data)
```

### JavaScript Style Guide

```javascript
// Good JavaScript code style
import { BrainAISDK, BrainAIConfig } from 'brain-ai-sdk';

/**
 * Memory manager for Brain AI operations
 */
class MemoryManager {
    /**
     * @param {BrainAIConfig} config - Brain AI configuration
     */
    constructor(config) {
        this.config = config;
        this.sdk = new BrainAISDK(config);
    }

    /**
     * Store a memory in the brain
     * @param {string|Object|Array} content - The content to store
     * @param {string} memoryType - Type of memory
     * @param {Object} metadata - Optional metadata
     * @returns {Promise<string>} Memory ID
     * @throws {Error} If content is invalid
     */
    async storeMemory(content, memoryType, metadata = {}) {
        if (!content) {
            throw new Error('Content cannot be empty');
        }

        const validTypes = ['episodic', 'semantic', 'procedural', 'emotional'];
        if (!validTypes.includes(memoryType)) {
            throw new Error(`Invalid memory type: ${memoryType}`);
        }

        const memoryData = {
            content,
            type: memoryType,
            metadata,
            timestamp: Date.now()
        };

        return await this.sdk.storeMemory(memoryData);
    }
}

export default MemoryManager;
```

### Java Style Guide

```java
// Good Java code style
package com.brainai.sdk;

import java.util.concurrent.CompletableFuture;
import java.util.List;
import java.util.Map;

/**
 * Manages memory operations for Brain AI.
 */
public class MemoryManager {
    private final BrainAIConfig config;
    private final BrainAISDK sdk;

    /**
     * Constructs a new MemoryManager.
     * @param config Brain AI configuration
     */
    public MemoryManager(BrainAIConfig config) {
        this.config = config;
        this.sdk = new BrainAISDK(config);
    }

    /**
     * Store a memory in the brain.
     * @param content The content to store
     * @param memoryType Type of memory
     * @param metadata Optional metadata
     * @return CompletableFuture with memory ID
     * @throws IllegalArgumentException if content is invalid
     */
    public CompletableFuture<String> storeMemory(
            Object content, 
            String memoryType, 
            Map<String, Object> metadata) {
        
        if (content == null || content.toString().trim().isEmpty()) {
            throw new IllegalArgumentException("Content cannot be empty");
        }

        List<String> validTypes = List.of("episodic", "semantic", "procedural", "emotional");
        if (!validTypes.contains(memoryType)) {
            throw new IllegalArgumentException("Invalid memory type: " + memoryType);
        }

        Map<String, Object> memoryData = Map.of(
            "content", content,
            "type", memoryType,
            "metadata", metadata != null ? metadata : Map.of(),
            "timestamp", System.currentTimeMillis()
        );

        return sdk.storeMemory(memoryData, MemoryType.valueOf(memoryType.toUpperCase()), metadata);
    }
}
```

### General Guidelines

1. **Use Type Hints** (Python) or **JSDoc** (JavaScript):
   ```python
   def process_data(data: List[Dict], filter_func: Callable[[Dict], bool]) -> List[Dict]:
       return [item for item in data if filter_func(item)]
   ```

2. **Write Descriptive Docstrings**:
   ```python
   def search_memories(query: str, limit: int = 10) -> List[SearchResult]:
       """
       Search for memories similar to the query.
       
       Args:
           query: Search query string
           limit: Maximum number of results (default: 10)
           
       Returns:
           List of SearchResult objects ordered by relevance
           
       Raises:
           ValueError: If query is empty or limit is invalid
       """
   ```

3. **Use Meaningful Variable Names**:
   ```python
   # Bad
   d = search_memories(q, 5)
   
   # Good
   search_results = search_memories(query="machine learning", limit=5)
   ```

4. **Handle Errors Gracefully**:
   ```python
   async def safe_memory_operation(func, *args, **kwargs):
       try:
           return await func(*args, **kwargs)
       except ConnectionError:
           logger.error("Failed to connect to Brain AI server")
           return None
       except ValueError as e:
           logger.warning(f"Invalid input: {e}")
           return None
   ```

## 🧪 Testing Guidelines

### Test Structure

Follow the **Arrange-Act-Assert** pattern:

```python
@pytest.mark.asyncio
async def test_search_memories_functionality():
    """Test search memories with various scenarios."""
    # Arrange
    config = BrainAIConfig("http://localhost:8000")
    sdk = BrainAISDK(config)
    
    # Add test data
    await sdk.store_memory("test query", "semantic")
    await sdk.store_memory("different content", "episodic")
    
    # Act
    results = await sdk.search_memories("test", limit=10)
    
    # Assert
    assert len(results) >= 1
    assert any("test query" in str(result.content) for result in results)
```

### Test Coverage

Aim for high test coverage:

```bash
# Run tests with coverage
pytest --cov=brain_ai tests/ --cov-report=html

# Check coverage report
open htmlcov/index.html
```

### Mock Testing

Use mocking for external dependencies:

```python
from unittest.mock import AsyncMock, patch

@patch('brain_ai.core.memory.requests.get')
async def test_offline_memory_search(mock_get):
    """Test memory search when server is offline."""
    mock_get.side_effect = ConnectionError("Server unavailable")
    
    config = BrainAIConfig("http://localhost:8000")
    sdk = BrainAISDK(config)
    
    # Should return empty results when offline
    results = await sdk.search_memories("test", limit=5)
    assert len(results) == 0
```

## 📖 Documentation

### Code Documentation

- **Classes**: Document purpose, key methods, usage examples
- **Functions**: Document parameters, return values, exceptions, examples
- **Complex Logic**: Add inline comments for complex algorithms

### API Documentation

Update API docs when adding new features:

```markdown
## SDK.store_memory()

Store a memory in the brain.

### Parameters

- `content` (Union[str, Dict, List]): The content to store
- `memory_type` (str): Type of memory ('episodic', 'semantic', 'procedural', 'emotional')
- `metadata` (Dict, optional): Additional metadata

### Returns

- `str`: Memory ID

### Examples

```python
# Store a simple memory
memory_id = await sdk.store_memory("Hello World", "semantic")

# Store with metadata
memory_id = await sdk.store_memory(
    content={"title": "Important Note", "text": "Remember this"},
    type="semantic",
    metadata={"importance": 0.9, "tags": ["note", "important"]}
)
```

### Tutorial Documentation

Create step-by-step tutorials:

```markdown
# Building Your First Brain AI Application

## Prerequisites
- Python 3.8+
- Brain AI SDK installed

## Step 1: Setup
Install the SDK and create your first app:

```bash
pip install brain-ai-sdk
```

## Step 2: Create the Application

```python
from brain_ai import BrainAISDK, BrainAIConfig

# Configure the SDK
config = BrainAIConfig("http://localhost:8000")
sdk = BrainAISDK(config)

# Store your first memory
memory_id = await sdk.store_memory(
    content="My first Brain AI memory!",
    type="semantic"
)

print(f"Stored memory with ID: {memory_id}")
```

## Step 3: Run Your Application

```bash
python my_first_app.py
```

## Next Steps
- [Learn about memory types](memory-types.md)
- [Explore search functionality](searching-memories.md)
- [Build advanced applications](advanced-examples.md)
```
```

## 🔄 Pull Request Process

### Before Submitting

1. **Run Tests**: Ensure all tests pass
2. **Update Documentation**: Update relevant docs
3. **Check Style**: Run linting tools
4. **Test Thoroughly**: Test your changes locally

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] Tests pass locally
- [ ] Added tests for new functionality
- [ ] Manual testing completed

## Checklist
- [ ] My code follows the style guidelines
- [ ] I have performed a self-review of my code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes

## Screenshots (if applicable)
Add screenshots for UI changes

## Additional Notes
Any additional information for reviewers
```

### Review Process

1. **Automated Checks**: CI/CD pipeline runs tests and linting
2. **Code Review**: Maintainers review code quality and logic
3. **Testing**: Changes are tested in staging environment
4. **Documentation**: Documentation is reviewed and updated
5. **Merge**: Changes are merged once approved

### Commit Messages

Use conventional commits:

```bash
# Feature additions
git commit -m "feat: add batch memory operations"

# Bug fixes
git commit -m "fix: resolve memory leak in search function"

# Documentation
git commit -m "docs: add getting started tutorial"

# Tests
git commit -m "test: add unit tests for memory manager"

# Refactoring
git commit -m "refactor: simplify memory validation logic"

# Performance
git commit -m "perf: optimize vector similarity search"
```

## 👥 Community Guidelines

### Code of Conduct

We are committed to providing a welcoming and inclusive environment:

- **Be Respectful**: Treat all community members with respect
- **Be Inclusive**: Welcome people of all backgrounds and experience levels
- **Be Constructive**: Provide helpful feedback and suggestions
- **Be Patient**: Help newcomers learn and grow
- **Be Professional**: Maintain professional communication

### Communication Channels

- **GitHub Discussions**: General questions and feature discussions
- **GitHub Issues**: Bug reports and feature requests
- **Discord**: Real-time chat and community support
- **Email**: Direct communication with maintainers

### Getting Help

1. **Check Documentation**: Look for answers in docs and guides
2. **Search Issues**: Check existing GitHub issues
3. **Ask Questions**: Use GitHub Discussions for questions
4. **Join Discord**: Get real-time help from community
5. **Contact Maintainers**: Email for private or urgent matters

## 🚀 Release Process

### Version Numbering

We follow [Semantic Versioning](https://semver.org/):

- **Major** (X.0.0): Breaking changes
- **Minor** (0.X.0): New features, backward compatible
- **Patch** (0.0.X): Bug fixes, backward compatible

### Release Checklist

Before each release:

- [ ] All tests pass
- [ ] Documentation is updated
- [ ] CHANGELOG.md is updated
- [ ] Version numbers are bumped
- [ ] Release notes are prepared
- [ ] Git tags are created
- [ ] PyPI packages are published
- [ ] NPM packages are published
- [ ] Docker images are built
- [ ] Announcement is posted

### Release Notes Template

```markdown
# Brain AI Framework v1.2.0

## 🎉 New Features
- **Batch Operations**: Process multiple memories in a single request
- **Enhanced Search**: Improved similarity algorithms with better performance
- **Graph Visualization**: Visualize knowledge graphs with new UI components

## 🐛 Bug Fixes
- Fixed memory leak in vector search operations
- Resolved timeout issues in high-load scenarios
- Corrected error handling in network failures

## 📚 Documentation
- Added comprehensive getting started guide
- Updated API reference with new parameters
- Created video tutorials for common use cases

## 🔧 Improvements
- 30% performance improvement in memory storage
- Reduced memory footprint by 20%
- Better error messages and debugging info

## 📦 Breaking Changes
- Renamed `search_memories` parameter `max_results` to `limit`
- Changed default similarity threshold from 0.8 to 0.7

## 🙏 Contributors
Thanks to all contributors who made this release possible!

- @alice贡献者 - Batch operations feature
- @bob开发者 - Performance optimizations
- @charlie文档员 - Documentation improvements

## 🚀 Upgrade Guide
To upgrade from v1.1.0:

```bash
pip install --upgrade brain-ai-sdk
```

See [UPGRADE.md](UPGRADE.md) for detailed migration instructions.
```

## 🏆 Recognition

### Contributors Hall of Fame

We maintain a contributors page recognizing outstanding contributions:

```markdown
# 🏆 Brain AI Contributors Hall of Fame

## Core Contributors
- **@alice核心开发者**: Lead architect, implemented core memory system
- **@bob性能优化师**: Optimized vector operations, 300% performance improvement
- **@charlie文档专家**: Created comprehensive documentation suite

## Feature Contributors
- **@david批量处理**: Implemented batch memory operations
- **@eve图可视化**: Built knowledge graph visualization tools
- **@frank测试大师**: Achieved 95% test coverage

## Community Contributors
- **@grace支持专家**: Helped 100+ users in Discord
- **@henry翻译官**: Translated documentation to 5 languages
- **@iris设计师**: Created beautiful UI components

## Special Recognition
- **🏅 MVP Award**: @alice for outstanding leadership
- **🚀 Innovation Award**: @bob for breakthrough algorithms
- **❤️ Community Award**: @grace for exceptional support
```

### Contribution Levels

- **Bronze** 🏅: 1-5 contributions
- **Silver** 🥈: 6-20 contributions
- **Gold** 🥇: 21-50 contributions
- **Platinum** 💎: 51+ contributions
- **Legend** ⭐: Exceptional ongoing contributions

### Rewards

Top contributors may receive:

- **Swag**: Branded t-shirts, stickers, mugs
- **Early Access**: Beta features before public release
- **Speaking Opportunities**: Conference talks about Brain AI
- **Job Referrals**: Priority consideration for positions
- **Trophy**: Physical trophy for hall of fame members

## 📝 Final Notes

Thank you for contributing to Brain AI! Your efforts help make this project better for everyone. Whether you're fixing a small typo or implementing a major feature, every contribution is valuable and appreciated.

### Resources

- [GitHub Repository](https://github.com/brain-ai/framework)
- [Documentation](https://docs.brain-ai.com)
- [Discord Community](https://discord.gg/brain-ai)
- [Email Support](mailto:contributors@brain-ai.com)

### Questions?

If you have questions about contributing, don't hesitate to:

1. Check existing documentation and issues
2. Ask in GitHub Discussions
3. Join our Discord server
4. Contact the maintainers directly

We're here to help you succeed in your contribution journey!

---

*Built with ❤️ by the Brain AI Team*