# Getting Started with Brain AI

Welcome to Brain AI! This guide will help you get up and running with the framework in just a few minutes.

## 🎯 What You'll Learn

- How to set up your first Brain AI project
- Store and retrieve your first memories
- Perform semantic searches
- Use the learning and reasoning capabilities
- Build your first intelligent application

## ⚡ Quick Setup (5 Minutes)

### 1. Choose Your Language

Brain AI supports 8 programming languages. Choose one that fits your project:

| Language | Best For | Complexity |
|----------|----------|------------|
| **Python** | Data Science, AI/ML | Beginner |
| **JavaScript** | Web Apps, Frontend | Beginner |
| **Java** | Enterprise, Android | Intermediate |
| **Go** | High Performance, Backend | Intermediate |
| **Rust** | Systems Programming | Advanced |
| **Ruby** | Web Development | Beginner |
| **PHP** | Web Applications | Beginner |
| **C#** | .NET Development | Intermediate |

### 2. Install the SDK

Select your language and follow the installation instructions:

#### Python
```bash
pip install brain-ai-sdk
```

#### JavaScript/TypeScript
```bash
npm install brain-ai-sdk
# or
yarn add brain-ai-sdk
```

#### Java
```xml
<!-- Add to your pom.xml -->
<dependency>
    <groupId>com.brainai</groupId>
    <artifactId>brain-ai-sdk</artifactId>
    <version>1.0.0</version>
</dependency>
```

#### Go
```bash
go get github.com/brain-ai/sdk
```

### 3. Create Your First Brain AI Application

Let's start with a simple "Personal Knowledge Assistant" that learns from your notes and answers questions.

#### Python Version
```python
# File: knowledge_assistant.py
import asyncio
from brain_ai import BrainAISDK, BrainAIConfig

class PersonalKnowledgeAssistant:
    def __init__(self):
        config = BrainAIConfig(
            base_url="http://localhost:8000",  # Brain AI server
            api_key="your-api-key-here"       # Get from brain-ai.com
        )
        self.sdk = BrainAISDK(config)
    
    async def add_note(self, title, content, tags=None):
        """Store a note in your personal knowledge base"""
        memory_id = await self.sdk.store_memory(
            content={
                "title": title,
                "content": content,
                "tags": tags or []
            },
            type="semantic",
            metadata={
                "source": "personal_note",
                "importance": 0.8
            }
        )
        return memory_id
    
    async def search_knowledge(self, query, limit=5):
        """Search your knowledge base"""
        results = await self.sdk.search_memories(query, limit)
        return results
    
    async def ask_question(self, question, context=None):
        """Ask a question and get an intelligent answer"""
        reasoning = await self.sdk.reason(question, context)
        return reasoning
    
    async def learn_preference(self, preference, context):
        """Learn from user preferences"""
        await self.sdk.learn(preference, context)

# Example usage
async def main():
    assistant = PersonalKnowledgeAssistant()
    
    # Add some knowledge
    await assistant.add_note(
        "Python Tips", 
        "Use list comprehensions for clean, efficient code. Always use type hints for better IDE support.",
        ["python", "programming", "tips"]
    )
    
    await assistant.add_note(
        "Machine Learning Basics", 
        "Start with simple models like linear regression before moving to complex neural networks.",
        ["ml", "basics", "tutorial"]
    )
    
    # Search knowledge
    results = await assistant.search_knowledge("programming tips", limit=3)
    print("Found knowledge:")
    for result in results:
        print(f"- {result['content']['title']} (Score: {result['score']:.2f})")
    
    # Ask a question
    answer = await assistant.ask_question(
        "What should I know about Python programming?",
        ["programming", "python", "tips"]
    )
    print(f"\nAI Answer: {answer['conclusion']}")
    print(f"Confidence: {answer['confidence']:.2f}")

# Run the example
if __name__ == "__main__":
    asyncio.run(main())
```

#### JavaScript Version
```javascript
// File: knowledge-assistant.js
import { BrainAISDK } from 'brain-ai-sdk';

class PersonalKnowledgeAssistant {
    constructor() {
        this.sdk = new BrainAISDK({
            baseUrl: 'http://localhost:8000',
            apiKey: 'your-api-key-here'
        });
    }
    
    async addNote(title, content, tags = []) {
        const memoryId = await this.sdk.storeMemory(
            {
                title,
                content,
                tags
            },
            'semantic',
            {
                source: 'personal_note',
                importance: 0.8
            }
        );
        return memoryId;
    }
    
    async searchKnowledge(query, limit = 5) {
        const results = await this.sdk.searchMemories(query, limit);
        return results;
    }
    
    async askQuestion(question, context = []) {
        const reasoning = await this.sdk.reason(question, context);
        return reasoning;
    }
    
    async learnPreference(preference, context) {
        await this.sdk.learn(preference, context);
    }
}

// Example usage
async function main() {
    const assistant = new PersonalKnowledgeAssistant();
    
    // Add some knowledge
    await assistant.addNote(
        'JavaScript Best Practices',
        'Always use const/let instead of var. Use arrow functions for cleaner code.',
        ['javascript', 'programming', 'best-practices']
    );
    
    await assistant.addNote(
        'Web Development Tips',
        'Use semantic HTML elements for better accessibility and SEO.',
        ['web-dev', 'html', 'accessibility']
    );
    
    // Search knowledge
    const results = await assistant.searchKnowledge('programming', 3);
    console.log('Found knowledge:');
    results.forEach(result => {
        console.log(`- ${result.content.title} (Score: ${result.score.toFixed(2)})`);
    });
    
    // Ask a question
    const answer = await assistant.askQuestion(
        'What are JavaScript best practices?',
        ['javascript', 'programming']
    );
    
    console.log(`\nAI Answer: ${answer.conclusion}`);
    console.log(`Confidence: ${answer.confidence.toFixed(2)}`);
}

// Run the example
main().catch(console.error);
```

## 🏗️ Understanding the Components

### Memory Storage
Brain AI stores information in different memory types:

```python
# Episodic Memory - Specific events
await sdk.store_memory(
    content="I met John at the conference yesterday",
    type="episodic"
)

# Semantic Memory - General knowledge
await sdk.store_memory(
    content="Python is a programming language created by Guido van Rossum",
    type="semantic"
)

# Procedural Memory - How-to knowledge
await sdk.store_memory(
    content="To install Python: pip install python",
    type="procedural"
)

# Emotional Memory - Preferences
await sdk.store_memory(
    content="I prefer working with Python over JavaScript",
    type="emotional"
)
```

### Semantic Search
Find related information using natural language:

```python
# Search for programming related knowledge
results = await sdk.search_memories("How to write clean code", limit=10)

for result in results:
    print(f"Found: {result['content']}")
    print(f"Relevance Score: {result['score']:.2f}")
```

### Learning System
Brain AI automatically learns patterns from your data:

```python
# Provide feedback to improve learning
await sdk.add_feedback(
    "positive",
    "User was satisfied with the answer",
    "The response matched the user's needs perfectly"
)

# Learn from user interactions
await sdk.learn(
    "user_preference",
    ["prefers_detailed_explanations", "asks_technical_questions"]
)
```

### Reasoning Engine
Ask questions and get intelligent answers:

```python
reasoning_result = await sdk.reason(
    query="What programming language should I learn first?",
    context=["beginner", "career_development", "data_science"]
)

print(f"Answer: {reasoning_result['conclusion']}")
print(f"Confidence: {reasoning_result['confidence']:.2f}")
print(f"Reasoning path: {reasoning_result['reasoning_path']}")
```

## 🚀 Next Steps

### 1. Explore More Examples
- Check out the [Examples Guide](examples.md) for advanced use cases
- Try building a [Customer Service Bot](examples.md#customer-service-ai)
- Create a [Research Assistant](examples.md#research-assistant)

### 2. Customize Your Configuration
```python
# High-performance configuration
config = BrainAIConfig(
    base_url="http://localhost:8000",
    memory_size=100000,           # Larger memory capacity
    learning_rate=0.05,          # Conservative learning
    similarity_threshold=0.8,     # Higher accuracy requirement
    max_reasoning_depth=10        # Deeper reasoning
)
```

### 3. Monitor Your Application
```python
# Check system health
status = await sdk.get_status()
print(f"System status: {status}")

# Get statistics
stats = await sdk.get_statistics()
print(f"Memory usage: {stats['memory_usage']:.1%}")
print(f"Learning patterns: {len(stats['patterns'])}")
```

## 🔧 Common Setup Issues

### Connection Problems
```python
# Test connectivity
import aiohttp

async def test_connection():
    async with aiohttp.ClientSession() as session:
        async with session.get("http://localhost:8000/api/status") as resp:
            print(f"Server status: {resp.status}")
            data = await resp.json()
            print(f"Brain AI status: {data.get('status')}")
```

### Authentication Issues
```python
# Verify your API key
config = BrainAIConfig(
    base_url="http://localhost:8000",
    api_key="your-actual-api-key-here"  # Get from brain-ai.com
)

# Test authentication
try:
    status = await sdk.get_status()
    print("✅ Authentication successful!")
except Exception as e:
    print(f"❌ Authentication failed: {e}")
```

### Performance Optimization
```python
# Use batch operations for efficiency
operations = [
    {"type": "store_memory", "data": memory1},
    {"type": "store_memory", "data": memory2},
    {"type": "learn", "data": pattern}
]

results = await sdk.batch(operations)
```

## 🎓 Learning Path

### Beginner Path
1. ✅ Complete this getting started guide
2. 📚 Read the [API Reference](api-reference.md)
3. 🔧 Try the [Basic Examples](examples.md#basic-examples)
4. 🎯 Build your first application

### Intermediate Path
1. 🔍 Study [Advanced Use Cases](examples.md#advanced-use-cases)
2. ⚙️ Learn [Configuration Options](configuration.md)
3. 📊 Implement [Performance Monitoring](troubleshooting.md#performance-monitoring)
4. 🏗️ Build a production application

### Advanced Path
1. 🧠 Contribute to the [Core Framework](contributing.md)
2. 🔧 Create [Custom Extensions](contributing.md#creating-extensions)
3. 📈 Optimize for [Enterprise Scale](configuration.md#enterprise-configuration)
4. 🤝 Join the [Development Community](contributing.md#community)

## 💡 Pro Tips

1. **Start Simple**: Begin with basic memory storage and search before exploring advanced features
2. **Use Metadata**: Tag your memories with relevant metadata for better organization
3. **Provide Feedback**: Use `add_feedback()` to improve AI accuracy over time
4. **Monitor Performance**: Regularly check system status and adjust configuration as needed
5. **Join the Community**: Connect with other developers in our Discord server

## 🆘 Need Help?

- 📚 **Documentation**: Check the [full documentation](README.md)
- 🐛 **Bug Reports**: Report issues on [GitHub](https://github.com/brain-ai/framework/issues)
- 💬 **Community**: Join our [Discord server](https://discord.gg/brain-ai)
- 📧 **Support**: Email support@brain-ai.com

---

*Ready to build something amazing with Brain AI? Let's go! 🚀*