# Examples & Use Cases

Practical examples and real-world use cases for the Brain AI Framework across different domains and programming languages.

## 📋 Table of Contents

- [Basic Examples](#basic-examples)
- [Advanced Use Cases](#advanced-use-cases)
- [Industry Applications](#industry-applications)
- [Integration Examples](#integration-examples)
- [Performance Optimization](#performance-optimization)
- [Multi-Language Examples](#multi-language-examples)

## 🎯 Basic Examples

### Personal Knowledge Assistant

Build an intelligent note-taking system that learns from your notes and answers questions.

```python
# personal_knowledge_assistant.py
import asyncio
from brain_ai import BrainAISDK, BrainAIConfig

class PersonalKnowledgeAssistant:
    def __init__(self):
        config = BrainAIConfig(
            base_url="http://localhost:8000",
            api_key="your-api-key"
        )
        self.sdk = BrainAISDK(config)
    
    async def add_note(self, title, content, tags=None, importance=0.7):
        """Store a note with automatic categorization"""
        memory_id = await self.sdk.store_memory(
            content={
                "title": title,
                "content": content,
                "tags": tags or [],
                "word_count": len(content.split()),
                "category": self._categorize_note(title, content)
            },
            type="semantic",
            metadata={
                "source": "personal_note",
                "importance": importance,
                "created_date": asyncio.get_event_loop().time()
            }
        )
        return memory_id
    
    async def search_notes(self, query, limit=10):
        """Search through personal notes"""
        results = await self.sdk.search_memories(query, limit)
        
        # Filter for personal notes only
        personal_notes = [
            result for result in results 
            if result['metadata'].get('source') == 'personal_note'
        ]
        
        return personal_notes
    
    async def ask_question(self, question):
        """Ask questions about stored knowledge"""
        reasoning = await self.sdk.reason(
            query=question,
            context=["personal_knowledge", "notes", "research"]
        )
        return reasoning
    
    async def get_learning_insights(self):
        """Get insights about knowledge patterns"""
        patterns = await self.sdk.get_learning_patterns()
        
        insights = {
            "most_common_topics": [],
            "knowledge_gaps": [],
            "improvement_suggestions": []
        }
        
        for pattern in patterns:
            if pattern['strength'] > 0.7:
                insights["most_common_topics"].append({
                    "topic": pattern['pattern'],
                    "frequency": pattern['frequency'],
                    "strength": pattern['strength']
                })
        
        return insights
    
    def _categorize_note(self, title, content):
        """Simple categorization logic"""
        title_lower = title.lower()
        content_lower = content.lower()
        
        if any(word in title_lower or word in content_lower for word in 
               ['work', 'project', 'meeting', 'deadline']):
            return "work"
        elif any(word word in content_lower for word in 
 in title_lower or                ['learn', 'study', 'course', 'book']):
            return "learning"
        elif any(word in title_lower or word in content_lower for word in 
                ['idea', 'thought', 'brainstorm']):
            return "ideas"
        else:
            return "general"

# Usage Example
async def main():
    assistant = PersonalKnowledgeAssistant()
    
    # Add some notes
    await assistant.add_note(
        "Python List Comprehensions",
        "List comprehensions provide a concise way to create lists. "
        "Syntax: [expression for item in iterable if condition]",
        tags=["python", "programming", "syntax"],
        importance=0.8
    )
    
    await assistant.add_note(
        "Machine Learning Project Ideas",
        "1. Sentiment Analysis of Reviews\n2. Stock Price Prediction\n3. Image Classification",
        tags=["ml", "ideas", "projects"],
        importance=0.7
    )
    
    # Search for notes
    notes = await assistant.search_notes("python programming", limit=5)
    print("Found notes:")
    for note in notes:
        print(f"- {note['content']['title']} (Score: {note['score']:.2f})")
    
    # Ask a question
    answer = await assistant.ask_question(
        "What should I learn about Python programming?"
    )
    print(f"\nAI Suggestion: {answer['conclusion']}")
    print(f"Confidence: {answer['confidence']:.2f}")
    
    # Get insights
    insights = await assistant.get_learning_insights()
    print(f"\nKnowledge Insights:")
    for topic in insights["most_common_topics"]:
        print(f"- {topic['topic']}: {topic['frequency']} occurrences")

# Run the example
if __name__ == "__main__":
    asyncio.run(main())
```

### Smart Todo List

Create a todo list that learns from your habits and optimizes task scheduling.

```javascript
// smart_todo_list.js
import { BrainAISDK, BrainAIConfig } from 'brain-ai-sdk';

class SmartTodoList {
    constructor() {
        this.sdk = new BrainAISDK({
            baseUrl: 'http://localhost:8000',
            apiKey: 'your-api-key'
        });
    }
    
    async addTask(title, description, priority = 'medium', category = 'general') {
        const task = {
            title,
            description,
            priority,
            category,
            status: 'pending',
            created_at: new Date().toISOString()
        };
        
        const memoryId = await this.sdk.storeMemory(
            task,
            'episodic',
            {
                type: 'todo_task',
                priority,
                category,
                source: 'todo_app'
            }
        );
        
        // Learn task pattern
        await this.sdk.learn('task_pattern', [
            `priority_${priority}`,
            `category_${category}`,
            'todo_creation'
        ]);
        
        return { task, memoryId };
    }
    
    async getTodaysTasks() {
        const today = new Date().toISOString().split('T')[0];
        
        const results = await this.sdk.searchMemories(
            { type: 'todo_task', status: 'pending' },
            50
        );
        
        // Filter for today's tasks (simplified)
        return results.filter(result => 
            result.content.created_at.startsWith(today)
        );
    }
    
    async completeTask(taskId) {
        // Update task status
        const success = await this.sdk.updateMemoryStrength(taskId, 0.2);
        
        // Learn completion pattern
        await this.sdk.learn('task_completion', [
            'positive_reinforcement',
            'task_finished'
        ]);
        
        return success;
    }
    
    async getTaskInsights() {
        const patterns = await this.sdk.getLearningPatterns();
        
        return patterns.filter(p => 
            p.pattern.includes('task') || p.pattern.includes('todo')
        );
    }
    
    async suggestOptimalTime(taskId) {
        const task = await this.sdk.getMemory(taskId);
        if (!task) return null;
        
        const reasoning = await this.sdk.reason(
            'When is the best time to work on this task?',
            [
                task.content.priority,
                task.content.category,
                'time_optimization'
            ]
        );
        
        return reasoning;
    }
}

// Usage Example
async function main() {
    const todoList = new SmartTodoList();
    
    // Add tasks
    const { task: task1 } = await todoList.addTask(
        'Complete project proposal',
        'Write and review the Q1 project proposal document',
        'high',
        'work'
    );
    
    const { task: task2 } = await todoList.addTask(
        'Learn React hooks',
        'Study useState and useEffect hooks for React development',
        'medium',
        'learning'
    );
    
    // Get today's tasks
    const todaysTasks = await todoList.getTodaysTasks();
    console.log('Today\'s tasks:');
    todaysTasks.forEach(task => {
        console.log(`- ${task.content.title} (${task.content.priority})`);
    });
    
    // Get insights
    const insights = await todoList.getTaskInsights();
    console.log('\nTask Insights:');
    insights.forEach(insight => {
        console.log(`- ${insight.pattern}: strength ${insight.strength.toFixed(2)}`);
    });
}

main().catch(console.error);
```

### Customer Service Chatbot

Build an adaptive customer service system that learns from interactions.

```java
// CustomerServiceBot.java
import com.brainai.sdk.BrainAISDK;
import com.brainai.sdk.BrainAIConfig;
import java.util.*;
import java.util.concurrent.CompletableFuture;

public class CustomerServiceBot {
    private final BrainAISDK sdk;
    private final Map<String, String> sessionData = new HashMap<>();
    
    public CustomerServiceBot() {
        BrainAIConfig config = BrainAIConfig.builder()
            .baseUrl("http://localhost:8000")
            .apiKey("your-api-key")
            .build();
        this.sdk = new BrainAISDK(config);
    }
    
    public CompletableFuture<String> handleCustomerMessage(
            String customerId, 
            String message, 
            String context) {
        
        // Store the customer interaction
        CompletableFuture<String> storeInteraction = sdk.storeMemory(
            Map.of(
                "customer_id", customerId,
                "message", message,
                "context", context,
                "timestamp", System.currentTimeMillis()
            ),
            MemoryType.EPISODIC,
            Map.of(
                "type", "customer_interaction",
                "channel", "chat",
                "customer_id", customerId
            )
        );
        
        // Analyze the message for intent
        CompletableFuture<String> analyzeIntent = storeInteraction
            .thenCompose(interactionId -> analyzeIntent(message, customerId));
        
        // Generate response based on learned patterns
        return analyzeIntent
            .thenCompose(intent -> generateResponse(message, intent, customerId))
            .thenCompose(response -> {
                // Learn from this interaction
                return sdk.learn(
                    "customer_service_pattern",
                    Arrays.asList(intent, context, "chatbot_interaction")
                ).thenApply(learned -> response);
            });
    }
    
    private CompletableFuture<String> analyzeIntent(String message, String customerId) {
        // Simple intent analysis (in practice, use NLP models)
        String intent = "general_inquiry";
        
        if (message.toLowerCase().contains("password") || 
            message.toLowerCase().contains("reset")) {
            intent = "password_reset";
        } else if (message.toLowerCase().contains("account") || 
                   message.toLowerCase().contains("billing")) {
            intent = "account_issue";
        } else if (message.toLowerCase().contains("help") || 
                   message.toLowerCase().contains("support")) {
            intent = "help_request";
        }
        
        return CompletableFuture.completedFuture(intent);
    }
    
    private CompletableFuture<String> generateResponse(
            String message, 
            String intent, 
            String customerId) {
        
        // Use reasoning to generate contextual response
        return sdk.reason(
            "Generate a helpful response for this customer inquiry",
            Arrays.asList(intent, message, customerId)
        ).thenApply(reasoning -> {
            if (reasoning.get("conclusion") != null) {
                return (String) reasoning.get("conclusion");
            } else {
                // Fallback responses based on intent
                return getFallbackResponse(intent);
            }
        });
    }
    
    private String getFallbackResponse(String intent) {
        Map<String, String> responses = Map.of(
            "password_reset", "I can help you reset your password. Please check your email for reset instructions.",
            "account_issue", "I'm here to help with your account. Could you please provide more details about the issue?",
            "help_request", "I'd be happy to help! What specific assistance do you need today?",
            "general_inquiry", "Thank you for your message. How can I assist you today?"
        );
        
        return responses.getOrDefault(intent, "I'm here to help! Could you please provide more details?");
    }
    
    public CompletableFuture<Void> provideFeedback(
            String interactionId, 
            String feedback, 
            String rating) {
        
        return sdk.addFeedback(
            "positive".equals(rating) ? FeedbackType.POSITIVE : FeedbackType.NEGATIVE,
            feedback,
            "customer_service_rating"
        );
    }
    
    public CompletableFuture<Map<String, Object>> getCustomerInsights(String customerId) {
        // Get patterns related to this customer
        return sdk.getLearningPatterns()
            .thenApply(patterns -> {
                Map<String, Object> insights = new HashMap<>();
                List<String> relevantPatterns = new ArrayList<>();
                
                for (Map<String, Object> pattern : patterns) {
                    List<String> context = (List<String>) pattern.get("context");
                    if (context != null && context.contains(customerId)) {
                        relevantPatterns.add((String) pattern.get("pattern"));
                    }
                }
                
                insights.put("customer_patterns", relevantPatterns);
                insights.put("total_interactions", relevantPatterns.size());
                
                return insights;
            });
    }
}

// Usage Example
public class CustomerServiceExample {
    public static void main(String[] args) {
        CustomerServiceBot bot = new CustomerServiceBot();
        
        // Handle customer message
        bot.handleCustomerMessage(
            "customer_123",
            "I need help resetting my password",
            "support_ticket"
        ).thenAccept(response -> {
            System.out.println("Bot Response: " + response);
            
            // Provide feedback
            bot.provideFeedback(
                "interaction_456",
                "Customer was satisfied with the response",
                "positive"
            ).thenRun(() -> {
                System.out.println("Feedback recorded");
            });
        });
        
        // Get customer insights
        bot.getCustomerInsights("customer_123")
            .thenAccept(insights -> {
                System.out.println("Customer Insights: " + insights);
            });
    }
}
```

## 🚀 Advanced Use Cases

### Research Assistant

Create an AI-powered research assistant that learns from academic papers and provides insights.

```python
# research_assistant.py
import asyncio
from typing import List, Dict, Any
from brain_ai import BrainAISDK, BrainAIConfig

class ResearchAssistant:
    def __init__(self):
        config = BrainAIConfig(
            base_url="http://localhost:8000",
            memory_size=50000,  # Large capacity for research
            learning_rate=0.05  # Conservative learning for accuracy
        )
        self.sdk = BrainAISDK(config)
    
    async def add_paper(self, paper_data: Dict[str, Any]) -> str:
        """Add a research paper to the knowledge base"""
        memory_id = await self.sdk.store_memory(
            content={
                "title": paper_data["title"],
                "abstract": paper_data["abstract"],
                "authors": paper_data["authors"],
                "venue": paper_data.get("venue", ""),
                "year": paper_data.get("year", 2024),
                "keywords": paper_data.get("keywords", []),
                "citations": paper_data.get("citations", 0),
                "methodology": paper_data.get("methodology", ""),
                "findings": paper_data.get("findings", ""),
                "doi": paper_data.get("doi", "")
            },
            type="semantic",
            metadata={
                "type": "research_paper",
                "domain": paper_data.get("domain", "general"),
                "source": "academic_database",
                "relevance_score": paper_data.get("relevance_score", 0.8)
            }
        )
        
        # Learn paper patterns
        await self.sdk.learn(
            "research_pattern",
            [
                paper_data.get("domain", "general"),
                f"venue_{paper_data.get('venue', 'unknown')}",
                f"year_{paper_data.get('year', 2024)}"
            ]
        )
        
        return memory_id
    
    async def find_related_work(self, query: str, domain: str = None, limit: int = 10) -> List[Dict]:
        """Find related research papers"""
        search_context = [query]
        if domain:
            search_context.append(f"domain_{domain}")
        
        results = await self.sdk.search_memories(query, limit)
        
        # Filter for research papers
        papers = [
            result for result in results 
            if result['metadata'].get('type') == 'research_paper'
        ]
        
        # Rank by relevance and citations
        for paper in papers:
            paper['weighted_score'] = (
                paper['score'] * 0.6 + 
                min(paper['content'].get('citations', 0) / 100, 1) * 0.4
            )
        
        return sorted(papers, key=lambda x: x['weighted_score'], reverse=True)
    
    async def generate_research_summary(self, topic: str, papers: List[Dict]) -> Dict[str, Any]:
        """Generate a comprehensive research summary"""
        context = [topic, "research_synthesis"]
        
        reasoning = await self.sdk.reason(
            f"Synthesize the key findings and trends from these papers about {topic}",
            context
        )
        
        # Extract key themes
        themes = await self._extract_key_themes(papers)
        
        # Identify research gaps
        gaps = await self._identify_research_gaps(papers, topic)
        
        return {
            "topic": topic,
            "summary": reasoning.get('conclusion', ''),
            "confidence": reasoning.get('confidence', 0),
            "key_themes": themes,
            "research_gaps": gaps,
            "paper_count": len(papers),
            "synthesis_date": asyncio.get_event_loop().time()
        }
    
    async def track_research_trends(self, domain: str, time_range: int = 365) -> Dict[str, Any]:
        """Analyze research trends in a specific domain"""
        # Get patterns related to the domain
        patterns = await self.sdk.get_learning_patterns()
        domain_patterns = [
            p for p in patterns 
            if f"domain_{domain}" in p.get('context', [])
        ]
        
        # Analyze trend data
        trend_analysis = {
            "domain": domain,
            "active_research_areas": [],
            "emerging_topics": [],
            "declining_areas": [],
            "total_patterns": len(domain_patterns)
        }
        
        for pattern in domain_patterns:
            if pattern['strength'] > 0.7:
                trend_analysis["active_research_areas"].append({
                    "area": pattern['pattern'],
                    "strength": pattern['strength'],
                    "frequency": pattern['frequency']
                })
            elif pattern['last_updated'] > asyncio.get_event_loop().time() - (time_range * 24 * 3600):
                trend_analysis["emerging_topics"].append(pattern['pattern'])
        
        return trend_analysis
    
    async def suggest_research_directions(self, current_work: str, domain: str) -> List[Dict]:
        """Suggest new research directions based on existing work"""
        reasoning = await self.sdk.reason(
            f"What are promising research directions related to {current_work} in {domain}?",
            [domain, current_work, "research_suggestion"]
        )
        
        # Parse suggestions (in practice, use more sophisticated parsing)
        suggestions = []
        if reasoning.get('conclusion'):
            # Extract potential research questions from the conclusion
            # This is a simplified example
            suggestions.append({
                "direction": reasoning['conclusion'],
                "confidence": reasoning['confidence'],
                "reasoning_path": reasoning.get('reasoning_path', [])
            })
        
        return suggestions
    
    async def _extract_key_themes(self, papers: List[Dict]) -> List[str]:
        """Extract key themes from research papers"""
        themes = set()
        
        for paper in papers:
            # Extract from keywords, findings, and content
            content = paper['content']
            
            if 'keywords' in content:
                themes.update(content['keywords'])
            
            # Simple keyword extraction from abstract
            if 'abstract' in content:
                words = content['abstract'].lower().split()
                themes.update([w for w in words if len(w) > 5])
        
        return list(themes)[:20]  # Return top 20 themes
    
    async def _identify_research_gaps(self, papers: List[Dict], topic: str) -> List[str]:
        """Identify potential research gaps"""
        # This is a simplified gap analysis
        # In practice, use more sophisticated NLP techniques
        
        covered_topics = set()
        for paper in papers:
            content = paper['content']
            if 'keywords' in content:
                covered_topics.update(content['keywords'])
        
        # Suggest gaps based on common research areas
        common_areas = ["methodology", "evaluation", "comparison", "optimization", "scalability"]
        gaps = [area for area in common_areas if area not in covered_topics]
        
        return gaps

# Usage Example
async def main():
    assistant = ResearchAssistant()
    
    # Add some research papers
    papers = [
        {
            "title": "Attention Is All You Need",
            "abstract": "The dominant sequence transduction models are based on complex recurrent or convolutional neural networks.",
            "authors": ["Vaswani, A.", "Shazeer, N.", "Parmar, N."],
            "venue": "NIPS",
            "year": 2017,
            "keywords": ["transformer", "attention", "nlp"],
            "citations": 50000,
            "domain": "machine_learning"
        },
        {
            "title": "BERT: Pre-training of Deep Bidirectional Transformers",
            "abstract": "We introduce a new language representation model called BERT.",
            "authors": ["Devlin, J.", "Chang, M.", "Lee, K."],
            "venue": "NAACL",
            "year": 2019,
            "keywords": ["bert", "transformer", "pre-training"],
            "citations": 25000,
            "domain": "nlp"
        }
    ]
    
    for paper in papers:
        await assistant.add_paper(paper)
    
    # Find related work
    related = await assistant.find_related_work("transformer architecture", "machine_learning")
    print("Related papers:")
    for paper in related:
        print(f"- {paper['content']['title']} (Score: {paper['score']:.2f})")
    
    # Generate research summary
    summary = await assistant.generate_research_summary("transformers", related)
    print(f"\nResearch Summary: {summary['summary']}")
    print(f"Key themes: {', '.join(summary['key_themes'][:5])}")
    
    # Track trends
    trends = await assistant.track_research_trends("machine_learning")
    print(f"\nActive research areas: {len(trends['active_research_areas'])}")

if __name__ == "__main__":
    asyncio.run(main())
```

### Adaptive Learning Platform

Build an educational system that adapts to each student's learning style.

```go
// adaptive_learning_platform.go
package main

import (
    "context"
    "fmt"
    "log"
    "time"
    
    "github.com/brain-ai/go-sdk"
)

type Student struct {
    ID          string
    Name        string
    GradeLevel  int
    LearningStyle string
    Preferences map[string]interface{}
}

type LearningActivity struct {
    ID          string
    Type        string
    Subject     string
    Difficulty  float64
    Content     string
    Duration    time.Duration
}

type AdaptiveLearningPlatform struct {
    sdk *brainai.BrainAISDK
    students map[string]*Student
}

func NewAdaptiveLearningPlatform() *AdaptiveLearningPlatform {
    config := brainai.BrainAIConfig{
        BaseURL: "http://localhost:8000",
        APIKey:  "your-api-key",
    }
    
    return &AdaptiveLearningPlatform{
        sdk:      brainai.NewBrainAISDK(config),
        students: make(map[string]*Student),
    }
}

func (alp *AdaptiveLearningPlatform) RegisterStudent(student *Student) error {
    alp.students[student.ID] = student
    
    // Store student profile
    memoryID, err := alp.sdk.StoreMemory(
        map[string]interface{}{
            "student_id": student.ID,
            "name": student.Name,
            "grade_level": student.GradeLevel,
            "learning_style": student.LearningStyle,
            "preferences": student.Preferences,
            "registration_date": time.Now().Unix(),
        },
        brainai.SemanticMemory,
        map[string]interface{}{
            "type": "student_profile",
            "student_id": student.ID,
        },
    )
    
    if err != nil {
        return fmt.Errorf("failed to store student profile: %w", err)
    }
    
    // Learn student pattern
    err = alp.sdk.Learn(
        fmt.Sprintf("student_%s_profile", student.ID),
        []string{
            fmt.Sprintf("grade_%d", student.GradeLevel),
            student.LearningStyle,
            "student_registration",
        },
    )
    
    if err != nil {
        return fmt.Errorf("failed to learn student pattern: %w", err)
    }
    
    log.Printf("Registered student %s (ID: %s)", student.Name, student.ID)
    return nil
}

func (alp *AdaptiveLearningPlatform) RecommendActivities(studentID string, subject string, count int) ([]LearningActivity, error) {
    student, exists := alp.students[studentID]
    if !exists {
        return nil, fmt.Errorf("student not found: %s", studentID)
    }
    
    // Search for suitable activities
    query := map[string]interface{}{
        "subject": subject,
        "learning_style": student.LearningStyle,
        "grade_level": student.GradeLevel,
    }
    
    results, err := alp.sdk.SearchMemories(query, count*2) // Get more to filter
    
    if err != nil {
        return nil, fmt.Errorf("failed to search activities: %w", err)
    }
    
    // Filter and rank activities
    var activities []LearningActivity
    for _, result := range results {
        if result.Content["type"] == "learning_activity" {
            activity := LearningActivity{
                ID:         result.ID,
                Type:       result.Content["activity_type"].(string),
                Subject:    result.Content["subject"].(string),
                Difficulty: result.Content["difficulty"].(float64),
                Content:    result.Content["content"].(string),
                Duration:   time.Duration(result.Content["duration"].(float64)) * time.Minute,
            }
            
            // Adjust difficulty based on student's learning style
            if student.LearningStyle == "visual" {
                activity.Difficulty *= 0.9 // Slightly easier for visual learners
            } else if student.LearningStyle == "kinesthetic" {
                activity.Difficulty *= 1.1 // Slightly harder for kinesthetic learners
            }
            
            activities = append(activities, activity)
        }
        
        if len(activities) >= count {
            break
        }
    }
    
    return activities, nil
}

func (alp *AdaptiveLearningPlatform) RecordLearningSession(studentID string, activity LearningActivity, performance float64) error {
    // Store learning session
    sessionID, err := alp.sdk.StoreMemory(
        map[string]interface{}{
            "student_id": studentID,
            "activity_id": activity.ID,
            "subject": activity.Subject,
            "performance": performance,
            "duration": activity.Duration.Minutes(),
            "timestamp": time.Now().Unix(),
        },
        brainai.EpisodicMemory,
        map[string]interface{}{
            "type": "learning_session",
            "student_id": studentID,
            "activity_id": activity.ID,
        },
    )
    
    if err != nil {
        return fmt.Errorf("failed to record session: %w", err)
    }
    
    // Learn from performance
    performanceContext := []string{
        fmt.Sprintf("performance_%.1f", performance),
        activity.Subject,
        fmt.Sprintf("difficulty_%.1f", activity.Difficulty),
    }
    
    if performance > 0.8 {
        performanceContext = append(performanceContext, "high_performance")
    } else if performance < 0.5 {
        performanceContext = append(performanceContext, "low_performance")
    }
    
    err = alp.sdk.Learn(
        fmt.Sprintf("student_%s_performance", studentID),
        performanceContext,
    )
    
    if err != nil {
        return fmt.Errorf("failed to learn from performance: %w", err)
    }
    
    // Provide feedback
    feedbackType := "neutral"
    if performance > 0.8 {
        feedbackType = "positive"
    } else if performance < 0.5 {
        feedbackType = "negative"
    }
    
    err = alp.sdk.AddFeedback(
        brainai.FeedbackType(feedbackType),
        fmt.Sprintf("Student %s performance on %s activity: %.1f", 
            studentID, activity.Type, performance),
        fmt.Sprintf("Activity difficulty: %.1f, Duration: %.1f minutes", 
            activity.Duration.Minutes(), activity.Duration.Minutes()),
    )
    
    if err != nil {
        return fmt.Errorf("failed to provide feedback: %w", err)
    }
    
    log.Printf("Recorded learning session for student %s: %s (performance: %.1f)", 
        studentID, activity.Type, performance)
    
    return nil
}

func (alp *AdaptiveLearningPlatform) GetLearningInsights(studentID string) (map[string]interface{}, error) {
    student, exists := alp.students[studentID]
    if !exists {
        return nil, fmt.Errorf("student not found: %s", studentID)
    }
    
    // Get learning patterns
    patterns, err := alp.sdk.GetLearningPatterns()
    if err != nil {
        return nil, fmt.Errorf("failed to get patterns: %w", err)
    }
    
    // Filter patterns for this student
    studentPatterns := []map[string]interface{}{}
    for _, pattern := range patterns {
        if containsString(pattern.Context, fmt.Sprintf("student_%s", studentID)) {
            studentPatterns = append(studentPatterns, map[string]interface{}{
                "pattern":     pattern.Pattern,
                "strength":    pattern.Strength,
                "frequency":   pattern.Frequency,
                "last_updated": pattern.LastUpdated,
            })
        }
    }
    
    // Get recent performance data
    ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
    defer cancel()
    
    reasoning, err := alp.sdk.ReasonWithContext(
        ctx,
        "Analyze this student's learning patterns and provide insights",
        []string{
            fmt.Sprintf("student_%s", studentID),
            student.LearningStyle,
            fmt.Sprintf("grade_%d", student.GradeLevel),
        },
    )
    
    if err != nil {
        log.Printf("Failed to get reasoning: %v", err)
    }
    
    insights := map[string]interface{}{
        "student_id":   studentID,
        "learning_style": student.LearningStyle,
        "patterns":     studentPatterns,
        "total_patterns": len(studentPatterns),
        "ai_insights":  reasoning.Conclusion,
        "confidence":   reasoning.Confidence,
    }
    
    return insights, nil
}

func containsString(slice []string, str string) bool {
    for _, s := range slice {
        if s == str {
            return true
        }
    }
    return false
}

// Usage Example
func main() {
    platform := NewAdaptiveLearningPlatform()
    
    // Register students
    students := []*Student{
        {
            ID:           "student_001",
            Name:         "Alice Johnson",
            GradeLevel:   8,
            LearningStyle: "visual",
            Preferences:  map[string]interface{}{
                "preferred_subjects": []string{"math", "science"},
                "learning_pace": "moderate",
            },
        },
        {
            ID:           "student_002",
            Name:         "Bob Smith",
            GradeLevel:   9,
            LearningStyle: "kinesthetic",
            Preferences:  map[string]interface{}{
                "preferred_subjects": []string{"history", "english"},
                "learning_pace": "fast",
            },
        },
    }
    
    for _, student := range students {
        err := platform.RegisterStudent(student)
        if err != nil {
            log.Printf("Failed to register student %s: %v", student.Name, err)
        }
    }
    
    // Recommend activities
    activities, err := platform.RecommendActivities("student_001", "math", 3)
    if err != nil {
        log.Printf("Failed to get recommendations: %v", err)
    } else {
        fmt.Println("Recommended activities for Alice:")
        for _, activity := range activities {
            fmt.Printf("- %s: %s (Difficulty: %.1f)\n", 
                activity.Type, activity.Subject, activity.Difficulty)
        }
    }
    
    // Record learning session
    if len(activities) > 0 {
        err = platform.RecordLearningSession("student_001", activities[0], 0.85)
        if err != nil {
            log.Printf("Failed to record session: %v", err)
        }
    }
    
    // Get insights
    insights, err := platform.GetLearningInsights("student_001")
    if err != nil {
        log.Printf("Failed to get insights: %v", err)
    } else {
        fmt.Printf("\nLearning Insights for Alice:\n")
        fmt.Printf("Learning Style: %s\n", insights["learning_style"])
        fmt.Printf("Total Patterns: %d\n", insights["total_patterns"])
        if insights["ai_insights"] != nil {
            fmt.Printf("AI Insights: %s\n", insights["ai_insights"])
        }
    }
}
```

## 🏭 Industry Applications

### E-commerce Recommendation Engine

Build a sophisticated recommendation system that learns from customer behavior.

```python
# ecommerce_recommendation.py
import asyncio
from typing import List, Dict, Any
from brain_ai import BrainAISDK, BrainAIConfig

class EcommerceRecommendationEngine:
    def __init__(self):
        config = BrainAIConfig(
            base_url="http://localhost:8000",
            memory_size=100000,  # Large capacity for e-commerce
            similarity_threshold=0.6  # Lower threshold for recommendations
        )
        self.sdk = BrainAISDK(config)
    
    async def track_user_action(self, user_id: str, action: str, item_data: Dict[str, Any]):
        """Track user interactions with products"""
        memory_id = await self.sdk.store_memory(
            content={
                "user_id": user_id,
                "action": action,  # view, click, purchase, add_to_cart, review
                "item_id": item_data["id"],
                "item_category": item_data.get("category", ""),
                "item_price": item_data.get("price", 0),
                "item_rating": item_data.get("rating", 0),
                "timestamp": asyncio.get_event_loop().time(),
                "session_id": item_data.get("session_id", "")
            },
            type="episodic",
            metadata={
                "type": "user_interaction",
                "user_id": user_id,
                "action_type": action
            }
        )
        
        # Learn user preferences
        preference_context = [
            f"action_{action}",
            f"category_{item_data.get('category', 'unknown')}",
            f"price_range_{self._get_price_range(item_data.get('price', 0))}"
        ]
        
        await self.sdk.learn(
            f"user_{user_id}_preferences",
            preference_context
        )
        
        return memory_id
    
    async def get_personalized_recommendations(self, user_id: str, limit: int = 10) -> List[Dict]:
        """Get personalized product recommendations"""
        
        # Get user's learned preferences
        reasoning = await self.sdk.reason(
            f"What products would user {user_id} likely be interested in?",
            [f"user_{user_id}_preferences", "recommendation_request"]
        )
        
        # Search for products based on user patterns
        user_patterns = await self.sdk.get_learning_patterns()
        user_specific_patterns = [
            p for p in user_patterns 
            if f"user_{user_id}" in p.get('context', [])
        ]
        
        # Build search query based on preferences
        preferred_categories = []
        preferred_price_ranges = []
        
        for pattern in user_specific_patterns:
            if "category_" in pattern['pattern']:
                preferred_categories.append(pattern['pattern'].replace("category_", ""))
            if "price_range_" in pattern['pattern']:
                preferred_price_ranges.append(pattern['pattern'].replace("price_range_", ""))
        
        # Search for products
        search_query = {
            "type": "product",
            "categories": preferred_categories,
            "price_ranges": preferred_price_ranges
        }
        
        results = await self.sdk.search_memories(search_query, limit * 2)
        
        # Filter and rank products
        products = []
        for result in results:
            if result['metadata'].get('type') == 'product':
                # Calculate recommendation score
                base_score = result['score']
                
                # Boost score based on user's category preferences
                category_boost = 0
                for cat in preferred_categories:
                    if cat in result['content'].get('category', ''):
                        category_boost += 0.2
                
                # Adjust for price range preferences
                price_boost = 0
                product_price = result['content'].get('price', 0)
                for price_range in preferred_price_ranges:
                    if self._price_matches_range(product_price, price_range):
                        price_boost += 0.1
                
                final_score = base_score + category_boost + price_boost
                
                products.append({
                    **result,
                    "recommendation_score": final_score,
                    "reasons": {
                        "base_similarity": base_score,
                        "category_match": category_boost > 0,
                        "price_match": price_boost > 0
                    }
                })
        
        # Sort by recommendation score
        products.sort(key=lambda x: x['recommendation_score'], reverse=True)
        
        return products[:limit]
    
    async def get_trending_products(self, category: str = None, limit: int = 20) -> List[Dict]:
        """Get trending products based on recent user activity"""
        
        # Get recent user interactions
        recent_interactions = await self.sdk.search_memories(
            {
                "type": "user_interaction",
                "action": "purchase",
                "timestamp": {">": asyncio.get_event_loop().time() - (7 * 24 * 3600)}  # Last 7 days
            },
            1000
        )
        
        # Count product interactions
        product_counts = {}
        for interaction in recent_interactions:
            item_id = interaction['content']['item_id']
            if category and interaction['content'].get('category') != category:
                continue
                
            if item_id not in product_counts:
                product_counts[item_id] = {
                    'interactions': 0,
                    'purchases': 0,
                    'total_score': 0
                }
            
            product_counts[item_id]['interactions'] += 1
            product_counts[item_id]['total_score'] += interaction['score']
            
            if interaction['content']['action'] == 'purchase':
                product_counts[item_id]['purchases'] += 1
        
        # Get product details and calculate trending score
        trending_products = []
        for item_id, counts in product_counts.items():
            # Get product details
            product_results = await self.sdk.search_memories(
                {"id": item_id, "type": "product"},
                1
            )
            
            if product_results:
                product = product_results[0]
                trending_score = (
                    counts['purchases'] * 0.6 +
                    counts['interactions'] * 0.3 +
                    counts['total_score'] * 0.1
                )
                
                trending_products.append({
                    **product,
                    "trending_score": trending_score,
                    "interaction_count": counts['interactions'],
                    "purchase_count": counts['purchases']
                })
        
        trending_products.sort(key=lambda x: x['trending_score'], reverse=True)
        return trending_products[:limit]
    
    async def analyze_user_behavior(self, user_id: str) -> Dict[str, Any]:
        """Analyze user behavior patterns"""
        
        # Get user interactions
        user_interactions = await self.sdk.search_memories(
            {"user_id": user_id, "type": "user_interaction"},
            500
        )
        
        if not user_interactions:
            return {"error": "No interactions found for user"}
        
        # Analyze patterns
        analysis = {
            "user_id": user_id,
            "total_interactions": len(user_interactions),
            "action_breakdown": {},
            "category_preferences": {},
            "price_sensitivity": {},
            "session_patterns": {},
            "learning_insights": {}
        }
        
        # Count actions
        for interaction in user_interactions:
            action = interaction['content']['action']
            analysis["action_breakdown"][action] = analysis["action_breakdown"].get(action, 0) + 1
        
        # Analyze category preferences
        for interaction in user_interactions:
            category = interaction['content'].get('category', 'unknown')
            analysis["category_preferences"][category] = analysis["category_preferences"].get(category, 0) + 1
        
        # Analyze price sensitivity
        for interaction in user_interactions:
            price = interaction['content'].get('price', 0)
            price_range = self._get_price_range(price)
            analysis["price_sensitivity"][price_range] = analysis["price_sensitivity"].get(price_range, 0) + 1
        
        # Get AI insights
        reasoning = await self.sdk.reason(
            f"Analyze user {user_id}'s shopping behavior and provide insights",
            [f"user_{user_id}_preferences", "behavior_analysis"]
        )
        
        analysis["learning_insights"] = {
            "conclusion": reasoning.get('conclusion', ''),
            "confidence": reasoning.get('confidence', 0),
            "reasoning_path": reasoning.get('reasoning_path', [])
        }
        
        return analysis
    
    def _get_price_range(self, price: float) -> str:
        """Categorize price into ranges"""
        if price < 25:
            return "budget"
        elif price < 100:
            return "mid_range"
        elif price < 500:
            return "premium"
        else:
            return "luxury"
    
    def _price_matches_range(self, price: float, price_range: str) -> bool:
        """Check if price matches the specified range"""
        return self._get_price_range(price) == price_range

# Usage Example
async def main():
    engine = EcommerceRecommendationEngine()
    
    # Simulate user interactions
    user_id = "user_12345"
    
    # Track views
    await engine.track_user_action(user_id, "view", {
        "id": "laptop_001",
        "category": "electronics",
        "price": 1200,
        "rating": 4.5,
        "session_id": "session_001"
    })
    
    await engine.track_user_action(user_id, "add_to_cart", {
        "id": "laptop_001",
        "category": "electronics",
        "price": 1200,
        "rating": 4.5,
        "session_id": "session_001"
    })
    
    await engine.track_user_action(user_id, "purchase", {
        "id": "laptop_001",
        "category": "electronics",
        "price": 1200,
        "rating": 4.5,
        "session_id": "session_001"
    })
    
    # Get recommendations
    recommendations = await engine.get_personalized_recommendations(user_id, 5)
    print("Personalized Recommendations:")
    for rec in recommendations:
        print(f"- {rec['content']['name']} (Score: {rec['recommendation_score']:.2f})")
        print(f"  Reasons: {rec['reasons']}")
    
    # Get trending products
    trending = await engine.get_trending_products("electronics", 5)
    print("\nTrending Electronics:")
    for product in trending:
        print(f"- {product['content']['name']} (Trending: {product['trending_score']:.2f})")
    
    # Analyze user behavior
    behavior = await engine.analyze_user_behavior(user_id)
    print(f"\nUser Behavior Analysis:")
    print(f"Total interactions: {behavior['total_interactions']}")
    print(f"Top category: {max(behavior['category_preferences'], key=behavior['category_preferences'].get)}")
    print(f"AI Insights: {behavior['learning_insights']['conclusion']}")

if __name__ == "__main__":
    asyncio.run(main())
```

### Healthcare Information System

Build a healthcare system that learns from patient data and medical knowledge.

```javascript
// healthcare_information_system.js
import { BrainAISDK, BrainAIConfig } from 'brain-ai-sdk';

class HealthcareInformationSystem {
    constructor() {
        this.sdk = new BrainAISDK({
            baseUrl: 'http://localhost:8000',
            apiKey: 'healthcare-api-key',
            memorySize: 200000, // Large capacity for medical data
            similarityThreshold: 0.9 // High threshold for medical accuracy
        });
    }

    async recordPatientVisit(patientData) {
        const visitId = await this.sdk.storeMemory(
            {
                patient_id: patientData.id,
                visit_date: new Date().toISOString(),
                symptoms: patientData.symptoms,
                diagnosis: patientData.diagnosis,
                treatment: patientData.treatment,
                medications: patientData.medications,
                vital_signs: patientData.vitalSigns,
                doctor_notes: patientData.notes,
                follow_up_required: patientData.followUpRequired
            },
            'episodic',
            {
                type: 'patient_visit',
                patient_id: patientData.id,
                visit_type: patientData.visitType || 'consultation',
                priority: this._assessPriority(patientData.symptoms)
            }
        );

        // Learn from the case
        await this.sdk.learn('medical_case_pattern', [
            `diagnosis_${patientData.diagnosis}`,
            `symptoms_${patientData.symptoms.join('_')}`,
            `treatment_${patientData.treatment}`,
            `patient_demographics_${patientData.ageGroup}`
        ]);

        return visitId;
    }

    async searchMedicalKnowledge(query, filters = {}) {
        // Search for relevant medical information
        const results = await this.sdk.searchMemories(
            {
                ...query,
                type: 'medical_knowledge',
                ...filters
            },
            20
        );

        // Filter and rank results
        const medicalResults = results.filter(result => 
            result.metadata.type === 'medical_knowledge'
        );

        // Enhance results with medical relevance scoring
        return medicalResults.map(result => ({
            ...result,
            medical_relevance: this._calculateMedicalRelevance(result, query),
            evidence_level: result.content.evidence_level || 'case_study',
            last_updated: result.content.last_updated
        }));
    }

    async getDiagnosticSuggestions(symptoms, patientContext = {}) {
        // Use reasoning to suggest possible diagnoses
        const reasoning = await this.sdk.reason(
            'Based on these symptoms, what are the most likely diagnoses to consider?',
            [
                `symptoms_${symptoms.join('_')}`,
                `age_group_${patientContext.ageGroup || 'adult'}`,
                `medical_history_${patientContext.history || 'none'}`,
                'diagnostic_assistance'
            ]
        );

        // Get similar cases for comparison
        const similarCases = await this.sdk.searchMemories(
            {
                symptoms: symptoms,
                type: 'patient_visit'
            },
            10
        );

        const confirmedDiagnoses = similarCases
            .filter(case => case.content.diagnosis)
            .map(case => ({
                diagnosis: case.content.diagnosis,
                symptoms: case.content.symptoms,
                treatment: case.content.treatment,
                outcome: case.content.outcome || 'unknown',
                similarity: case.score
            }));

        return {
            ai_suggestions: {
                primary_suggestion: reasoning.conclusion,
                confidence: reasoning.confidence,
                reasoning_path: reasoning.reasoning_path
            },
            similar_cases: confirmedDiagnoses,
            recommended_tests: await this._getRecommendedTests(symptoms, reasoning.conclusion)
        };
    }

    async trackTreatmentOutcome(patientId, treatment, outcome, followUpData = {}) {
        const outcomeId = await this.sdk.storeMemory(
            {
                patient_id: patientId,
                treatment: treatment,
                outcome: outcome, // improved, stable, deteriorated, cured
                effectiveness_score: followUpData.effectivenessScore || 0,
                side_effects: followUpData.sideEffects || [],
                duration: followUpData.duration || 0,
                notes: followUpData.notes || '',
                follow_up_date: followUpData.followUpDate,
                timestamp: new Date().toISOString()
            },
            'episodic',
            {
                type: 'treatment_outcome',
                patient_id: patientId,
                treatment_type: treatment.type,
                outcome_category: outcome
            }
        );

        // Learn treatment effectiveness patterns
        await this.sdk.learn('treatment_effectiveness', [
            `treatment_${treatment.type}`,
            `outcome_${outcome}`,
            `patient_group_${followUpData.patientGroup || 'general'}`,
            `duration_${Math.floor((followUpData.duration || 0) / 7)}weeks`
        ]);

        // Provide feedback on treatment effectiveness
        const feedbackType = outcome === 'improved' || outcome === 'cured' ? 'positive' : 'negative';
        await this.sdk.addFeedback(feedbackType, 
            `Treatment ${treatment.type} for patient ${patientId} resulted in ${outcome}`,
            `Effectiveness score: ${followUpData.effectivenessScore || 0}/10`
        );

        return outcomeId;
    }

    async getPopulationHealthInsights(criteria = {}) {
        // Analyze population-level patterns
        const patterns = await this.sdk.getLearningPatterns();
        
        const healthPatterns = patterns.filter(pattern =>
            pattern.pattern.includes('medical_case') || 
            pattern.pattern.includes('treatment_effectiveness')
        );

        // Calculate insights
        const insights = {
            common_diagnoses: [],
            treatment_effectiveness: {},
            risk_factors: [],
            demographic_trends: {},
            recommendations: []
        };

        // Analyze diagnosis patterns
        const diagnosisCounts = {};
        healthPatterns.forEach(pattern => {
            if (pattern.pattern.includes('diagnosis_')) {
                const diagnosis = pattern.pattern.replace('diagnosis_', '');
                diagnosisCounts[diagnosis] = (diagnosisCounts[diagnosis] || 0) + pattern.frequency;
            }
        });

        insights.common_diagnoses = Object.entries(diagnosisCounts)
            .sort(([,a], [,b]) => b - a)
            .slice(0, 10)
            .map(([diagnosis, count]) => ({ diagnosis, count }));

        // Get AI-generated insights
        const reasoning = await this.sdk.reason(
            'Analyze population health trends and provide insights for public health planning',
            ['population_health', 'public_health_analysis', 'health_trends']
        );

        insights.ai_analysis = {
            conclusion: reasoning.conclusion,
            confidence: reasoning.confidence,
            key_trends: reasoning.reasoning_path
        };

        return insights;
    }

    async detectDrugInteractions(medications, patientHistory = {}) {
        const interactionResults = [];

        // Check each medication against known interactions
        for (let i = 0; i < medications.length; i++) {
            for (let j = i + 1; j < medications.length; j++) {
                const med1 = medications[i];
                const med2 = medications[j];

                const searchResults = await this.sdk.searchMemories(
                    {
                        medication1: med1.name,
                        medication2: med2.name,
                        type: 'drug_interaction'
                    },
                    5
                );

                if (searchResults.length > 0) {
                    const interaction = searchResults[0];
                    interactionResults.push({
                        medication1: med1,
                        medication2: med2,
                        severity: interaction.content.severity || 'moderate',
                        interaction_type: interaction.content.type || 'unknown',
                        clinical_effects: interaction.content.effects || [],
                        recommendation: interaction.content.recommendation || 'Monitor closely',
                        evidence_level: interaction.content.evidence_level || 'case_report'
                    });
                }
            }
        }

        // Sort by severity
        interactionResults.sort((a, b) => {
            const severityOrder = { 'severe': 3, 'moderate': 2, 'mild': 1 };
            return (severityOrder[b.severity] || 0) - (severityOrder[a.severity] || 0);
        });

        return interactionResults;
    }

    _assessPriority(symptoms) {
        // Simple priority assessment based on symptoms
        const highPrioritySymptoms = ['chest_pain', 'difficulty_breathing', 'severe_headache', 'loss_consciousness'];
        const mediumPrioritySymptoms = ['fever', 'persistent_cough', 'abdominal_pain'];

        if (symptoms.some(s => highPrioritySymptoms.includes(s))) {
            return 'high';
        } else if (symptoms.some(s => mediumPrioritySymptoms.includes(s))) {
            return 'medium';
        }
        return 'low';
    }

    _calculateMedicalRelevance(result, query) {
        // Calculate relevance score for medical content
        let relevance = result.score;

        // Boost for recent medical literature
        if (result.content.publication_date) {
            const daysSincePublication = (Date.now() - new Date(result.content.publication_date).getTime()) / (1000 * 60 * 60 * 24);
            if (daysSincePublication < 365) {
                relevance += 0.1; // Recent publications
            }
        }

        // Boost for high evidence levels
        const evidenceBoost = {
            'systematic_review': 0.3,
            'randomized_trial': 0.2,
            'cohort_study': 0.15,
            'case_control': 0.1,
            'case_report': 0.05
        };
        relevance += evidenceBoost[result.content.evidence_level] || 0;

        return Math.min(relevance, 1.0);
    }

    async _getRecommendedTests(symptoms, primaryDiagnosis) {
        // Search for recommended diagnostic tests
        const testResults = await this.sdk.searchMemories(
            {
                diagnosis: primaryDiagnosis,
                type: 'diagnostic_test',
                symptoms: symptoms
            },
            10
        );

        return testResults.map(result => ({
            test_name: result.content.test_name,
            indication: result.content.indication,
            urgency: result.content.urgency || 'routine',
            preparation: result.content.preparation || 'none'
        }));
    }
}

// Usage Example
async function main() {
    const healthcare = new HealthcareInformationSystem();

    // Record a patient visit
    const visitData = {
        id: 'patient_001',
        symptoms: ['fever', 'cough', 'fatigue'],
        diagnosis: 'upper_respiratory_infection',
        treatment: { type: 'antibiotics', medication: 'amoxicillin' },
        medications: ['amoxicillin'],
        vitalSigns: { temperature: 38.5, bp: '120/80', pulse: 85 },
        notes: 'Patient presenting with flu-like symptoms',
        ageGroup: 'adult',
        visitType: 'consultation'
    };

    const visitId = await healthcare.recordPatientVisit(visitData);
    console.log(`Recorded visit: ${visitId}`);

    // Get diagnostic suggestions
    const suggestions = await healthcare.getDiagnosticSuggestions(
        ['fever', 'cough', 'fatigue'],
        { ageGroup: 'adult', history: 'none' }
    );

    console.log('Diagnostic Suggestions:');
    console.log(`Primary: ${suggestions.ai_suggestions.primary_suggestion}`);
    console.log(`Confidence: ${suggestions.ai_suggestions.confidence.toFixed(2)}`);

    // Search medical knowledge
    const knowledge = await healthcare.searchMedicalKnowledge(
        { topic: 'respiratory_infections' },
        { evidence_level: 'systematic_review' }
    );

    console.log('\nRelevant Medical Knowledge:');
    knowledge.slice(0, 3).forEach(item => {
        console.log(`- ${item.content.title} (Relevance: ${item.medical_relevance.toFixed(2)})`);
    });

    // Track treatment outcome
    await healthcare.trackTreatmentOutcome('patient_001', 
        { type: 'antibiotics', medication: 'amoxicillin' },
        'improved',
        {
            effectivenessScore: 8,
            duration: 7,
            patientGroup: 'adult',
            notes: 'Symptoms resolved after 5 days'
        }
    );

    // Detect drug interactions
    const medications = [
        { name: 'warfarin', dosage: '5mg' },
        { name: 'aspirin', dosage: '81mg' }
    ];

    const interactions = await healthcare.detectDrugInteractions(medications);
    if (interactions.length > 0) {
        console.log('\nDrug Interactions Detected:');
        interactions.forEach(interaction => {
            console.log(`${interaction.severity}: ${interaction.medication1.name} + ${interaction.medication2.name}`);
            console.log(`Recommendation: ${interaction.recommendation}`);
        });
    }

    // Get population health insights
    const insights = await healthcare.getPopulationHealthInsights();
    console.log('\nPopulation Health Insights:');
    console.log(`Common diagnoses: ${insights.common_diagnoses.slice(0, 3).map(d => d.diagnosis).join(', ')}`);
    if (insights.ai_analysis) {
        console.log(`AI Analysis: ${insights.ai_analysis.conclusion}`);
    }
}

main().catch(console.error);
```

## 🔗 Integration Examples

### API Gateway Integration

Integrate Brain AI with existing API gateways for intelligent request routing.

```python
# api_gateway_integration.py
import asyncio
from typing import Dict, Any, List
from brain_ai import BrainAISDK, BrainAIConfig

class IntelligentAPIGateway:
    def __init__(self):
        config = BrainAIConfig(
            base_url="http://localhost:8000",
            memory_size=50000,
            learning_rate=0.1
        )
        self.sdk = BrainAISDK(config)
        
        # Service registry
        self.services = {
            "user_service": {"url": "http://user-service:8080", "health": True},
            "order_service": {"url": "http://order-service:8081", "health": True},
            "payment_service": {"url": "http://payment-service:8082", "health": False},
            "notification_service": {"url": "http://notification-service:8083", "health": True}
        }
    
    async def route_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Intelligently route requests based on learned patterns"""
        
        # Store request pattern
        await self.sdk.store_memory(
            content={
                "endpoint": request_data["endpoint"],
                "method": request_data["method"],
                "user_id": request_data.get("user_id"),
                "payload_size": len(str(request_data.get("payload", {}))),
                "timestamp": asyncio.get_event_loop().time(),
                "user_agent": request_data.get("user_agent", ""),
                "source_ip": request_data.get("source_ip", "")
            },
            type="episodic",
            metadata={
                "type": "api_request",
                "endpoint_category": self._categorize_endpoint(request_data["endpoint"])
            }
        )
        
        # Learn request patterns
        await self.sdk.learn(
            "api_request_pattern",
            [
                f"method_{request_data['method']}",
                f"endpoint_{request_data['endpoint']}",
                f"category_{self._categorize_endpoint(request_data['endpoint'])}"
            ]
        )
        
        # Determine optimal service
        service_decision = await self._select_service(request_data)
        
        # Add routing intelligence
        routing_info = {
            "selected_service": service_decision["service"],
            "confidence": service_decision["confidence"],
            "reasoning": service_decision["reasoning"],
            "load_balancing": service_decision.get("load_balancing", "round_robin"),
            "caching_strategy": service_decision.get("caching", "none")
        }
        
        return routing_info
    
    async def _select_service(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Select the best service for the request"""
        
        endpoint = request_data["endpoint"]
        user_id = request_data.get("user_id")
        
        # Check service health
        healthy_services = [
            name for name, info in self.services.items() 
            if info["health"]
        ]
        
        if not healthy_services:
            return {
                "service": "fallback_service",
                "confidence": 0.1,
                "reasoning": "No healthy services available"
            }
        
        # Use AI to make routing decision
        reasoning = await self.sdk.reason(
            f"Which service should handle this {endpoint} request?",
            [
                f"endpoint_{endpoint}",
                f"user_{user_id}" if user_id else "anonymous_user",
                "service_selection"
            ]
        )
        
        # Map endpoint to likely service
        service_mapping = {
            "/api/users": "user_service",
            "/api/orders": "order_service", 
            "/api/payments": "payment_service",
            "/api/notifications": "notification_service"
        }
        
        selected_service = None
        for pattern, service in service_mapping.items():
            if endpoint.startswith(pattern):
                selected_service = service
                break
        
        if not selected_service:
            selected_service = healthy_services[0]  # Default to first healthy service
        
        # Check if selected service is healthy
        if not self.services[selected_service]["health"]:
            selected_service = healthy_services[0]  # Fallback to first healthy
        
        return {
            "service": selected_service,
            "confidence": reasoning.get("confidence", 0.7),
            "reasoning": reasoning.get("conclusion", f"Routing {endpoint} to {selected_service}"),
            "load_balancing": "least_connections" if selected_service == "payment_service" else "round_robin",
            "caching": "redis" if endpoint.startswith("/api/users") else "none"
        }
    
    async def learn_from_response(self, request_data: Dict[str, Any], response_data: Dict[str, Any]):
        """Learn from API responses to improve routing"""
        
        # Analyze response patterns
        response_quality = self._assess_response_quality(response_data)
        
        await self.sdk.learn(
            "response_quality_pattern",
            [
                f"status_{response_data.get('status_code', 200)}",
                f"response_time_{self._categorize_response_time(response_data.get('response_time', 0))}",
                f"quality_{response_quality}"
            ]
        )
        
        # Learn from errors
        if response_data.get("status_code", 200) >= 400:
            await self.sdk.add_feedback(
                "negative",
                f"API request to {request_data['endpoint']} failed with status {response_data.get('status_code')}",
                f"Service: {request_data.get('selected_service')}, Error: {response_data.get('error_message')}"
            )
        elif response_quality == "high":
            await self.sdk.add_feedback(
                "positive",
                f"API request to {request_data['endpoint']} completed successfully",
                f"Response time: {response_data.get('response_time', 0)}ms"
            )
    
    async def optimize_service_health(self):
        """Continuously optimize service health based on patterns"""
        
        patterns = await self.sdk.get_learning_patterns()
        
        # Analyze error patterns
        error_patterns = [
            p for p in patterns 
            if "negative" in p.get('context', []) and p['strength'] > 0.7
        ]
        
        for pattern in error_patterns:
            # Extract service information
            service_info = pattern['context']
            failed_services = [ctx for ctx in service_info if ctx.endswith('_service')]
            
            for service_name in failed_services:
                if service_name in self.services:
                    # Mark service as unhealthy if error rate is high
                    self.services[service_name]["health"] = False
                    print(f"Marked {service_name} as unhealthy due to error patterns")
        
        # Periodically check service health
        await self._check_service_health()
    
    def _categorize_endpoint(self, endpoint: str) -> str:
        """Categorize API endpoints"""
        if endpoint.startswith("/api/users"):
            return "user_management"
        elif endpoint.startswith("/api/orders"):
            return "order_processing"
        elif endpoint.startswith("/api/payments"):
            return "payment_processing"
        elif endpoint.startswith("/api/notifications"):
            return "notification_delivery"
        else:
            return "general"
    
    def _assess_response_quality(self, response_data: Dict[str, Any]) -> str:
        """Assess the quality of API response"""
        status_code = response_data.get("status_code", 200)
        response_time = response_data.get("response_time", 0)
        
        if status_code >= 400:
            return "poor"
        elif response_time > 2000:
            return "slow"
        elif status_code == 200 and response_time < 500:
            return "high"
        else:
            return "acceptable"
    
    def _categorize_response_time(self, response_time: float) -> str:
        """Categorize response time"""
        if response_time < 100:
            return "fast"
        elif response_time < 500:
            return "normal"
        elif response_time < 2000:
            return "slow"
        else:
            return "very_slow"
    
    async def _check_service_health(self):
        """Check health of all registered services"""
        import aiohttp
        
        async with aiohttp.ClientSession() as session:
            for service_name, service_info in self.services.items():
                try:
                    async with session.get(f"{service_info['url']}/health") as response:
                        if response.status == 200:
                            self.services[service_name]["health"] = True
                        else:
                            self.services[service_name]["health"] = False
                except Exception:
                    self.services[service_name]["health"] = False

# Usage Example
async def main():
    gateway = IntelligentAPIGateway()
    
    # Simulate API requests
    requests = [
        {
            "endpoint": "/api/users/profile",
            "method": "GET",
            "user_id": "user_123",
            "user_agent": "Mozilla/5.0",
            "source_ip": "192.168.1.100"
        },
        {
            "endpoint": "/api/orders/create",
            "method": "POST",
            "user_id": "user_123",
            "payload": {"items": [{"id": "item1", "quantity": 2}]}
        },
        {
            "endpoint": "/api/payments/process",
            "method": "POST", 
            "user_id": "user_123",
            "payload": {"amount": 99.99, "currency": "USD"}
        }
    ]
    
    for request_data in requests:
        # Route the request
        routing_info = await gateway.route_request(request_data)
        print(f"Request to {request_data['endpoint']}:")
        print(f"  Service: {routing_info['selected_service']}")
        print(f"  Confidence: {routing_info['confidence']:.2f}")
        print(f"  Load Balancing: {routing_info['load_balancing']}")
        
        # Simulate response
        response_data = {
            "status_code": 200,
            "response_time": 150,
            "data": {"success": True}
        }
        
        # Learn from response
        await gateway.learn_from_response(request_data, response_data)
    
    # Optimize service health
    await gateway.optimize_service_health()
    print("\nService Health Status:")
    for service, info in gateway.services.items():
        status = "✅ Healthy" if info["health"] else "❌ Unhealthy"
        print(f"  {service}: {status}")

if __name__ == "__main__":
    asyncio.run(main())
```

## 📊 Performance Optimization

### Caching Strategy

Implement intelligent caching based on access patterns.

```python
# intelligent_caching.py
import asyncio
import hashlib
from typing import Any, Optional, Dict, List
from brain_ai import BrainAISDK, BrainAIConfig

class IntelligentCache:
    def __init__(self, brain_ai_sdk: BrainAISDK):
        self.sdk = brain_ai_sdk
        self.cache_ttl = {
            "user_profile": 3600,      # 1 hour
            "product_catalog": 1800,   # 30 minutes
            "static_content": 86400,   # 24 hours
            "dynamic_content": 300     # 5 minutes
        }
        
    async def get_cached_data(self, cache_key: str, content_type: str) -> Optional[Dict[str, Any]]:
        """Retrieve data from cache with smart invalidation"""
        
        # Search for cached item
        cached_items = await self.sdk.search_memories(
            {
                "cache_key": cache_key,
                "content_type": content_type,
                "type": "cached_data"
            },
            1
        )
        
        if not cached_items:
            return None
        
        cached_item = cached_items[0]
        
        # Check if cache is still valid
        cache_age = asyncio.get_event_loop().time() - cached_item['content']['timestamp']
        max_age = self.cache_ttl.get(content_type, 3600)
        
        if cache_age > max_age:
            # Cache expired, invalidate
            await self.sdk.delete_memory(cached_item['id'])
            return None
        
        # Check if underlying data has changed
        if await self._is_data_stale(cached_item):
            await self.sdk.delete_memory(cached_item['id'])
            return None
        
        return cached_item['content']['data']
    
    async def set_cached_data(self, cache_key: str, data: Any, content_type: str, metadata: Dict = None):
        """Store data in cache with metadata"""
        
        memory_id = await self.sdk.store_memory(
            content={
                "cache_key": cache_key,
                "data": data,
                "content_type": content_type,
                "timestamp": asyncio.get_event_loop().time(),
                "metadata": metadata or {},
                "size_bytes": len(str(data))
            },
            type="semantic",
            metadata={
                "type": "cached_data",
                "content_type": content_type,
                "cache_key": cache_key
            }
        )
        
        # Learn cache access patterns
        await self.sdk.learn(
            f"cache_access_{content_type}",
            [
                f"content_type_{content_type}",
                f"cache_key_hash_{hashlib.md5(cache_key.encode()).hexdigest()[:8]}",
                "cache_storage"
            ]
        )
        
        return memory_id
    
    async def invalidate_cache_pattern(self, pattern: str, content_type: str = None):
        """Invalidate cache based on patterns"""
        
        # Find all cached items matching the pattern
        search_query = {
            "cache_key": {"$regex": pattern},
            "type": "cached_data"
        }
        
        if content_type:
            search_query["content_type"] = content_type
        
        cached_items = await self.sdk.search_memories(search_query, 100)
        
        # Invalidate matching items
        for item in cached_items:
            await self.sdk.delete_memory(item['id'])
            
        return len(cached_items)
    
    async def get_cache_statistics(self) -> Dict[str, Any]:
        """Get cache performance statistics"""
        
        patterns = await self.sdk.get_learning_patterns()
        cache_patterns = [p for p in patterns if "cache_access_" in p['pattern']]
        
        stats = {
            "total_cache_patterns": len(cache_patterns),
            "cache_hit_predictions": [],
            "invalidation_suggestions": [],
            "optimization_recommendations": []
        }
        
        # Analyze cache hit patterns
        for pattern in cache_patterns:
            if pattern['strength'] > 0.8:
                stats["cache_hit_predictions"].append({
                    "content_type": pattern['pattern'].replace("cache_access_", ""),
                    "hit_probability": pattern['strength'],
                    "frequency": pattern['frequency']
                })
        
        # Generate optimization recommendations
        reasoning = await self.sdk.reason(
            "Analyze cache patterns and suggest optimizations",
            ["cache_optimization", "performance_analysis"]
        )
        
        stats["ai_recommendations"] = {
            "conclusion": reasoning.get('conclusion', ''),
            "confidence": reasoning.get('confidence', 0)
        }
        
        return stats
    
    async def _is_data_stale(self, cached_item: Dict[str, Any]) -> bool:
        """Check if cached data is stale based on external factors"""
        
        content_type = cached_item['content']['content_type']
        metadata = cached_item['content']['metadata']
        
        # Check for data version mismatches
        if 'data_version' in metadata:
            current_version = await self._get_current_data_version(content_type)
            cached_version = metadata['data_version']
            
            if current_version != cached_version:
                return True
        
        # Check for dependency invalidation
        dependencies = metadata.get('dependencies', [])
        for dependency in dependencies:
            dep_cache_key = f"dependency_{dependency}"
            dep_cached = await self.sdk.search_memories(
                {"cache_key": dep_cache_key, "type": "cached_data"},
                1
            )
            
            if not dep_cached:
                return True  # Dependency not cached, might be stale
        
        return False
    
    async def _get_current_data_version(self, content_type: str) -> str:
        """Get current version of data (simulated)"""
        # In practice, this would query the actual data source
        version_map = {
            "user_profile": "v2.1",
            "product_catalog": "v1.8", 
            "static_content": "v1.0",
            "dynamic_content": "v3.2"
        }
        return version_map.get(content_type, "v1.0")

# Usage Example
async def main():
    config = BrainAIConfig("http://localhost:8000")
    sdk = BrainAISDK(config)
    cache = IntelligentCache(sdk)
    
    # Cache user profile
    user_data = {
        "user_id": "12345",
        "name": "John Doe",
        "email": "john@example.com",
        "preferences": {"theme": "dark", "language": "en"}
    }
    
    cache_key = "user_profile_12345"
    await cache.set_cached_data(cache_key, user_data, "user_profile", {
        "data_version": "v2.1",
        "dependencies": ["user_settings_12345"]
    })
    
    # Retrieve from cache
    cached_data = await cache.get_cached_data(cache_key, "user_profile")
    if cached_data:
        print("✅ Cache hit!")
        print(f"User: {cached_data['name']}")
    else:
        print("❌ Cache miss")
    
    # Get cache statistics
    stats = await cache.get_cache_statistics()
    print(f"\nCache Statistics:")
    print(f"Total patterns: {stats['total_cache_patterns']}")
    print(f"Hit predictions: {len(stats['cache_hit_predictions'])}")
    
    # Invalidate cache pattern
    invalidated = await cache.invalidate_cache_pattern("user_profile_.*", "user_profile")
    print(f"\nInvalidated {invalidated} cache entries")

if __name__ == "__main__":
    asyncio.run(main())
```

## 🌍 Multi-Language Examples

The following examples show the same application implemented in different languages:

### Todo Application Comparison

```python
# Python version
import asyncio
from brain_ai import BrainAISDK

class TodoApp:
    def __init__(self):
        self.sdk = BrainAISDK(BrainAIConfig())
    
    async def add_todo(self, title, priority="medium"):
        return await self.sdk.store_memory(
            {"title": title, "priority": priority, "completed": False},
            "episodic"
        )
    
    async def get_todos(self):
        return await self.sdk.search_memories({"completed": False}, 50)

# Run the app
async def main():
    app = TodoApp()
    todo_id = await app.add_todo("Learn Brain AI", "high")
    todos = await app.get_todos()
    print(f"Found {len(todos)} todos")

asyncio.run(main())
```

```javascript
// JavaScript version
import { BrainAISDK } from 'brain-ai-sdk';

class TodoApp {
    constructor() {
        this.sdk = new BrainAISDK();
    }
    
    async addTodo(title, priority = "medium") {
        return await this.sdk.storeMemory(
            { title, priority, completed: false },
            'episodic'
        );
    }
    
    async getTodos() {
        return await this.sdk.searchMemories({ completed: false }, 50);
    }
}

// Run the app
const app = new TodoApp();
app.addTodo("Learn Brain AI", "high")
    .then(() => app.getTodos())
    .then(todos => console.log(`Found ${todos.length} todos`));
```

```java
// Java version
import com.brainai.sdk.BrainAISDK;
import java.util.*;

public class TodoApp {
    private BrainAISDK sdk;
    
    public TodoApp() {
        this.sdk = new BrainAISDK(BrainAIConfig.builder().build());
    }
    
    public CompletableFuture<String> addTodo(String title, String priority) {
        Map<String, Object> todo = new HashMap<>();
        todo.put("title", title);
        todo.put("priority", priority);
        todo.put("completed", false);
        
        return sdk.storeMemory(todo, MemoryType.EPISODIC, null);
    }
    
    public CompletableFuture<List<Map<String, Object>>> getTodos() {
        Map<String, Object> query = new HashMap<>();
        query.put("completed", false);
        
        return sdk.searchMemories(query, 50);
    }
}

// Usage
TodoApp app = new TodoApp();
app.addTodo("Learn Brain AI", "high")
    .thenCompose(id -> app.getTodos())
    .thenAccept(todos -> System.out.println("Found " + todos.size() + " todos"));
```

---

*These examples demonstrate the versatility and power of Brain AI across different use cases and programming languages. Each implementation maintains the same core functionality while leveraging language-specific features and patterns.*