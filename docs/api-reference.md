# API Reference

Complete API documentation for the Brain AI Framework across all supported programming languages.

## 📋 Table of Contents

- [Overview](#overview)
- [Core Methods](#core-methods)
- [Memory Management](#memory-management)
- [Learning System](#learning-system)
- [Reasoning Engine](#reasoning-engine)
- [Vector Operations](#vector-operations)
- [Graph Knowledge](#graph-knowledge)
- [System Management](#system-management)
- [Utility Methods](#utility-methods)
- [Language-Specific APIs](#language-specific-apis)

## 🔍 Overview

The Brain AI Framework provides a unified API across all programming languages. Each SDK implements the same core functionality with language-specific idioms and patterns.

### Base Configuration
All SDKs share a common configuration structure:

```python
# Configuration parameters
config = {
    "base_url": "http://localhost:8000",        # Brain AI server URL
    "api_key": "your-api-key",                  # Authentication key
    "timeout": 30000,                           # Request timeout (ms)
    "memory_size": 10000,                       # Maximum memory entries
    "learning_rate": 0.1,                       # Learning rate (0.0-1.0)
    "similarity_threshold": 0.7,                # Similarity threshold (0.0-1.0)
    "max_reasoning_depth": 5                    # Maximum reasoning depth
}
```

### Memory Types
Brain AI supports four types of memory:

| Type | Description | Use Case |
|------|-------------|----------|
| `episodic` | Specific experiences and events | Personal memories, event logs |
| `semantic` | General knowledge and facts | Facts, concepts, definitions |
| `procedural` | Skills and processes | How-to knowledge, procedures |
| `emotional` | Preferences and associations | User preferences, emotional responses |

### Response Formats
All API methods return consistent response formats:

```json
{
    "success": true,
    "data": {...},
    "timestamp": 1640995200000,
    "execution_time": 45
}
```

## 🧠 Core Methods

### `store_memory(content, type, metadata)`

Stores a new memory in the brain.

**Parameters:**
- `content` (any): The content to store
- `type` (string): Memory type ('episodic', 'semantic', 'procedural', 'emotional')
- `metadata` (dict): Additional metadata for organization

**Returns:** Memory ID string

**Example:**
```python
# Python
memory_id = await sdk.store_memory(
    content={
        "title": "Important Meeting",
        "date": "2025-01-15",
        "attendees": ["Alice", "Bob"],
        "summary": "Discussed Q1 strategy"
    },
    type="episodic",
    metadata={
        "importance": 0.9,
        "tags": ["meeting", "strategy", "business"],
        "source": "calendar"
    }
)
```

```javascript
// JavaScript
const memoryId = await sdk.storeMemory(
    {
        title: "Important Meeting",
        date: "2025-01-15",
        attendees: ["Alice", "Bob"],
        summary: "Discussed Q1 strategy"
    },
    'episodic',
    {
        importance: 0.9,
        tags: ["meeting", "strategy", "business"],
        source: "calendar"
    }
);
```

```java
// Java
CompletableFuture<String> memoryId = sdk.storeMemory(
    Map.of(
        "title", "Important Meeting",
        "date", "2025-01-15",
        "attendees", List.of("Alice", "Bob"),
        "summary", "Discussed Q1 strategy"
    ),
    MemoryType.EPISODIC,
    Map.of(
        "importance", 0.9,
        "tags", List.of("meeting", "strategy", "business"),
        "source", "calendar"
    )
);
```

### `get_memory(id)`

Retrieves a memory by its ID.

**Parameters:**
- `id` (string): Memory ID

**Returns:** Memory object or None

**Example:**
```python
memory = await sdk.get_memory(memory_id)
if memory:
    print(f"Found: {memory['content']['title']}")
    print(f"Type: {memory['type']}")
    print(f"Strength: {memory['strength']}")
```

### `search_memories(query, limit)`

Searches for memories similar to the query.

**Parameters:**
- `query` (any): Search query (string, dict, or object)
- `limit` (int): Maximum number of results (default: 10)

**Returns:** List of search results

**Search Result Format:**
```json
{
    "id": "memory_123",
    "score": 0.85,
    "content": {...},
    "metadata": {...}
}
```

**Example:**
```python
# Search by text
results = await sdk.search_memories("meeting strategy", limit=5)

# Search with filters
results = await sdk.search_memories(
    query={
        "type": "episodic",
        "domain": "business",
        "importance": ">0.7"
    },
    limit=10
)

for result in results:
    print(f"Found: {result['content']['title']}")
    print(f"Score: {result['score']:.2f}")
    print(f"Tags: {result['metadata'].get('tags', [])}")
```

### `connect_memories(id1, id2, strength)`

Creates a connection between two memories.

**Parameters:**
- `id1` (string): First memory ID
- `id2` (string): Second memory ID
- `strength` (float): Connection strength (0.0 to 1.0)

**Returns:** Boolean success indicator

**Example:**
```python
# Connect related memories
await sdk.connect_memories(
    memory_id_1,
    memory_id_2,
    strength=0.8
)
```

## 📚 Memory Management

### `update_memory_strength(id, delta)`

Updates the strength of a memory based on usage.

**Parameters:**
- `id` (string): Memory ID
- `delta` (float): Strength change (-1.0 to 1.0)

**Returns:** Boolean success indicator

**Example:**
```python
# Strengthen frequently accessed memory
await sdk.update_memory_strength(memory_id, 0.1)

# Weaken outdated memory
await sdk.update_memory_strength(old_memory_id, -0.2)
```

### `get_memory_stats(id)`

Gets statistics about a specific memory.

**Parameters:**
- `id` (string): Memory ID

**Returns:** Memory statistics object

**Statistics Format:**
```json
{
    "access_count": 15,
    "last_accessed": 1640995200000,
    "creation_time": 1640995100000,
    "connection_count": 3,
    "average_relevance": 0.75
}
```

### `delete_memory(id)`

Deletes a memory from the brain.

**Parameters:**
- `id` (string): Memory ID

**Returns:** Boolean success indicator

**Example:**
```python
success = await sdk.delete_memory(memory_id)
if success:
    print("Memory deleted successfully")
```

### `list_memories(filters, limit)`

Lists memories with optional filtering.

**Parameters:**
- `filters` (dict): Filter criteria
- `limit` (int): Maximum results to return

**Returns:** List of memory summaries

**Example:**
```python
# List recent episodic memories
memories = await sdk.list_memories(
    filters={
        "type": "episodic",
        "created_after": "2025-01-01",
        "importance": ">0.5"
    },
    limit=20
)
```

## 🎯 Learning System

### `learn(pattern, context)`

Learns from new information and patterns.

**Parameters:**
- `pattern` (string): Pattern to learn
- `context` (list): Context information

**Returns:** Boolean success indicator

**Example:**
```python
# Learn user behavior patterns
await sdk.learn(
    pattern="user_prefers_detailed_explanations",
    context=["asks_follow_up_questions", "reads_documentation"]
)

# Learn system patterns
await sdk.learn(
    pattern="high_engagement_content",
    context=["interactive_elements", "visual_content", "short_videos"]
)
```

### `get_learning_patterns()`

Retrieves learned patterns and their statistics.

**Returns:** List of learning patterns

**Pattern Format:**
```json
{
    "pattern": "user_prefers_detailed_explanations",
    "frequency": 25,
    "strength": 0.85,
    "context": ["asks_follow_up_questions", "reads_documentation"],
    "last_updated": 1640995200000,
    "confidence": 0.92
}
```

**Example:**
```python
patterns = await sdk.get_learning_patterns()
for pattern in patterns:
    print(f"Pattern: {pattern['pattern']}")
    print(f"Strength: {pattern['strength']:.2f}")
    print(f"Frequency: {pattern['frequency']}")
```

### `add_feedback(type, information, reasoning)`

Provides feedback to improve learning accuracy.

**Parameters:**
- `type` (string): Feedback type ('positive', 'negative', 'neutral')
- `information` (string): Feedback information
- `reasoning` (string): Optional reasoning behind the feedback

**Returns:** Boolean success indicator

**Example:**
```python
# Positive feedback
await sdk.add_feedback(
    "positive",
    "User was very satisfied with the explanation",
    "The answer matched exactly what the user was looking for"
)

# Negative feedback
await sdk.add_feedback(
    "negative",
    "User found the answer confusing",
    "Technical jargon was not appropriate for the user's level"
)
```

### `get_learning_progress()`

Gets information about the learning system's progress.

**Returns:** Learning progress statistics

**Progress Format:**
```json
{
    "total_patterns": 156,
    "active_patterns": 89,
    "learning_accuracy": 0.87,
    "improvement_rate": 0.12,
    "last_training": 1640995200000
}
```

## 🤔 Reasoning Engine

### `reason(query, context)`

Performs reasoning on a query using stored knowledge.

**Parameters:**
- `query` (string): Question or query
- `context` (list): Additional context information

**Returns:** Reasoning result object

**Reasoning Result Format:**
```json
{
    "conclusion": "You should learn Python first",
    "confidence": 0.85,
    "reasoning_path": [
        "Python is beginner-friendly",
        "High demand in job market",
        "Good for data science"
    ],
    "supporting_evidence": [
        "Memory: python_tutorial_completion",
        "Pattern: user_prefers_practical_examples"
    ],
    "timestamp": 1640995200000
}
```

**Example:**
```python
# Ask a question
reasoning = await sdk.reason(
    query="What programming language should I learn first?",
    context=["beginner", "career_oriented", "data_science"]
)

print(f"Answer: {reasoning['conclusion']}")
print(f"Confidence: {reasoning['confidence']:.2f}")
print("Reasoning steps:")
for step in reasoning['reasoning_path']:
    print(f"  - {step}")
```

### `explain_conclusion(conclusion_id)`

Gets detailed explanation for a reasoning conclusion.

**Parameters:**
- `conclusion_id` (string): Reasoning conclusion ID

**Returns:** Detailed explanation object

### `validate_reasoning(reasoning_id)`

Validates the quality of a reasoning result.

**Parameters:**
- `reasoning_id` (string): Reasoning result ID

**Returns:** Validation result with quality metrics

## 🔍 Vector Operations

### `store_vector(vector, metadata)`

Stores a vector for similarity search.

**Parameters:**
- `vector` (list): Numerical vector
- `metadata` (dict): Associated metadata

**Returns:** Vector ID string

**Example:**
```python
# Store embedding vector
vector_id = await sdk.store_vector(
    vector=[0.1, 0.2, 0.3, 0.4, 0.5],
    metadata={
        "text": "Hello world",
        "language": "english",
        "topic": "greeting"
    }
)
```

### `search_similar_vectors(vector, limit)`

Searches for similar vectors using cosine similarity.

**Parameters:**
- `vector` (list): Query vector
- `limit` (int): Maximum results

**Returns:** List of similar vectors

**Example:**
```python
# Find similar vectors
query_vector = [0.15, 0.25, 0.35, 0.45, 0.55]
similar_vectors =imilar_vectors(query_vector await sdk.search_s, limit=5)

for vector in similar_vectors:
    print(f"Similarity: {vector['score']:.3f}")
    print(f"Text: {vector['metadata']['text']}")
```

### `compute_similarity(vector1, vector2)`

Computes similarity between two vectors.

**Parameters:**
- `vector1` (list): First vector
- `vector2` (list): Second vector

**Returns:** Similarity score (0.0 to 1.0)

**Example:**
```python
similarity = await sdk.compute_similarity(
    vector1=[0.1, 0.2, 0.3],
    vector2=[0.15, 0.25, 0.35]
)
print(f"Similarity: {similarity:.3f}")
```

## 🕸️ Graph Knowledge

### `create_graph_node(id, label, type, properties)`

Creates a node in the knowledge graph.

**Parameters:**
- `id` (string): Node ID
- `label` (string): Node label
- `type` (string): Node type
- `properties` (dict): Node properties

**Returns:** Boolean success indicator

**Example:**
```python
# Create concept node
await sdk.create_graph_node(
    id="python_concept",
    label="Python Programming",
    type="technology",
    properties={
        "category": "programming_language",
        "difficulty": "beginner",
        "popularity": 0.95
    }
)
```

### `connect_graph_nodes(node_id1, node_id2, weight)`

Creates an edge between two graph nodes.

**Parameters:**
- `node_id1` (string): First node ID
- `node_id2` (string): Second node ID
- `weight` (float): Connection weight (0.0 to 1.0)

**Returns:** Boolean success indicator

**Example:**
```python
# Connect related concepts
await sdk.connect_graph_nodes(
    "python_concept",
    "data_science_concept",
    weight=0.8
)
```

### `get_graph_neighbors(node_id, depth)`

Gets neighboring nodes in the graph.

**Parameters:**
- `node_id` (string): Node ID
- `depth` (int): Search depth

**Returns:** List of neighboring nodes

**Example:**
```python
# Get related concepts
neighbors = await sdk.get_graph_neighbors("python_concept", depth=2)

for neighbor in neighbors:
    print(f"Related: {neighbor['label']}")
    print(f"Connection strength: {neighbor['weight']}")
```

### `find_graph_path(start_node, end_node)`

Finds a path between two nodes in the graph.

**Parameters:**
- `start_node` (string): Starting node ID
- `end_node` (string): Ending node ID

**Returns:** List of nodes representing the path

**Example:**
```python
# Find concept relationships
path = await sdk.find_graph_path("python_concept", "ai_concept")
print("Concept chain:")
for node in path:
    print(f"  {node['label']}")
```

## ⚙️ System Management

### `get_status()`

Returns the current system status.

**Returns:** System status object

**Status Format:**
```json
{
    "status": "healthy",
    "version": "1.0.0",
    "uptime": 86400,
    "memory_usage": 0.45,
    "cpu_usage": 0.23,
    "active_connections": 12
}
```

### `get_statistics()`

Returns comprehensive system statistics.

**Returns:** System statistics object

**Statistics Format:**
```json
{
    "total_memories": 15420,
    "memory_types": {
        "episodic": 4520,
        "semantic": 8230,
        "procedural": 1890,
        "emotional": 780
    },
    "learning_patterns": 156,
    "vector_count": 8930,
    "graph_nodes": 2340,
    "average_response_time": 45,
    "cache_hit_rate": 0.87
}
```

### `clear_all()`

Clears all data from the system.

**⚠️ Warning:** This operation is irreversible!

**Returns:** Boolean success indicator

**Example:**
```python
# Clear all data (use with caution!)
success = await sdk.clear_all()
if success:
    print("All data cleared successfully")
```

### `backup_data()`

Creates a backup of all system data.

**Returns:** Backup information object

**Example:**
```python
# Create backup
backup_info = await sdk.backup_data()
print(f"Backup created: {backup_info['backup_id']}")
print(f"Size: {backup_info['size_mb']} MB")
```

### `restore_data(backup_id)`

Restores data from a backup.

**Parameters:**
- `backup_id` (string): Backup ID to restore

**Returns:** Boolean success indicator

## 🔧 Utility Methods

### `batch(operations)`

Performs multiple operations in a single request.

**Parameters:**
- `operations` (list): List of operation objects

**Returns:** List of operation results

**Example:**
```python
# Batch operations
operations = [
    {
        "type": "store_memory",
        "data": {
            "content": {"text": "Memory 1"},
            "type": "semantic"
        }
    },
    {
        "type": "store_memory",
        "data": {
            "content": {"text": "Memory 2"},
            "type": "episodic"
        }
    },
    {
        "type": "learn",
        "data": {
            "pattern": "user_pattern",
            "context": ["context1"]
        }
    }
]

results = await sdk.batch(operations)
```

### `stream(endpoint, callback)`

Subscribes to real-time updates via streaming.

**Parameters:**
- `endpoint` (string): Stream endpoint
- `callback` (function): Callback function for updates

**Returns:** Unsubscribe function

**Example:**
```python
# Subscribe to memory updates
def on_memory_update(data):
    print(f"New memory: {data['content']}")

unsubscribe = await sdk.stream('/api/memory/stream', on_memory_update)

# Later, unsubscribe
unsubscribe()
```

### `health_check()`

Performs a comprehensive health check.

**Returns:** Boolean health status

**Example:**
```python
# Check system health
is_healthy = await sdk.health_check()
if is_healthy:
    print("✅ System is healthy")
else:
    print("❌ System has issues")
    status = await sdk.get_status()
    print(f"Issues: {status.get('issues', [])}")
```

## 🌍 Language-Specific APIs

### Python SDK Features

#### Async/Await Support
```python
import asyncio

async def main():
    # All methods support async/await
    memory_id = await sdk.store_memory(content, type)
    reasoning = await sdk.reason(query, context)

asyncio.run(main())
```

#### Type Hints
```python
from typing import List, Dict, Optional

async def search_knowledge(
    query: str, 
    limit: int = 10,
    filters: Optional[Dict] = None
) -> List[Dict]:
    return await sdk.search_memories(query, limit, filters)
```

#### Context Managers
```python
async with sdk.transaction() as session:
    await session.store_memory(content1, type1)
    await session.store_memory(content2, type2)
    # Automatically commits or rolls back
```

### JavaScript/TypeScript SDK Features

#### Promise-based API
```javascript
// All methods return promises
sdk.storeMemory(content, type)
    .then(memoryId => console.log('Stored:', memoryId))
    .catch(error => console.error('Error:', error));

// Or use async/await
const memoryId = await sdk.storeMemory(content, type);
```

#### TypeScript Support
```typescript
interface MemoryContent {
    title: string;
    content: string;
    tags: string[];
}

const memoryId: string = await sdk.storeMemory<MemoryContent>(
    { title: "Test", content: "Content", tags: ["test"] },
    'semantic'
);
```

#### Event Emitter
```javascript
// Subscribe to events
sdk.on('memory_stored', (data) => {
    console.log('Memory stored:', data.id);
});

sdk.on('reasoning_completed', (data) => {
    console.log('Reasoning result:', data.conclusion);
});
```

### Java SDK Features

#### CompletableFuture Support
```java
CompletableFuture<String> memoryId = sdk.storeMemory(content, type, metadata);

// Chain operations
CompletableFuture<ReasoningResult> reasoning = memoryId
    .thenCompose(id -> sdk.getMemory(id))
    .thenCompose(memory -> sdk.reason(memory.getContent().toString()));

// Handle errors
reasoning.exceptionally(throwable -> {
    System.err.println("Error: " + throwable.getMessage());
    return null;
});
```

#### Builder Pattern
```java
MemorySearchRequest request = MemorySearchRequest.builder()
    .query("search term")
    .limit(10)
    .filters(Map.of("type", "semantic"))
    .build();

CompletableFuture<List<SearchResult>> results = sdk.searchMemories(request);
```

### Go SDK Features

#### Context Support
```go
ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
defer cancel()

memoryID, err := sdk.StoreMemoryWithContext(ctx, content, semanticMemory, nil)
```

#### Error Handling
```go
if err != nil {
    if brainaiErr, ok := err.(*brainai.BrainAIError); ok {
        switch brainaiErr.Code {
        case brainai.ErrNotFound:
            fmt.Println("Memory not found")
        case brainai.ErrInvalidInput:
            fmt.Println("Invalid input parameters")
        default:
            fmt.Printf("Unknown error: %v\n", brainaiErr)
        }
    }
}
```

### Rust SDK Features

#### Async/Await with Tokio
```rust
#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let memory_id = sdk.store_memory(
        json!({"text": "Hello"}),
        MemoryType::Semantic,
        None,
    ).await?;
    
    Ok(())
}
```

#### Strong Typing
```rust
pub struct CustomMemory {
    pub id: String,
    pub content: serde_json::Value,
    pub memory_type: MemoryType,
    pub metadata: HashMap<String, serde_json::Value>,
}

impl CustomMemory {
    pub async fn store(&self, sdk: &BrainAISDK) -> Result<String, BrainAIError> {
        sdk.store_memory(
            self.content.clone(),
            self.memory_type,
            Some(self.metadata.clone())
        ).await
    }
}
```

### Ruby SDK Features

#### Block Support
```ruby
# Methods that accept blocks
sdk.search_memories("query", 10) do |result|
  puts "Found: #{result['content']['title']}"
end

# Context manager style
sdk.transaction do |session|
  session.store_memory(content1, type1)
  session.store_memory(content2, type2)
end
```

#### Ruby-style Iterators
```ruby
# Memory iteration
sdk.list_memories(type: 'episodic').each do |memory|
  puts "Memory: #{memory['content']['title']}"
end

# Pattern iteration
sdk.get_learning_patterns.each_with_index do |pattern, index|
  puts "#{index + 1}. #{pattern['pattern']} (strength: #{pattern['strength']})"
end
```

### PHP SDK Features

#### Exception Handling
```php
try {
    $memoryId = $sdk->storeMemory($content, $type, $metadata);
    echo "Stored memory: $memoryId\n";
} catch (BrainAIException $e) {
    error_log("Brain AI error: " . $e->getMessage());
}
```

#### Static Factory Methods
```php
// Factory pattern
$memory = BrainAIMemory::create()
    ->withContent($content)
    ->withType('semantic')
    ->withMetadata(['importance' => 0.8])
    ->store($sdk);
```

### C# SDK Features

#### LINQ Support
```csharp
// LINQ queries
var recentMemories = (await sdk.GetAllMemoriesAsync())
    .Where(m => m.Timestamp > DateTimeOffset.UtcNow.AddDays(-7))
    .OrderByDescending(m => m.Strength)
    .Take(10);

// Async enumeration
await foreach (var memory in sdk.GetMemoriesStreamAsync())
{
    Console.WriteLine($"Memory: {memory.Content}");
}
```

#### Dependency Injection
```csharp
// Startup.cs
services.AddSingleton<BrainAISDK>(provider => 
    new BrainAISDK(configuration.GetSection("BrainAI").Get<BrainAIConfig>())
);

// In your service
public class MyService
{
    private readonly BrainAISDK _brainAI;
    
    public MyService(BrainAISDK brainAI)
    {
        _brainAI = brainAI;
    }
}
```

## 📊 Rate Limiting

All SDKs implement rate limiting to prevent API abuse:

- **Default Limits**: 100 requests per minute
- **Burst Limit**: 10 requests per second
- **Headers**: Rate limit information in response headers

```python
# Check rate limit status
headers = response.headers
remaining = headers.get('X-RateLimit-Remaining')
reset_time = headers.get('X-RateLimit-Reset')
```

## 🔒 Authentication

All requests require authentication via API key:

```python
# API key in configuration
config = BrainAIConfig(
    base_url="http://localhost:8000",
    api_key="your-api-key-here"
)

# Environment variable
export BRAIN_AI_API_KEY="your-api-key-here"
```

## 📈 Performance Tips

### Batch Operations
```python
# Instead of multiple individual calls
for item in items:
    await sdk.store_memory(item['content'], item['type'])

# Use batch operations
operations = [
    {"type": "store_memory", "data": item} 
    for item in items
]
await sdk.batch(operations)
```

### Connection Pooling
```python
# Reuse SDK instance
sdk = BrainAISDK(config)

# Don't create new instances for each request
async def process_requests(requests):
    tasks = [sdk.process_request(req) for req in requests]
    return await asyncio.gather(*tasks)
```

### Caching
```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_cached_memory(memory_id: str):
    return sdk.get_memory(memory_id)
```

---

*This API reference covers all methods available across all Brain AI SDKs. For language-specific examples and advanced usage patterns, see the [Examples Guide](examples.md).*