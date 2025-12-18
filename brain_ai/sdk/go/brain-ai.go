/**
 * Brain AI Framework - Go SDK
 * Brain-inspired AI system with persistent memory, learning, and reasoning
 * 
 * @author MiniMax Agent
 * @version 1.0.0
 * @license MIT
 */

package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"math"
	"net/http"
	"sync"
	"time"
)

// Enums
type MemoryType int

const (
	EpisodicMemory MemoryType = iota
	SemanticMemory
	ProceduralMemory
	EmotionalMemory
)

type FeedbackType int

const (
	Positive FeedbackType = iota
	Negative
	Neutral
)

// Data structures
type MemoryNode struct {
	ID          string                 `json:"id"`
	Content     interface{}            `json:"content"`
	Type        MemoryType             `json:"type"`
	Strength    float64                `json:"strength"`
	Timestamp   int64                  `json:"timestamp"`
	Connections []string               `json:"connections"`
	Metadata    map[string]interface{} `json:"metadata"`
}

type LearningPattern struct {
	Pattern     string    `json:"pattern"`
	Frequency   int       `json:"frequency"`
	Strength    float64   `json:"strength"`
	Context     []string  `json:"context"`
	LastUpdated int64     `json:"lastUpdated"`
}

type ReasoningResult struct {
	Conclusion         string    `json:"conclusion"`
	Confidence         float64   `json:"confidence"`
	ReasoningPath      []string  `json:"reasoning_path"`
	SupportingEvidence []string  `json:"supporting_evidence"`
	Timestamp          int64     `json:"timestamp"`
}

type VectorEntry struct {
	ID         string                 `json:"id"`
	Vector     []float64              `json:"vector"`
	Metadata   map[string]interface{} `json:"metadata"`
	Timestamp  int64                  `json:"timestamp"`
}

type GraphNode struct {
	ID          string                 `json:"id"`
	Label       string                 `json:"label"`
	Type        string                 `json:"type"`
	Properties  map[string]interface{} `json:"properties"`
	Connections []string               `json:"connections"`
	Weight      float64                `json:"weight"`
}

type SearchResult struct {
	ID       string                 `json:"id"`
	Score    float64                `json:"score"`
	Content  interface{}            `json:"content"`
	Metadata map[string]interface{} `json:"metadata"`
}

type BatchOperation struct {
	Type      string      `json:"type"`
	Endpoint  string      `json:"endpoint"`
	Method    string      `json:"method"`
	Data      interface{} `json:"data"`
}

type BrainAIConfig struct {
	BaseURL             string  `json:"-"`
	APIKey              string  `json:"-"`
	Timeout             int     `json:"timeout"`
	MemorySize          int     `json:"memorySize"`
	LearningRate        float64 `json:"learningRate"`
	SimilarityThreshold float64 `json:"similarityThreshold"`
	MaxReasoningDepth   int     `json:"maxReasoningDepth"`
}

type BrainAISDK struct {
	config  BrainAIConfig
	client  *http.Client
	mu      sync.RWMutex
	baseURL string
}

// NewBrainAISDK creates a new Brain AI SDK instance
func NewBrainAISDK(config BrainAIConfig) *BrainAISDK {
	sdk := &BrainAISDK{
		config: BrainAIConfig{
			Timeout:             30000,
			MemorySize:          10000,
			LearningRate:        0.1,
			SimilarityThreshold: 0.7,
			MaxReasoningDepth:   5,
		},
		client: &http.Client{
			Timeout: time.Duration(30000) * time.Millisecond,
		},
	}
	
	// Update with provided config
	if config.BaseURL != "" {
		sdk.config.BaseURL = config.BaseURL
		sdk.baseURL = config.BaseURL
		if sdk.baseURL[len(sdk.baseURL)-1] == '/' {
			sdk.baseURL = sdk.baseURL[:len(sdk.baseURL)-1]
		}
	}
	if config.APIKey != "" {
		sdk.config.APIKey = config.APIKey
	}
	if config.Timeout != 0 {
		sdk.config.Timeout = config.Timeout
		sdk.client.Timeout = time.Duration(config.Timeout) * time.Millisecond
	}
	if config.MemorySize != 0 {
		sdk.config.MemorySize = config.MemorySize
	}
	if config.LearningRate != 0 {
		sdk.config.LearningRate = config.LearningRate
	}
	if config.SimilarityThreshold != 0 {
		sdk.config.SimilarityThreshold = config.SimilarityThreshold
	}
	if config.MaxReasoningDepth != 0 {
		sdk.config.MaxReasoningDepth = config.MaxReasoningDepth
	}

	return sdk
}

// makeRequest performs HTTP request
func (sdk *BrainAISDK) makeRequest(endpoint, method string, data interface{}) (map[string]interface{}, error) {
	url := sdk.baseURL + endpoint
	
	var req *http.Request
	var err error
	
	if data != nil {
		jsonData, err := json.Marshal(data)
		if err != nil {
			return nil, err
		}
		req, err = http.NewRequest(method, url, bytes.NewBuffer(jsonData))
	} else {
		req, err = http.NewRequest(method, url, nil)
	}
	
	if err != nil {
		return nil, err
	}
	
	// Set headers
	req.Header.Set("Content-Type", "application/json")
	if sdk.config.APIKey != "" {
		req.Header.Set("Authorization", "Bearer "+sdk.config.APIKey)
	}
	
	resp, err := sdk.client.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()
	
	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, err
	}
	
	if resp.StatusCode >= 400 {
		return nil, fmt.Errorf("HTTP error! status: %d", resp.StatusCode)
	}
	
	var result map[string]interface{}
	err = json.Unmarshal(body, &result)
	if err != nil {
		return nil, err
	}
	
	return result, nil
}

// StoreMemory stores a memory node in the brain
func (sdk *BrainAISDK) StoreMemory(content interface{}, memoryType MemoryType, metadata map[string]interface{}) (string, error) {
	memoryNode := MemoryNode{
		Content:     content,
		Type:        memoryType,
		Strength:    1.0,
		Timestamp:   time.Now().UnixMilli(),
		Connections: []string{},
		Metadata:    metadata,
	}
	
	result, err := sdk.makeRequest("/api/memory", "POST", memoryNode)
	if err != nil {
		return "", err
	}
	
	if id, ok := result["id"].(string); ok {
		return id, nil
	}
	
	return "", fmt.Errorf("invalid response: missing id")
}

// GetMemory retrieves memory by ID
func (sdk *BrainAISDK) GetMemory(id string) (*MemoryNode, error) {
	result, err := sdk.makeRequest("/api/memory/"+id, "GET", nil)
	if err != nil {
		return nil, err
	}
	
	memoryNode, err := parseMemoryNode(result)
	if err != nil {
		return nil, err
	}
	
	return memoryNode, nil
}

// SearchMemories searches memories by content similarity
func (sdk *BrainAISDK) SearchMemories(query interface{}, limit int) ([]SearchResult, error) {
	request := map[string]interface{}{
		"query":     query,
		"limit":     limit,
		"threshold": sdk.config.SimilarityThreshold,
	}
	
	result, err := sdk.makeRequest("/api/memory/search", "POST", request)
	if err != nil {
		return nil, err
	}
	
	results, ok := result["results"].([]interface{})
	if !ok {
		return []SearchResult{}, nil
	}
	
	searchResults := make([]SearchResult, 0, len(results))
	for _, r := range results {
		if rMap, ok := r.(map[string]interface{}); ok {
			searchResult := SearchResult{
				ID:       getString(rMap["id"]),
				Score:    getFloat64(rMap["score"]),
				Content:  rMap["content"],
				Metadata: getMap(rMap["metadata"]),
			}
			searchResults = append(searchResults, searchResult)
		}
	}
	
	return searchResults, nil
}

// ConnectMemories connects two memories
func (sdk *BrainAISDK) ConnectMemories(memoryID1, memoryID2 string, strength float64) error {
	request := map[string]interface{}{
		"memoryId1": memoryID1,
		"memoryId2": memoryID2,
		"strength":  strength,
	}
	
	_, err := sdk.makeRequest("/api/memory/connect", "POST", request)
	return err
}

// UpdateMemoryStrength updates memory strength
func (sdk *BrainAISDK) UpdateMemoryStrength(id string, delta float64) error {
	request := map[string]interface{}{
		"delta": delta,
	}
	
	_, err := sdk.makeRequest("/api/memory/"+id+"/strength", "PATCH", request)
	return err
}

// Learn learns from experience
func (sdk *BrainAISDK) Learn(pattern string, context []string) error {
	request := map[string]interface{}{
		"pattern": pattern,
		"context": context,
		"rate":    sdk.config.LearningRate,
	}
	
	_, err := sdk.makeRequest("/api/learning/learn", "POST", request)
	return err
}

// GetLearningPatterns gets learning patterns
func (sdk *BrainAISDK) GetLearningPatterns() ([]LearningPattern, error) {
	result, err := sdk.makeRequest("/api/learning/patterns", "GET", nil)
	if err != nil {
		return nil, err
	}
	
	patterns, ok := result["patterns"].([]interface{})
	if !ok {
		return []LearningPattern{}, nil
	}
	
	learningPatterns := make([]LearningPattern, 0, len(patterns))
	for _, p := range patterns {
		if pMap, ok := p.(map[string]interface{}); ok {
			pattern := LearningPattern{
				Pattern:     getString(pMap["pattern"]),
				Frequency:   int(getFloat64(pMap["frequency"])),
				Strength:    getFloat64(pMap["strength"]),
				Context:     getStringSlice(pMap["context"]),
				LastUpdated: int64(getFloat64(pMap["lastUpdated"])),
			}
			learningPatterns = append(learningPatterns, pattern)
		}
	}
	
	return learningPatterns, nil
}

// Reason performs reasoning on a query
func (sdk *BrainAISDK) Reason(query string, context []string) (ReasoningResult, error) {
	request := map[string]interface{}{
		"query":     query,
		"context":   context,
		"maxDepth":  sdk.config.MaxReasoningDepth,
	}
	
	result, err := sdk.makeRequest("/api/reasoning/reason", "POST", request)
	if err != nil {
		return ReasoningResult{}, err
	}
	
	reasoningResult := parseReasoningResult(result)
	return reasoningResult, nil
}

// AddFeedback adds feedback for learning
func (sdk *BrainAISDK) AddFeedback(feedbackType FeedbackType, information, reasoning string) error {
	request := map[string]interface{}{
		"type":       getFeedbackTypeString(feedbackType),
		"information": information,
		"reasoning":   reasoning,
		"timestamp":   time.Now().UnixMilli(),
	}
	
	_, err := sdk.makeRequest("/api/feedback", "POST", request)
	return err
}

// StoreVector stores vector for similarity search
func (sdk *BrainAISDK) StoreVector(vector []float64, metadata map[string]interface{}) (string, error) {
	vectorEntry := VectorEntry{
		Vector:     vector,
		Metadata:   metadata,
		Timestamp:  time.Now().UnixMilli(),
	}
	
	result, err := sdk.makeRequest("/api/vector", "POST", vectorEntry)
	if err != nil {
		return "", err
	}
	
	if id, ok := result["id"].(string); ok {
		return id, nil
	}
	
	return "", fmt.Errorf("invalid response: missing id")
}

// SearchSimilarVectors searches for similar vectors
func (sdk *BrainAISDK) SearchSimilarVectors(vector []float64, limit int) ([]SearchResult, error) {
	request := map[string]interface{}{
		"vector":     vector,
		"limit":      limit,
		"threshold":  sdk.config.SimilarityThreshold,
	}
	
	result, err := sdk.makeRequest("/api/vector/search", "POST", request)
	if err != nil {
		return nil, err
	}
	
	results, ok := result["results"].([]interface{})
	if !ok {
		return []SearchResult{}, nil
	}
	
	searchResults := make([]SearchResult, 0, len(results))
	for _, r := range results {
		if rMap, ok := r.(map[string]interface{}); ok {
			searchResult := SearchResult{
				ID:       getString(rMap["id"]),
				Score:    getFloat64(rMap["score"]),
				Content:  rMap["content"],
				Metadata: getMap(rMap["metadata"]),
			}
			searchResults = append(searchResults, searchResult)
		}
	}
	
	return searchResults, nil
}

// CreateGraphNode creates or updates graph node
func (sdk *BrainAISDK) CreateGraphNode(id, label, nodeType string, properties map[string]interface{}) error {
	node := GraphNode{
		ID:          id,
		Label:       label,
		Type:        nodeType,
		Properties:  properties,
		Connections: []string{},
		Weight:      1.0,
	}
	
	_, err := sdk.makeRequest("/api/graph/node", "POST", node)
	return err
}

// ConnectGraphNodes connects graph nodes
func (sdk *BrainAISDK) ConnectGraphNodes(nodeID1, nodeID2 string, weight float64) error {
	request := map[string]interface{}{
		"nodeId1": nodeID1,
		"nodeId2": nodeID2,
		"weight":  weight,
	}
	
	_, err := sdk.makeRequest("/api/graph/connect", "POST", request)
	return err
}

// GetGraphNeighbors gets graph neighbors
func (sdk *BrainAISDK) GetGraphNeighbors(nodeID string, depth int) ([]GraphNode, error) {
	request := map[string]interface{}{
		"depth": depth,
	}
	
	result, err := sdk.makeRequest("/api/graph/neighbors/"+nodeID, "POST", request)
	if err != nil {
		return nil, err
	}
	
	neighbors, ok := result["neighbors"].([]interface{})
	if !ok {
		return []GraphNode{}, nil
	}
	
	graphNodes := make([]GraphNode, 0, len(neighbors))
	for _, n := range neighbors {
		if nMap, ok := n.(map[string]interface{}); ok {
			node := GraphNode{
				ID:          getString(nMap["id"]),
				Label:       getString(nMap["label"]),
				Type:        getString(nMap["type"]),
				Properties:  getMap(nMap["properties"]),
				Connections: getStringSlice(nMap["connections"]),
				Weight:      getFloat64(nMap["weight"]),
			}
			graphNodes = append(graphNodes, node)
		}
	}
	
	return graphNodes, nil
}

// GetStatus gets system status
func (sdk *BrainAISDK) GetStatus() (map[string]interface{}, error) {
	result, err := sdk.makeRequest("/api/status", "GET", nil)
	if err != nil {
		return nil, err
	}
	return result, nil
}

// GetStatistics gets system statistics
func (sdk *BrainAISDK) GetStatistics() (map[string]interface{}, error) {
	result, err := sdk.makeRequest("/api/stats", "GET", nil)
	if err != nil {
		return nil, err
	}
	return result, nil
}

// ClearAll clears all data
func (sdk *BrainAISDK) ClearAll() error {
	_, err := sdk.makeRequest("/api/clear", "POST", nil)
	return err
}

// Batch performs batch operations
func (sdk *BrainAISDK) Batch(operations []BatchOperation) ([]map[string]interface{}, error) {
	request := map[string]interface{}{
		"operations": operations,
	}
	
	result, err := sdk.makeRequest("/api/batch", "POST", request)
	if err != nil {
		return nil, err
	}
	
	results, ok := result["results"].([]interface{})
	if !ok {
		return []map[string]interface{}{}, nil
	}
	
	batchResults := make([]map[string]interface{}, 0, len(results))
	for _, r := range results {
		if rMap, ok := r.(map[string]interface{}); ok {
			batchResults = append(batchResults, rMap)
		}
	}
	
	return batchResults, nil
}

// HealthCheck performs health check
func (sdk *BrainAISDK) HealthCheck() (bool, error) {
	status, err := sdk.GetStatus()
	if err != nil {
		log.Printf("Health check failed: %v", err)
		return false, err
	}
	
	if statusStatus, ok := status["status"].(string); ok {
		return statusStatus == "healthy", nil
	}
	
	return false, nil
}

// Helper functions
func getString(v interface{}) string {
	if str, ok := v.(string); ok {
		return str
	}
	return ""
}

func getFloat64(v interface{}) float64 {
	if f, ok := v.(float64); ok {
		return f
	}
	if i, ok := v.(int); ok {
		return float64(i)
	}
	return 0
}

func getMap(v interface{}) map[string]interface{} {
	if m, ok := v.(map[string]interface{}); ok {
		return m
	}
	return map[string]interface{}{}
}

func getStringSlice(v interface{}) []string {
	if slice, ok := v.([]interface{}); ok {
		result := make([]string, 0, len(slice))
		for _, item := range slice {
			if str, ok := item.(string); ok {
				result = append(result, str)
			}
		}
		return result
	}
	return []string{}
}

func parseMemoryNode(data map[string]interface{}) (*MemoryNode, error) {
	memoryNode := &MemoryNode{
		ID:          getString(data["id"]),
		Content:     data["content"],
		Type:        MemoryType(getFloat64(data["type"])),
		Strength:    getFloat64(data["strength"]),
		Timestamp:   int64(getFloat64(data["timestamp"])),
		Connections: getStringSlice(data["connections"]),
		Metadata:    getMap(data["metadata"]),
	}
	return memoryNode, nil
}

func parseReasoningResult(data map[string]interface{}) ReasoningResult {
	return ReasoningResult{
		Conclusion:         getString(data["conclusion"]),
		Confidence:         getFloat64(data["confidence"]),
		ReasoningPath:      getStringSlice(data["reasoning_path"]),
		SupportingEvidence: getStringSlice(data["supporting_evidence"]),
		Timestamp:          int64(getFloat64(data["timestamp"])),
	}
}

func getFeedbackTypeString(feedbackType FeedbackType) string {
	switch feedbackType {
	case Positive:
		return "positive"
	case Negative:
		return "negative"
	case Neutral:
		return "neutral"
	default:
		return "neutral"
	}
}

// VectorUtils provides utility functions for vector operations
type VectorUtils struct{}

func (vu VectorUtils) CosineSimilarity(vecA, vecB []float64) float64 {
	if len(vecA) != len(vecB) {
		log.Fatal("Vectors must have the same length")
	}
	
	dotProduct := 0.0
	normA := 0.0
	normB := 0.0
	
	for i := range vecA {
		dotProduct += vecA[i] * vecB[i]
		normA += vecA[i] * vecA[i]
		normB += vecB[i] * vecB[i]
	}
	
	denominator := math.Sqrt(normA) * math.Sqrt(normB)
	if denominator == 0 {
		return 0
	}
	return dotProduct / denominator
}

func (vu VectorUtils) Normalize(vector []float64) []float64 {
	norm := 0.0
	for _, val := range vector {
		norm += val * val
	}
	norm = math.Sqrt(norm)
	
	if norm == 0 {
		return vector
	}
	
	result := make([]float64, len(vector))
	for i, val := range vector {
		result[i] = val / norm
	}
	return result
}

func (vu VectorUtils) EuclideanDistance(vecA, vecB []float64) float64 {
	if len(vecA) != len(vecB) {
		log.Fatal("Vectors must have the same length")
	}
	
	sum := 0.0
	for i := range vecA {
		diff := vecA[i] - vecB[i]
		sum += diff * diff
	}
	return math.Sqrt(sum)
}

func (vu VectorUtils) RandomVector(dimensions int, min, max float64) []float64 {
	vector := make([]float64, dimensions)
	for i := 0; i < dimensions; i++ {
		vector[i] = min + (max-min)*math.Float64frombits(uint64(i<<1)) // Simplified random
	}
	return vector
}

// ClientFactory manages Brain AI SDK instances
type ClientFactory struct {
	mu       sync.RWMutex
	clients  map[string]*BrainAISDK
}

var factory = &ClientFactory{
	clients: make(map[string]*BrainAISDK),
}

// GetInstance gets or creates a Brain AI SDK instance
func (f *ClientFactory) GetInstance(config BrainAIConfig, name string) *BrainAISDK {
	f.mu.Lock()
	defer f.mu.Unlock()
	
	if client, exists := f.clients[name]; exists {
		return client
	}
	
	client := NewBrainAISDK(config)
	f.clients[name] = client
	return client
}

// RemoveInstance removes a Brain AI SDK instance
func (f *ClientFactory) RemoveInstance(name string) {
	f.mu.Lock()
	defer f.mu.Unlock()
	delete(f.clients, name)
}

// ClearAll removes all Brain AI SDK instances
func (f *ClientFactory) ClearAll() {
	f.mu.Lock()
	defer f.mu.Unlock()
	clear(f.clients)
}

// Example usage
func main() {
	// Create configuration
	config := BrainAISDK{
		BaseURL:             "http://localhost:8000",
		Timeout:             30000,
		MemorySize:          10000,
		LearningRate:        0.1,
		SimilarityThreshold: 0.7,
		MaxReasoningDepth:   5,
	}
	
	// Create SDK instance
	sdk := NewBrainAISDK(config)
	
	// Example: Store memory
	content := map[string]interface{}{
		"text":    "This is a test memory",
		"context": "testing",
	}
	
	id, err := sdk.StoreMemory(content, SemanticMemory, map[string]interface{}{
		"importance": 0.8,
	})
	if err != nil {
		log.Fatalf("Failed to store memory: %v", err)
	}
	
	fmt.Printf("Stored memory with ID: %s\n", id)
	
	// Example: Search memories
	searchResults, err := sdk.SearchMemories("test memory", 5)
	if err != nil {
		log.Fatalf("Failed to search memories: %v", err)
	}
	
	fmt.Printf("Found %d results\n", len(searchResults))
	for _, result := range searchResults {
		fmt.Printf("Result ID: %s, Score: %.2f\n", result.ID, result.Score)
	}
	
	// Example: Learn pattern
	err = sdk.Learn("user_pattern", []string{"context1", "context2"})
	if err != nil {
		log.Fatalf("Failed to learn pattern: %v", err)
	}
	
	fmt.Println("Learned pattern successfully")
	
	// Example: Perform reasoning
	reasoningResult, err := sdk.Reason("What is the meaning of life?", []string{"philosophy"})
	if err != nil {
		log.Fatalf("Failed to reason: %v", err)
	}
	
	fmt.Printf("Reasoning conclusion: %s (confidence: %.2f)\n", 
		reasoningResult.Conclusion, reasoningResult.Confidence)
	
	// Example: Health check
	isHealthy, err := sdk.HealthCheck()
	if err != nil {
		log.Fatalf("Health check failed: %v", err)
	}
	
	if isHealthy {
		fmt.Println("System is healthy")
	} else {
		fmt.Println("System is unhealthy")
	}
}