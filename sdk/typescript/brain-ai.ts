/**
 * Brain AI Framework - TypeScript SDK
 * Brain-inspired AI system with persistent memory, learning, and reasoning
 * 
 * @author MiniMax Agent
 * @version 1.0.0
 * @license MIT
 */

export interface MemoryNode {
  id: string;
  content: any;
  type: 'episodic' | 'semantic' | 'procedural' | 'emotional';
  strength: number;
  timestamp: number;
  connections: string[];
  metadata: Record<string, any>;
}

export interface LearningPattern {
  pattern: string;
  frequency: number;
  strength: number;
  context: string[];
  lastUpdated: number;
}

export interface ReasoningResult {
  conclusion: string;
  confidence: number;
  reasoning_path: string[];
  supporting_evidence: string[];
  timestamp: number;
}

export interface VectorEntry {
  id: string;
  vector: number[];
  metadata: Record<string, any>;
  timestamp: number;
}

export interface GraphNode {
  id: string;
  label: string;
  type: string;
  properties: Record<string, any>;
  connections: string[];
  weight: number;
}

export interface BrainAIConfig {
  baseUrl: string;
  apiKey?: string;
  timeout: number;
  memorySize: number;
  learningRate: number;
  similarityThreshold: number;
  maxReasoningDepth: number;
}

export interface SearchResult {
  id: string;
  score: number;
  content: any;
  metadata: Record<string, any>;
}

export class BrainAISDK {
  private config: BrainAIConfig;
  private baseUrl: string;

  constructor(config: BrainAIConfig) {
    this.config = {
      baseUrl: config.baseUrl,
      apiKey: config.apiKey,
      timeout: config.timeout || 30000,
      memorySize: config.memorySize || 10000,
      learningRate: config.learningRate || 0.1,
      similarityThreshold: config.similarityThreshold || 0.7,
      maxReasoningDepth: config.maxReasoningDepth || 5,
      ...config
    };
    this.baseUrl = this.config.baseUrl.replace(/\/$/, '');
  }

  private async makeRequest(endpoint: string, method: string = 'GET', data?: any): Promise<any> {
    const url = `${this.baseUrl}${endpoint}`;
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };

    if (this.config.apiKey) {
      headers['Authorization'] = `Bearer ${this.config.apiKey}`;
    }

    const options: RequestInit = {
      method,
      headers,
      signal: AbortSignal.timeout(this.config.timeout)
    };

    if (data) {
      options.body = JSON.stringify(data);
    }

    try {
      const response = await fetch(url, options);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error(`Request failed: ${error}`);
      throw error;
    }
  }

  /**
   * Store a memory node in the brain
   */
  async storeMemory(content: any, type: MemoryNode['type'] = 'semantic', metadata?: Record<string, any>): Promise<string> {
    const memoryNode: Partial<MemoryNode> = {
      content,
      type,
      strength: 1.0,
      timestamp: Date.now(),
      connections: [],
      metadata: metadata || {}
    };

    const result = await this.makeRequest('/api/memory', 'POST', memoryNode);
    return result.id;
  }

  /**
   * Retrieve memory by ID
   */
  async getMemory(id: string): Promise<MemoryNode | null> {
    try {
      return await this.makeRequest(`/api/memory/${id}`);
    } catch (error) {
      console.error(`Failed to get memory: ${error}`);
      return null;
    }
  }

  /**
   * Search memories by content similarity
   */
  async searchMemories(query: any, limit: number = 10): Promise<SearchResult[]> {
    const result = await this.makeRequest('/api/memory/search', 'POST', {
      query,
      limit,
      threshold: this.config.similarityThreshold
    });
    return result.results || [];
  }

  /**
   * Connect two memories
   */
  async connectMemories(memoryId1: string, memoryId2: string, strength: number = 0.5): Promise<boolean> {
    try {
      await this.makeRequest('/api/memory/connect', 'POST', {
        memoryId1,
        memoryId2,
        strength
      });
      return true;
    } catch (error) {
      console.error(`Failed to connect memories: ${error}`);
      return false;
    }
  }

  /**
   * Update memory strength
   */
  async updateMemoryStrength(id: string, delta: number): Promise<boolean> {
    try {
      await this.makeRequest(`/api/memory/${id}/strength`, 'PATCH', { delta });
      return true;
    } catch (error) {
      console.error(`Failed to update memory strength: ${error}`);
      return false;
    }
  }

  /**
   * Learn from experience
   */
  async learn(pattern: string, context: string[] = []): Promise<boolean> {
    try {
      await this.makeRequest('/api/learning/learn', 'POST', {
        pattern,
        context,
        rate: this.config.learningRate
      });
      return true;
    } catch (error) {
      console.error(`Failed to learn: ${error}`);
      return false;
    }
  }

  /**
   * Get learning patterns
   */
  async getLearningPatterns(): Promise<LearningPattern[]> {
    const result = await this.makeRequest('/api/learning/patterns');
    return result.patterns || [];
  }

  /**
   * Perform reasoning on a query
   */
  async reason(query: string, context?: string[]): Promise<ReasoningResult> {
    const result = await this.makeRequest('/api/reasoning/reason', 'POST', {
      query,
      context: context || [],
      maxDepth: this.config.maxReasoningDepth
    });
    return result;
  }

  /**
   * Add feedback for learning
   */
  async addFeedback(type: 'positive' | 'negative' | 'neutral', information: string, reasoning?: string): Promise<boolean> {
    try {
      await this.makeRequest('/api/feedback', 'POST', {
        type,
        information,
        reasoning,
        timestamp: Date.now()
      });
      return true;
    } catch (error) {
      console.error(`Failed to add feedback: ${error}`);
      return false;
    }
  }

  /**
   * Store vector for similarity search
   */
  async storeVector(vector: number[], metadata?: Record<string, any>): Promise<string> {
    const vectorEntry: Partial<VectorEntry> = {
      vector,
      metadata: metadata || {},
      timestamp: Date.now()
    };

    const result = await this.makeRequest('/api/vector', 'POST', vectorEntry);
    return result.id;
  }

  /**
   * Search for similar vectors
   */
  async searchSimilarVectors(vector: number[], limit: number = 10): Promise<SearchResult[]> {
    const result = await this.makeRequest('/api/vector/search', 'POST', {
      vector,
      limit,
      threshold: this.config.similarityThreshold
    });
    return result.results || [];
  }

  /**
   * Create or update graph node
   */
  async createGraphNode(id: string, label: string, type: string, properties?: Record<string, any>): Promise<boolean> {
    const node: Partial<GraphNode> = {
      id,
      label,
      type,
      properties: properties || {},
      connections: [],
      weight: 1.0
    };

    try {
      await this.makeRequest('/api/graph/node', 'POST', node);
      return true;
    } catch (error) {
      console.error(`Failed to create graph node: ${error}`);
      return false;
    }
  }

  /**
   * Connect graph nodes
   */
  async connectGraphNodes(nodeId1: string, nodeId2: string, weight: number = 0.5): Promise<boolean> {
    try {
      await this.makeRequest('/api/graph/connect', 'POST', {
        nodeId1,
        nodeId2,
        weight
      });
      return true;
    } catch (error) {
      console.error(`Failed to connect graph nodes: ${error}`);
      return false;
    }
  }

  /**
   * Get graph neighbors
   */
  async getGraphNeighbors(nodeId: string, depth: number = 1): Promise<GraphNode[]> {
    const result = await this.makeRequest(`/api/graph/neighbors/${nodeId}`, 'POST', { depth });
    return result.neighbors || [];
  }

  /**
   * Get system status
   */
  async getStatus(): Promise<any> {
    try {
      return await this.makeRequest('/api/status');
    } catch (error) {
      console.error(`Failed to get status: ${error}`);
      return null;
    }
  }

  /**
   * Get system statistics
   */
  async getStatistics(): Promise<any> {
    try {
      return await this.makeRequest('/api/stats');
    } catch (error) {
      console.error(`Failed to get statistics: ${error}`);
      return null;
    }
  }

  /**
   * Clear all data
   */
  async clearAll(): Promise<boolean> {
    try {
      await this.makeRequest('/api/clear', 'POST');
      return true;
    } catch (error) {
      console.error(`Failed to clear data: ${error}`);
      return false;
    }
  }

  /**
   * Batch operations
   */
  async batch(operations: Array<{
    type: string;
    endpoint: string;
    method: string;
    data?: any;
  }>): Promise<any[]> {
    const result = await this.makeRequest('/api/batch', 'POST', { operations });
    return result.results || [];
  }

  /**
   * Stream operations for real-time updates
   */
  async stream(endpoint: string, callback: (data: any) => void): Promise<() => void> {
    const url = `${this.baseUrl}${endpoint}`;
    
    const eventSource = new EventSource(url, {
      headers: this.config.apiKey ? { 'Authorization': `Bearer ${this.config.apiKey}` } : {}
    });

    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        callback(data);
      } catch (error) {
        console.error(`Failed to parse streaming data: ${error}`);
      }
    };

    eventSource.onerror = (error) => {
      console.error(`Stream error: ${error}`);
    };

    return () => {
      eventSource.close();
    };
  }

  /**
   * Health check
   */
  async healthCheck(): Promise<boolean> {
    try {
      const status = await this.getStatus();
      return status && status.status === 'healthy';
    } catch (error) {
      console.error(`Health check failed: ${error}`);
      return false;
    }
  }
}

/**
 * Utility functions for vector operations
 */
export class VectorUtils {
  /**
   * Calculate cosine similarity between two vectors
   */
  static cosineSimilarity(vecA: number[], vecB: number[]): number {
    if (vecA.length !== vecB.length) {
      throw new Error('Vectors must have the same length');
    }

    let dotProduct = 0;
    let normA = 0;
    let normB = 0;

    for (let i = 0; i < vecA.length; i++) {
      dotProduct += vecA[i] * vecB[i];
      normA += vecA[i] * vecA[i];
      normB += vecB[i] * vecB[i];
    }

    const denominator = Math.sqrt(normA) * Math.sqrt(normB);
    return denominator === 0 ? 0 : dotProduct / denominator;
  }

  /**
   * Normalize a vector
   */
  static normalize(vector: number[]): number[] {
    const norm = Math.sqrt(vector.reduce((sum, val) => sum + val * val, 0));
    return norm === 0 ? vector : vector.map(val => val / norm);
  }

  /**
   * Calculate Euclidean distance between two vectors
   */
  static euclideanDistance(vecA: number[], vecB: number[]): number {
    if (vecA.length !== vecB.length) {
      throw new Error('Vectors must have the same length');
    }

    return Math.sqrt(vecA.reduce((sum, val, i) => {
      return sum + Math.pow(val - vecB[i], 2);
    }, 0));
  }

  /**
   * Generate random vector
   */
  static randomVector(dimensions: number, min: number = -1, max: number = 1): number[] {
    return Array.from({ length: dimensions }, () => 
      min + Math.random() * (max - min)
    );
  }
}

/**
 * Brain AI client factory
 */
export class BrainAIClient {
  private static instances: Map<string, BrainAISDK> = new Map();

  /**
   * Get or create a Brain AI SDK instance
   */
  static getInstance(config: BrainAIConfig, name?: string): BrainAISDK {
    const key = name || 'default';
    
    if (!this.instances.has(key)) {
      this.instances.set(key, new BrainAISDK(config));
    }
    
    return this.instances.get(key)!;
  }

  /**
   * Remove instance
   */
  static removeInstance(name: string): void {
    this.instances.delete(name);
  }

  /**
   * Clear all instances
   */
  static clearAll(): void {
    this.instances.clear();
  }
}

/**
 * Decorators for Brain AI
 */
export function Memory(type: MemoryNode['type']) {
  return function (target: any, propertyName: string, descriptor: PropertyDescriptor) {
    const originalMethod = descriptor.value;
    
    descriptor.value = async function (...args: any[]) {
      const result = await originalMethod.apply(this, args);
      
      if (this.brainAI) {
        await this.brainAI.storeMemory({
          method: propertyName,
          args,
          result,
          timestamp: Date.now()
        }, type);
      }
      
      return result;
    };
    
    return descriptor;
  };
}

export function Learn() {
  return function (target: any, propertyName: string, descriptor: PropertyDescriptor) {
    const originalMethod = descriptor.value;
    
    descriptor.value = async function (...args: any[]) {
      const result = await originalMethod.apply(this, args);
      
      if (this.brainAI) {
        await this.brainAI.learn(propertyName, args.map(arg => String(arg)));
      }
      
      return result;
    };
    
    return descriptor;
  };
}

export function Reason() {
  return function (target: any, propertyName: string, descriptor: PropertyDescriptor) {
    const originalMethod = descriptor.value;
    
    descriptor.value = async function (...args: any[]) {
      if (this.brainAI) {
        const reasoning = await this.brainAI.reason(propertyName, args.map(arg => String(arg)));
        console.log('Reasoning result:', reasoning);
      }
      
      return await originalMethod.apply(this, args);
    };
    
    return descriptor;
  };
}

export default BrainAISDK;