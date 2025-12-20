/**
 * Brain-Inspired AI Framework JavaScript/TypeScript SDK
 * Easy-to-use JavaScript client for the Brain-Inspired AI Framework.
 */

import axios, { AxiosInstance, AxiosRequestConfig } from 'axios';

// TypeScript interfaces
export interface Memory {
  id: string;
  pattern_signature: string;
  memory_type: string;
  content: Record<string, any>;
  context: Record<string, any>;
  strength: number;
  access_count: number;
  last_accessed: string;
  created_at: string;
  associations: string[];
  tags: string[];
  confidence: number;
}

export interface ReasoningResult {
  result: string;
  confidence: number;
  reasoning_type: string;
  execution_time: number;
  tokens_used: number;
  timestamp: string;
  metadata: Record<string, any>;
}

export interface ProcessingResult {
  encoded_event: Record<string, any>;
  active_memories: Memory[];
  reasoning_result: ReasoningResult;
  memory_count: number;
  execution_time: number;
  processing_metadata: Record<string, any>;
}

export interface SystemStatus {
  status: string;
  brain_initialized: boolean;
  uptime: number;
  memory_count: number;
  total_operations: number;
  health_check: Record<string, any>;
}

export interface BrainAIConfig {
  apiKey?: string;
  baseURL?: string;
  timeout?: number;
  retries?: number;
}

export class BrainAI {
  private client: AxiosInstance;
  private config: Required<BrainAIConfig>;

  constructor(config: BrainAIConfig = {}) {
    this.config = {
      apiKey: config.apiKey || '',
      baseURL: config.baseURL || 'http://localhost:8000',
      timeout: config.timeout || 30000,
      retries: config.retries || 3,
      ...config
    };

    this.client = axios.create({
      baseURL: `${this.config.baseURL}/api/v1`,
      timeout: this.config.timeout,
      headers: {
        'Content-Type': 'application/json',
        ...(this.config.apiKey && { 'Authorization': `Bearer ${this.config.apiKey}` })
      }
    });

    // Add request interceptor for retries
    this.client.interceptors.response.use(
      (response) => response,
      async (error) => {
        const config = error.config;
        if (!config || config.__retryCount >= this.config.retries) {
          return Promise.reject(error);
        }

        config.__retryCount = (config.__retryCount || 0) + 1;
        
        // Wait before retrying
        await new Promise(resolve => setTimeout(resolve, 1000 * config.__retryCount));
        
        return this.client(config);
      }
    );
  }

  /**
   * Check system health
   */
  async healthCheck(): Promise<Record<string, any>> {
    try {
      const response = await this.client.get('/health');
      return response.data;
    } catch (error) {
      console.error('Health check failed:', error);
      throw error;
    }
  }

  /**
   * Process input through the brain system
   */
  async process(
    data: Record<string, any>,
    context?: Record<string, any>,
    reasoningType: string = 'analysis'
  ): Promise<ProcessingResult> {
    try {
      const payload = {
        data,
        context: context || {},
        reasoning_type: reasoningType
      };

      const response = await this.client.post('/process', payload);
      const result = response.data;

      // Convert to typed objects
      const activeMemories: Memory[] = (result.active_memories || []).map((memory: any) => ({
        ...memory,
        last_accessed: new Date(memory.last_accessed).toISOString(),
        created_at: new Date(memory.created_at).toISOString()
      }));

      const reasoningResult: ReasoningResult = {
        ...result.reasoning_result,
        timestamp: new Date(result.reasoning_result.timestamp).toISOString()
      };

      return {
        encoded_event: result.encoded_event || {},
        active_memories: activeMemories,
        reasoning_result: reasoningResult,
        memory_count: result.memory_count || 0,
        execution_time: result.execution_time || 0,
        processing_metadata: result.processing_metadata || {}
      };
    } catch (error) {
      console.error('Processing failed:', error);
      throw error;
    }
  }

  /**
   * Simple thinking interface
   */
  async think(query: string, context?: Record<string, any>): Promise<string> {
    const result = await this.process(
      { query },
      context,
      'analysis'
    );
    return result.reasoning_result.result;
  }

  /**
   * Explain a decision using memory
   */
  async explain(decision: string, context?: Record<string, any>): Promise<Record<string, any>> {
    try {
      const payload = {
        decision,
        context: context || {}
      };

      const response = await this.client.post('/explain', payload);
      return response.data;
    } catch (error) {
      console.error('Explanation failed:', error);
      throw error;
    }
  }

  /**
   * Make a prediction based on current situation
   */
  async predict(
    situation: Record<string, any>,
    timeHorizon: string = 'near_term'
  ): Promise<Record<string, any>> {
    try {
      const payload = {
        situation,
        time_horizon: timeHorizon
      };

      const response = await this.client.post('/predict', payload);
      return response.data;
    } catch (error) {
      console.error('Prediction failed:', error);
      throw error;
    }
  }

  /**
   * Create an action plan to achieve a goal
   */
  async plan(goal: string, constraints?: string[]): Promise<Record<string, any>> {
    try {
      const payload = {
        goal,
        constraints: constraints || []
      };

      const response = await this.client.post('/plan', payload);
      return response.data;
    } catch (error) {
      console.error('Plan creation failed:', error);
      throw error;
    }
  }

  /**
   * Get current memories
   */
  async getMemories(limit: number = 100): Promise<Memory[]> {
    try {
      const response = await this.client.get(`/memories?limit=${limit}`);
      const memories = response.data.memories || [];
      
      return memories.map((memory: any) => ({
        ...memory,
        last_accessed: new Date(memory.last_accessed).toISOString(),
        created_at: new Date(memory.created_at).toISOString()
      }));
    } catch (error) {
      console.error('Failed to get memories:', error);
      throw error;
    }
  }

  /**
   * Get comprehensive system status
   */
  async getStatus(): Promise<SystemStatus> {
    try {
      const response = await this.client.get('/status');
      const data = response.data;

      return {
        status: data.status || 'unknown',
        brain_initialized: data.brain_system?.initialized || false,
        uptime: data.uptime || 0,
        memory_count: data.brain_system?.memory_count || 0,
        total_operations: data.statistics?.total_operations || 0,
        health_check: data.statistics?.health_check || {}
      };
    } catch (error) {
      console.error('Failed to get status:', error);
      throw error;
    }
  }

  /**
   * Run system test
   */
  async test(): Promise<Record<string, any>> {
    try {
      const response = await this.client.post('/test');
      return response.data;
    } catch (error) {
      console.error('System test failed:', error);
      throw error;
    }
  }

  // Convenience methods for common use cases

  /**
   * Simple chat interface
   */
  async chat(
    message: string,
    conversationHistory?: Array<{ role: string; content: string }>
  ): Promise<string> {
    const context: Record<string, any> = { chat_mode: true };
    if (conversationHistory) {
      context.conversation_history = conversationHistory;
    }

    const result = await this.process(
      { message, type: 'chat' },
      context,
      'analysis'
    );

    return result.reasoning_result.result;
  }

  /**
   * Analyze text content
   */
  async analyzeText(text: string, analysisType: string = 'general'): Promise<Record<string, any>> {
    const result = await this.process(
      { text, analysis_type: analysisType },
      { source: 'text_analysis' },
      'analysis'
    );

    return {
      analysis: result.reasoning_result.result,
      active_memories: result.active_memories.map(m => m.pattern_signature),
      confidence: result.reasoning_result.confidence,
      processing_time: result.execution_time
    };
  }

  /**
   * Make a recommendation based on user profile and context
   */
  async makeRecommendation(
    userProfile: Record<string, any>,
    context: Record<string, any>,
    recommendationType: string = 'general'
  ): Promise<Record<string, any>> {
    const result = await this.process(
      {
        user_profile: userProfile,
        recommendation_type: recommendationType
      },
      context,
      'analysis'
    );

    return {
      recommendation: result.reasoning_result.result,
      confidence: result.reasoning_result.confidence,
      supporting_memories: result.active_memories.length,
      reasoning_trace: result.reasoning_result.metadata
    };
  }

  /**
   * Get insights based on query and time range
   */
  async getInsights(query: string, timeRange?: string): Promise<Record<string, any>> {
    const context: Record<string, any> = { insight_mode: true };
    if (timeRange) {
      context.time_range = timeRange;
    }

    const result = await this.process(
      { insight_query: query },
      context,
      'analysis'
    );

    return {
      insights: result.reasoning_result.result,
      related_memories: result.active_memories.map(m => ({
        pattern: m.pattern_signature,
        strength: m.strength,
        type: m.memory_type
      })),
      confidence: result.reasoning_result.confidence
    };
  }

  /**
   * Provide feedback to help the AI learn
   */
  async learn(
    experience: string,
    feedback: string | Record<string, any>,
    outcome?: Record<string, any>
  ): Promise<void> {
    // For now, this is a placeholder - the full learning interface
    // would need access to specific memory IDs
    console.log('Learning from experience:', experience);
    console.log('Feedback:', feedback);
    
    // In a full implementation, you would:
    // 1. Identify relevant memories
    // 2. Process feedback through the feedback API
    // 3. Update memory strengths
  }

  /**
   * Batch process multiple inputs
   */
  async batchProcess(
    inputs: Array<{ data: Record<string, any>; context?: Record<string, any> }>,
    parallel: boolean = true
  ): Promise<ProcessingResult[]> {
    const promises = inputs.map(input => this.process(input.data, input.context));
    
    if (parallel) {
      return Promise.all(promises);
    } else {
      const results: ProcessingResult[] = [];
      for (const promise of promises) {
        results.push(await promise);
      }
      return results;
    }
  }

  /**
   * Search memories by pattern
   */
  async searchMemories(
    query: string,
    limit: number = 10,
    minStrength: number = 0.1
  ): Promise<Memory[]> {
    const allMemories = await this.getMemories(1000); // Get more memories to search
    
    // Simple text-based search (in production, use semantic search)
    const queryLower = query.toLowerCase();
    const matchingMemories = allMemories.filter(memory => {
      const matchesPattern = memory.pattern_signature.toLowerCase().includes(queryLower);
      const matchesContent = JSON.stringify(memory.content).toLowerCase().includes(queryLower);
      const matchesStrength = memory.strength >= minStrength;
      
      return (matchesPattern || matchesContent) && matchesStrength;
    });

    // Sort by strength and limit results
    return matchingMemories
      .sort((a, b) => b.strength - a.strength)
      .slice(0, limit);
  }

  /**
   * Get memory statistics
   */
  async getMemoryStats(): Promise<Record<string, any>> {
    const memories = await this.getMemories(1000);
    
    const stats = {
      total_memories: memories.length,
      memory_types: {} as Record<string, number>,
      average_strength: 0,
      total_access_count: 0,
      most_accessed_memories: [] as Memory[],
      strongest_memories: [] as Memory[]
    };

    // Calculate statistics
    let totalStrength = 0;
    let totalAccess = 0;

    memories.forEach(memory => {
      // Count by type
      stats.memory_types[memory.memory_type] = (stats.memory_types[memory.memory_type] || 0) + 1;
      
      // Sum for averages
      totalStrength += memory.strength;
      totalAccess += memory.access_count;
    });

    stats.average_strength = memories.length > 0 ? totalStrength / memories.length : 0;
    stats.total_access_count = totalAccess;

    // Get top memories
    stats.most_accessed_memories = memories
      .sort((a, b) => b.access_count - a.access_count)
      .slice(0, 10);

    stats.strongest_memories = memories
      .sort((a, b) => b.strength - a.strength)
      .slice(0, 10);

    return stats;
  }
}

// Convenience function for quick start
export function createBrainAI(config: BrainAIConfig = {}): BrainAI {
  return new BrainAI(config);
}

// Export types for TypeScript users
export type {
  Memory,
  ReasoningResult,
  ProcessingResult,
  SystemStatus,
  BrainAIConfig
};

// Example usage
export async function exampleUsage(): Promise<void> {
  // Initialize Brain AI
  const brain = new BrainAI({
    baseURL: 'http://localhost:8000',
    apiKey: 'your-api-key' // optional
  });

  try {
    // Check health
    const health = await brain.healthCheck();
    console.log('System health:', health);

    // Process some input
    const result = await brain.process({
      user_input: 'I need help with machine learning',
      context: 'learning'
    });

    console.log('AI response:', result.reasoning_result.result);
    console.log('Active memories:', result.active_memories.length);

    // Get system status
    const status = await brain.getStatus();
    console.log('System status:', status.status);

    // Simple chat
    const chatResponse = await brain.chat('Hello, how can you help me?');
    console.log('Chat response:', chatResponse);

    // Analyze text
    const analysis = await brain.analyzeText('This is a sample text for analysis.');
    console.log('Text analysis:', analysis);

    // Get insights
    const insights = await brain.getInsights('What patterns do you see in the data?');
    console.log('Insights:', insights);

  } catch (error) {
    console.error('Error:', error);
  }
}

// Node.js compatibility
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    BrainAI,
    createBrainAI,
    exampleUsage,
    Memory,
    ReasoningResult,
    ProcessingResult,
    SystemStatus,
    BrainAIConfig
  };
}

// Browser compatibility
if (typeof window !== 'undefined') {
  (window as any).BrainAI = {
    BrainAI,
    createBrainAI,
    exampleUsage
  };
}