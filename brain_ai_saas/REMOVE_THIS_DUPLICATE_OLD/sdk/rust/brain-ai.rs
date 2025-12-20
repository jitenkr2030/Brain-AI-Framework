/**
 * Brain AI Framework - Rust SDK
 * Brain-inspired AI system with persistent memory, learning, and reasoning
 * 
 * @author MiniMax Agent
 * @version 1.0.0
 * @license MIT
 */

use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::time::Duration;
use tokio::time::timeout;
use ureq::{Agent, Request, Response};

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum MemoryType {
    Episodic,
    Semantic,
    Procedural,
    Emotional,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum FeedbackType {
    Positive,
    Negative,
    Neutral,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MemoryNode {
    pub id: Option<String>,
    pub content: serde_json::Value,
    pub memory_type: MemoryType,
    pub strength: f64,
    pub timestamp: i64,
    pub connections: Vec<String>,
    pub metadata: HashMap<String, serde_json::Value>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct LearningPattern {
    pub pattern: String,
    pub frequency: u32,
    pub strength: f64,
    pub context: Vec<String>,
    pub last_updated: i64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ReasoningResult {
    pub conclusion: String,
    pub confidence: f64,
    pub reasoning_path: Vec<String>,
    pub supporting_evidence: Vec<String>,
    pub timestamp: i64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct VectorEntry {
    pub id: Option<String>,
    pub vector: Vec<f64>,
    pub metadata: HashMap<String, serde_json::Value>,
    pub timestamp: i64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct GraphNode {
    pub id: String,
    pub label: String,
    pub node_type: String,
    pub properties: HashMap<String, serde_json::Value>,
    pub connections: Vec<String>,
    pub weight: f64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SearchResult {
    pub id: String,
    pub score: f64,
    pub content: serde_json::Value,
    pub metadata: HashMap<String, serde_json::Value>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BatchOperation {
    pub operation_type: String,
    pub endpoint: String,
    pub method: String,
    pub data: Option<serde_json::Value>,
}

#[derive(Debug, Clone)]
pub struct BrainAIConfig {
    pub base_url: String,
    pub api_key: Option<String>,
    pub timeout: Duration,
    pub memory_size: usize,
    pub learning_rate: f64,
    pub similarity_threshold: f64,
    pub max_reasoning_depth: usize,
}

impl Default for BrainAIConfig {
    fn default() -> Self {
        Self {
            base_url: "http://localhost:8000".to_string(),
            api_key: None,
            timeout: Duration::from_secs(30),
            memory_size: 10000,
            learning_rate: 0.1,
            similarity_threshold: 0.7,
            max_reasoning_depth: 5,
        }
    }
}

impl BrainAIConfig {
    pub fn new(base_url: &str) -> Self {
        let mut config = Self::default();
        config.base_url = base_url.to_string();
        config
    }

    pub fn with_api_key(mut self, api_key: &str) -> Self {
        self.api_key = Some(api_key.to_string());
        self
    }

    pub fn with_timeout(mut self, timeout_secs: u64) -> Self {
        self.timeout = Duration::from_secs(timeout_secs);
        self
    }

    pub fn with_memory_size(mut self, memory_size: usize) -> Self {
        self.memory_size = memory_size;
        self
    }

    pub fn with_learning_rate(mut self, learning_rate: f64) -> Self {
        self.learning_rate = learning_rate;
        self
    }

    pub fn with_similarity_threshold(mut self, threshold: f64) -> Self {
        self.similarity_threshold = threshold;
        self
    }

    pub fn with_max_reasoning_depth(mut self, depth: usize) -> Self {
        self.max_reasoning_depth = depth;
        self
    }
}

#[derive(Debug, thiserror::Error)]
pub enum BrainAIError {
    #[error("HTTP error: {status}")]
    HttpError { status: u16, message: String },
    #[error("Request timeout")]
    Timeout,
    #[error("JSON serialization error: {0}")]
    Serialization(#[from] serde_json::Error),
    #[error("Request error: {0}")]
    Request(#[from] ureq::Error),
    #[error("Other error: {0}")]
    Other(String),
}

pub struct BrainAISDK {
    config: BrainAIConfig,
    agent: Agent,
}

impl BrainAISDK {
    pub fn new(config: BrainAIConfig) -> Self {
        Self {
            config,
            agent: Agent::new(),
        }
    }

    async fn make_request<T: Serialize>(
        &self,
        endpoint: &str,
        method: &str,
        data: Option<&T>,
    ) -> Result<serde_json::Value, BrainAIError> {
        let url = format!("{}/{}", self.config.base_url.trim_end_matches('/'), endpoint);
        
        let mut request = match method {
            "GET" => self.agent.get(&url),
            "POST" => self.agent.post(&url),
            "PUT" => self.agent.put(&url),
            "PATCH" => self.agent.patch(&url),
            "DELETE" => self.agent.delete(&url),
            _ => return Err(BrainAIError::Other(format!("Unsupported method: {}", method))),
        };

        // Set headers
        request = request.set("Content-Type", "application/json");
        if let Some(api_key) = &self.config.api_key {
            request = request.set("Authorization", &format!("Bearer {}", api_key));
        }

        // Set body if provided
        if let Some(body_data) = data {
            let json_string = serde_json::to_string(body_data)
                .map_err(BrainAIError::Serialization)?;
            request = request.send_string(&json_string);
        }

        let future = request.call();
        let response = timeout(self.config.timeout, future)
            .await
            .map_err(|_| BrainAIError::Timeout)??;

        if !response.status().is_success() {
            let message = response.into_string().unwrap_or_else(|_| "Unknown error".to_string());
            return Err(BrainAIError::HttpError {
                status: response.status(),
                message,
            });
        }

        let response_text = response.into_string()
            .map_err(|e| BrainAIError::Other(format!("Failed to read response: {}", e)))?;
        
        let json_value: serde_json::Value = serde_json::from_str(&response_text)
            .map_err(BrainAIError::Serialization)?;

        Ok(json_value)
    }

    /// Store a memory node in the brain
    pub async fn store_memory(
        &self,
        content: serde_json::Value,
        memory_type: MemoryType,
        metadata: Option<HashMap<String, serde_json::Value>>,
    ) -> Result<String, BrainAIError> {
        let memory_node = MemoryNode {
            id: None,
            content,
            memory_type,
            strength: 1.0,
            timestamp: chrono::Utc::now().timestamp_millis(),
            connections: Vec::new(),
            metadata: metadata.unwrap_or_default(),
        };

        let result = self.make_request("/api/memory", "POST", Some(&memory_node)).await?;
        
        result.get("id")
            .and_then(|id| id.as_str().map(|s| s.to_string()))
            .ok_or_else(|| BrainAIError::Other("Invalid response: missing id".to_string()))
    }

    /// Retrieve memory by ID
    pub async fn get_memory(&self, id: &str) -> Result<Option<MemoryNode>, BrainAIError> {
        match self.make_request(&format!("/api/memory/{}", id), "GET", None::<&()>::None).await {
            Ok(json_value) => {
                let memory_node: MemoryNode = serde_json::from_value(json_value)
                    .map_err(BrainAIError::Serialization)?;
                Ok(Some(memory_node))
            }
            Err(BrainAIError::HttpError { status: 404, .. }) => Ok(None),
            Err(e) => Err(e),
        }
    }

    /// Search memories by content similarity
    pub async fn search_memories(
        &self,
        query: serde_json::Value,
        limit: usize,
    ) -> Result<Vec<SearchResult>, BrainAIError> {
        let request = serde_json::json!({
            "query": query,
            "limit": limit,
            "threshold": self.config.similarity_threshold,
        });

        let result = self.make_request("/api/memory/search", "POST", Some(&request)).await?;
        
        let results = result.get("results")
            .and_then(|r| r.as_array())
            .cloned()
            .unwrap_or_default();

        let search_results: Result<Vec<SearchResult>, _> = results
            .iter()
            .map(|r| serde_json::from_value(r.clone()).map_err(BrainAIError::Serialization))
            .collect();

        search_results
    }

    /// Connect two memories
    pub async fn connect_memories(
        &self,
        memory_id1: &str,
        memory_id2: &str,
        strength: f64,
    ) -> Result<(), BrainAIError> {
        let request = serde_json::json!({
            "memoryId1": memory_id1,
            "memoryId2": memory_id2,
            "strength": strength,
        });

        self.make_request("/api/memory/connect", "POST", Some(&request)).await?;
        Ok(())
    }

    /// Update memory strength
    pub async fn update_memory_strength(&self, id: &str, delta: f64) -> Result<(), BrainAIError> {
        let request = serde_json::json!({ "delta": delta });
        
        self.make_request(&format!("/api/memory/{}/strength", id), "PATCH", Some(&request)).await?;
        Ok(())
    }

    /// Learn from experience
    pub async fn learn(&self, pattern: &str, context: Option<Vec<String>>) -> Result<(), BrainAIError> {
        let request = serde_json::json!({
            "pattern": pattern,
            "context": context.unwrap_or_default(),
            "rate": self.config.learning_rate,
        });

        self.make_request("/api/learning/learn", "POST", Some(&request)).await?;
        Ok(())
    }

    /// Get learning patterns
    pub async fn get_learning_patterns(&self) -> Result<Vec<LearningPattern>, BrainAIError> {
        let result = self.make_request("/api/learning/patterns", "GET", None::<&()>::None).await?;
        
        let patterns = result.get("patterns")
            .and_then(|p| p.as_array())
            .cloned()
            .unwrap_or_default();

        let learning_patterns: Result<Vec<LearningPattern>, _> = patterns
            .iter()
            .map(|p| serde_json::from_value(p.clone()).map_err(BrainAIError::Serialization))
            .collect();

        learning_patterns
    }

    /// Perform reasoning on a query
    pub async fn reason(
        &self,
        query: &str,
        context: Option<Vec<String>>,
    ) -> Result<ReasoningResult, BrainAIError> {
        let request = serde_json::json!({
            "query": query,
            "context": context.unwrap_or_default(),
            "maxDepth": self.config.max_reasoning_depth,
        });

        let result = self.make_request("/api/reasoning/reason", "POST", Some(&request)).await?;
        
        let reasoning_result: ReasoningResult = serde_json::from_value(result)
            .map_err(BrainAIError::Serialization)?;

        Ok(reasoning_result)
    }

    /// Add feedback for learning
    pub async fn add_feedback(
        &self,
        feedback_type: FeedbackType,
        information: &str,
        reasoning: Option<&str>,
    ) -> Result<(), BrainAIError> {
        let request = serde_json::json!({
            "type": match feedback_type {
                FeedbackType::Positive => "positive",
                FeedbackType::Negative => "negative",
                FeedbackType::Neutral => "neutral",
            },
            "information": information,
            "reasoning": reasoning.unwrap_or(""),
            "timestamp": chrono::Utc::now().timestamp_millis(),
        });

        self.make_request("/api/feedback", "POST", Some(&request)).await?;
        Ok(())
    }

    /// Store vector for similarity search
    pub async fn store_vector(
        &self,
        vector: Vec<f64>,
        metadata: Option<HashMap<String, serde_json::Value>>,
    ) -> Result<String, BrainAIError> {
        let vector_entry = VectorEntry {
            id: None,
            vector,
            metadata: metadata.unwrap_or_default(),
            timestamp: chrono::Utc::now().timestamp_millis(),
        };

        let result = self.make_request("/api/vector", "POST", Some(&vector_entry)).await?;
        
        result.get("id")
            .and_then(|id| id.as_str().map(|s| s.to_string()))
            .ok_or_else(|| BrainAIError::Other("Invalid response: missing id".to_string()))
    }

    /// Search for similar vectors
    pub async fn search_similar_vectors(
        &self,
        vector: Vec<f64>,
        limit: usize,
    ) -> Result<Vec<SearchResult>, BrainAIError> {
        let request = serde_json::json!({
            "vector": vector,
            "limit": limit,
            "threshold": self.config.similarity_threshold,
        });

        let result = self.make_request("/api/vector/search", "POST", Some(&request)).await?;
        
        let results = result.get("results")
            .and_then(|r| r.as_array())
            .cloned()
            .unwrap_or_default();

        let search_results: Result<Vec<SearchResult>, _> = results
            .iter()
            .map(|r| serde_json::from_value(r.clone()).map_err(BrainAIError::Serialization))
            .collect();

        search_results
    }

    /// Create or update graph node
    pub async fn create_graph_node(
        &self,
        id: &str,
        label: &str,
        node_type: &str,
        properties: Option<HashMap<String, serde_json::Value>>,
    ) -> Result<(), BrainAIError> {
        let node = GraphNode {
            id: id.to_string(),
            label: label.to_string(),
            node_type: node_type.to_string(),
            properties: properties.unwrap_or_default(),
            connections: Vec::new(),
            weight: 1.0,
        };

        self.make_request("/api/graph/node", "POST", Some(&node)).await?;
        Ok(())
    }

    /// Connect graph nodes
    pub async fn connect_graph_nodes(
        &self,
        node_id1: &str,
        node_id2: &str,
        weight: f64,
    ) -> Result<(), BrainAIError> {
        let request = serde_json::json!({
            "nodeId1": node_id1,
            "nodeId2": node_id2,
            "weight": weight,
        });

        self.make_request("/api/graph/connect", "POST", Some(&request)).await?;
        Ok(())
    }

    /// Get graph neighbors
    pub async fn get_graph_neighbors(
        &self,
        node_id: &str,
        depth: usize,
    ) -> Result<Vec<GraphNode>, BrainAIError> {
        let request = serde_json::json!({ "depth": depth });

        let result = self.make_request(&format!("/api/graph/neighbors/{}", node_id), "POST", Some(&request)).await?;
        
        let neighbors = result.get("neighbors")
            .and_then(|n| n.as_array())
            .cloned()
            .unwrap_or_default();

        let graph_nodes: Result<Vec<GraphNode>, _> = neighbors
            .iter()
            .map(|n| serde_json::from_value(n.clone()).map_err(BrainAIError::Serialization))
            .collect();

        graph_nodes
    }

    /// Get system status
    pub async fn get_status(&self) -> Result<serde_json::Value, BrainAIError> {
        self.make_request("/api/status", "GET", None::<&()>::None).await
    }

    /// Get system statistics
    pub async fn get_statistics(&self) -> Result<serde_json::Value, BrainAIError> {
        self.make_request("/api/stats", "GET", None::<&()>::None).await
    }

    /// Clear all data
    pub async fn clear_all(&self) -> Result<(), BrainAIError> {
        self.make_request("/api/clear", "POST", None::<&()>::None).await?;
        Ok(())
    }

    /// Batch operations
    pub async fn batch(
        &self,
        operations: Vec<BatchOperation>,
    ) -> Result<Vec<serde_json::Value>, BrainAIError> {
        let request = serde_json::json!({ "operations": operations });

        let result = self.make_request("/api/batch", "POST", Some(&request)).await?;
        
        let results = result.get("results")
            .and_then(|r| r.as_array())
            .cloned()
            .unwrap_or_default();

        Ok(results)
    }

    /// Health check
    pub async fn health_check(&self) -> Result<bool, BrainAIError> {
        match self.get_status().await {
            Ok(status) => {
                if let Some(status_str) = status.get("status").and_then(|s| s.as_str()) {
                    Ok(status_str == "healthy")
                } else {
                    Ok(false)
                }
            }
            Err(e) => {
                eprintln!("Health check failed: {}", e);
                Ok(false)
            }
        }
    }
}

/// Vector utilities for vector operations
pub struct VectorUtils;

impl VectorUtils {
    /// Calculate cosine similarity between two vectors
    pub fn cosine_similarity(vec_a: &[f64], vec_b: &[f64]) -> f64 {
        if vec_a.len() != vec_b.len() {
            panic!("Vectors must have the same length");
        }

        let mut dot_product = 0.0;
        let mut norm_a = 0.0;
        let mut norm_b = 0.0;

        for i in 0..vec_a.len() {
            dot_product += vec_a[i] * vec_b[i];
            norm_a += vec_a[i] * vec_a[i];
            norm_b += vec_b[i] * vec_b[i];
        }

        let denominator = norm_a.sqrt() * norm_b.sqrt();
        if denominator == 0.0 {
            0.0
        } else {
            dot_product / denominator
        }
    }

    /// Normalize a vector
    pub fn normalize(vector: &[f64]) -> Vec<f64> {
        let norm: f64 = vector.iter().map(|&x| x * x).sum::<f64>().sqrt();
        
        if norm == 0.0 {
            vector.to_vec()
        } else {
            vector.iter().map(|&x| x / norm).collect()
        }
    }

    /// Calculate Euclidean distance between two vectors
    pub fn euclidean_distance(vec_a: &[f64], vec_b: &[f64]) -> f64 {
        if vec_a.len() != vec_b.len() {
            panic!("Vectors must have the same length");
        }

        let sum: f64 = vec_a.iter()
            .enumerate()
            .map(|(i, &a)| {
                let diff = a - vec_b[i];
                diff * diff
            })
            .sum();

        sum.sqrt()
    }

    /// Generate random vector
    pub fn random_vector(dimensions: usize, min: f64, max: f64) -> Vec<f64> {
        use rand::Rng;
        let mut rng = rand::thread_rng();
        
        (0..dimensions)
            .map(|_| rng.gen_range(min..max))
            .collect()
    }
}

/// Client factory for managing Brain AI SDK instances
use std::sync::{Arc, Mutex};
use std::collections::HashMap;

pub struct ClientFactory {
    clients: Arc<Mutex<HashMap<String, BrainAISDK>>>,
}

impl ClientFactory {
    pub fn new() -> Self {
        Self {
            clients: Arc::new(Mutex::new(HashMap::new())),
        }
    }

    pub fn get_instance(&self, config: BrainAIConfig, name: &str) -> BrainAISDK {
        let mut clients = self.clients.lock().unwrap();
        
        if let Some(client) = clients.get(name) {
            client.clone()
        } else {
            let client = BrainAISDK::new(config);
            clients.insert(name.to_string(), client.clone());
            client
        }
    }

    pub fn remove_instance(&self, name: &str) {
        let mut clients = self.clients.lock().unwrap();
        clients.remove(name);
    }

    pub fn clear_all(&self) {
        let mut clients = self.clients.lock().unwrap();
        clients.clear();
    }
}

impl Clone for BrainAISDK {
    fn clone(&self) -> Self {
        Self {
            config: self.config.clone(),
            agent: Agent::new(),
        }
    }
}

/// Example usage
#[cfg(test)]
mod tests {
    use super::*;

    #[tokio::test]
    async fn test_basic_operations() {
        let config = BrainAIConfig::new("http://localhost:8000");
        let sdk = BrainAISDK::new(config);

        // This would require a running Brain AI server
        // For demonstration purposes only
        let content = serde_json::json!({
            "text": "This is a test memory",
            "context": "testing"
        });

        // Test memory storage (would fail without running server)
        // let memory_id = sdk.store_memory(content, MemoryType::Semantic, None).await;
        // assert!(memory_id.is_ok());

        // Test vector utilities
        let vec_a = vec![1.0, 2.0, 3.0];
        let vec_b = vec![4.0, 5.0, 6.0];
        
        let similarity = VectorUtils::cosine_similarity(&vec_a, &vec_b);
        let distance = VectorUtils::euclidean_distance(&vec_a, &vec_b);
        let normalized = VectorUtils::normalize(&vec_a);
        
        println!("Cosine similarity: {}", similarity);
        println!("Euclidean distance: {}", distance);
        println!("Normalized vector: {:?}", normalized);
    }
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Example usage
    let config = BrainAIConfig::new("http://localhost:8000")
        .with_timeout(30)
        .with_memory_size(10000)
        .with_learning_rate(0.1)
        .with_similarity_threshold(0.7)
        .with_max_reasoning_depth(5);

    let sdk = BrainAISDK::new(config);

    // Example: Store memory
    let content = serde_json::json!({
        "text": "This is a test memory",
        "context": "testing"
    });

    println!("Storing memory...");
    // Note: This would require a running Brain AI server
    // let memory_id = sdk.store_memory(content, MemoryType::Semantic, None).await?;
    // println!("Stored memory with ID: {}", memory_id);

    // Example: Search memories
    println!("Searching memories...");
    // let search_results = sdk.search_memories("test memory", 5).await?;
    // println!("Found {} results", search_results.len());

    // Example: Learn pattern
    println!("Learning pattern...");
    // sdk.learn("user_pattern", Some(vec!["context1".to_string(), "context2".to_string()])).await?;
    // println!("Learned pattern successfully");

    // Example: Perform reasoning
    println!("Performing reasoning...");
    // let reasoning_result = sdk.reason("What is the meaning of life?", Some(vec!["philosophy".to_string()])).await?;
    // println!("Reasoning conclusion: {} (confidence: {:.2})", reasoning_result.conclusion, reasoning_result.confidence);

    // Example: Health check
    println!("Checking health...");
    // let is_healthy = sdk.health_check().await?;
    // if is_healthy {
    //     println!("System is healthy");
    // } else {
    //     println!("System is unhealthy");
    // }

    // Vector utilities example
    println!("\nVector utilities example:");
    let vec_a = vec![1.0, 2.0, 3.0, 4.0];
    let vec_b = vec![2.0, 4.0, 6.0, 8.0];
    
    let similarity = VectorUtils::cosine_similarity(&vec_a, &vec_b);
    let distance = VectorUtils::euclidean_distance(&vec_a, &vec_b);
    let normalized = VectorUtils::normalize(&vec_a);
    
    println!("Vector A: {:?}", vec_a);
    println!("Vector B: {:?}", vec_b);
    println!("Cosine similarity: {:.4}", similarity);
    println!("Euclidean distance: {:.4}", distance);
    println!("Normalized A: {:?}", normalized);

    Ok(())
}