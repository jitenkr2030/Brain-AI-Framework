/**
 * Brain AI Framework - Java SDK
 * Brain-inspired AI system with persistent memory, learning, and reasoning
 * 
 * @author MiniMax Agent
 * @version 1.0.0
 * @license MIT
 */

package com.brainai.sdk;

import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.JsonNode;
import okhttp3.*;

import java.io.IOException;
import java.time.Instant;
import java.util.*;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.TimeUnit;
import java.util.stream.Collectors;

/**
 * Main Brain AI SDK class
 */
public class BrainAISDK {
    private final String baseUrl;
    private final String apiKey;
    private final int timeout;
    private final int memorySize;
    private final double learningRate;
    private final double similarityThreshold;
    private final int maxReasoningDepth;
    private final OkHttpClient client;
    private final ObjectMapper objectMapper;

    public BrainAISDK(BrainAIConfig config) {
        this.baseUrl = config.getBaseUrl().replaceAll("/$", "");
        this.apiKey = config.getApiKey();
        this.timeout = config.getTimeout();
        this.memorySize = config.getMemorySize();
        this.learningRate = config.getLearningRate();
        this.similarityThreshold = config.getSimilarityThreshold();
        this.maxReasoningDepth = config.getMaxReasoningDepth();
        
        this.client = new OkHttpClient.Builder()
                .connectTimeout(timeout, TimeUnit.MILLISECONDS)
                .readTimeout(timeout, TimeUnit.MILLISECONDS)
                .writeTimeout(timeout, TimeUnit.MILLISECONDS)
                .build();
        
        this.objectMapper = new ObjectMapper();
        this.objectMapper.setSerializationInclusion(JsonInclude.Include.NON_NULL);
    }

    /**
     * Store a memory node in the brain
     */
    public CompletableFuture<String> storeMemory(Object content, MemoryType type, Map<String, Object> metadata) {
        MemoryNode memoryNode = new MemoryNode();
        memoryNode.setContent(content);
        memoryNode.setType(type);
        memoryNode.setStrength(1.0);
        memoryNode.setTimestamp(Instant.now().toEpochMilli());
        memoryNode.setConnections(new ArrayList<>());
        memoryNode.setMetadata(metadata != null ? metadata : new HashMap<>());

        return makeRequest("/api/memory", "POST", memoryNode)
                .thenApply(response -> response.get("id").asText());
    }

    /**
     * Retrieve memory by ID
     */
    public CompletableFuture<Optional<MemoryNode>> getMemory(String id) {
        return makeRequest("/api/memory/" + id)
                .thenApply(this::parseMemoryNode)
                .exceptionally(throwable -> {
                    System.err.println("Failed to get memory: " + throwable.getMessage());
                    return Optional.empty();
                });
    }

    /**
     * Search memories by content similarity
     */
    public CompletableFuture<List<SearchResult>> searchMemories(Object query, int limit) {
        Map<String, Object> request = new HashMap<>();
        request.put("query", query);
        request.put("limit", limit);
        request.put("threshold", similarityThreshold);

        return makeRequest("/api/memory/search", "POST", request)
                .thenApply(response -> {
                    JsonNode results = response.get("results");
                    if (results != null && results.isArray()) {
                        return parseSearchResults(results);
                    }
                    return new ArrayList<>();
                });
    }

    /**
     * Connect two memories
     */
    public CompletableFuture<Boolean> connectMemories(String memoryId1, String memoryId2, double strength) {
        Map<String, Object> request = new HashMap<>();
        request.put("memoryId1", memoryId1);
        request.put("memoryId2", memoryId2);
        request.put("strength", strength);

        return makeRequest("/api/memory/connect", "POST", request)
                .thenApply(response -> true)
                .exceptionally(throwable -> {
                    System.err.println("Failed to connect memories: " + throwable.getMessage());
                    return false;
                });
    }

    /**
     * Update memory strength
     */
    public CompletableFuture<Boolean> updateMemoryStrength(String id, double delta) {
        Map<String, Object> request = new HashMap<>();
        request.put("delta", delta);

        return makeRequest("/api/memory/" + id + "/strength", "PATCH", request)
                .thenApply(response -> true)
                .exceptionally(throwable -> {
                    System.err.println("Failed to update memory strength: " + throwable.getMessage());
                    return false;
                });
    }

    /**
     * Learn from experience
     */
    public CompletableFuture<Boolean> learn(String pattern, List<String> context) {
        Map<String, Object> request = new HashMap<>();
        request.put("pattern", pattern);
        request.put("context", context != null ? context : new ArrayList<>());
        request.put("rate", learningRate);

        return makeRequest("/api/learning/learn", "POST", request)
                .thenApply(response -> true)
                .exceptionally(throwable -> {
                    System.err.println("Failed to learn: " + throwable.getMessage());
                    return false;
                });
    }

    /**
     * Get learning patterns
     */
    public CompletableFuture<List<LearningPattern>> getLearningPatterns() {
        return makeRequest("/api/learning/patterns")
                .thenApply(response -> {
                    JsonNode patterns = response.get("patterns");
                    if (patterns != null && patterns.isArray()) {
                        return parseLearningPatterns(patterns);
                    }
                    return new ArrayList<>();
                });
    }

    /**
     * Perform reasoning on a query
     */
    public CompletableFuture<ReasoningResult> reason(String query, List<String> context) {
        Map<String, Object> request = new HashMap<>();
        request.put("query", query);
        request.put("context", context != null ? context : new ArrayList<>());
        request.put("maxDepth", maxReasoningDepth);

        return makeRequest("/api/reasoning/reason", "POST", request)
                .thenApply(this::parseReasoningResult);
    }

    /**
     * Add feedback for learning
     */
    public CompletableFuture<Boolean> addFeedback(FeedbackType type, String information, String reasoning) {
        Map<String, Object> request = new HashMap<>();
        request.put("type", type.toString().toLowerCase());
        request.put("information", information);
        request.put("reasoning", reasoning);
        request.put("timestamp", Instant.now().toEpochMilli());

        return makeRequest("/api/feedback", "POST", request)
                .thenApply(response -> true)
                .exceptionally(throwable -> {
                    System.err.println("Failed to add feedback: " + throwable.getMessage());
                    return false;
                });
    }

    /**
     * Store vector for similarity search
     */
    public CompletableFuture<String> storeVector(List<Double> vector, Map<String, Object> metadata) {
        VectorEntry vectorEntry = new VectorEntry();
        vectorEntry.setVector(vector);
        vectorEntry.setMetadata(metadata != null ? metadata : new HashMap<>());
        vectorEntry.setTimestamp(Instant.now().toEpochMilli());

        return makeRequest("/api/vector", "POST", vectorEntry)
                .thenApply(response -> response.get("id").asText());
    }

    /**
     * Search for similar vectors
     */
    public CompletableFuture<List<SearchResult>> searchSimilarVectors(List<Double> vector, int limit) {
        Map<String, Object> request = new HashMap<>();
        request.put("vector", vector);
        request.put("limit", limit);
        request.put("threshold", similarityThreshold);

        return makeRequest("/api/vector/search", "POST", request)
                .thenApply(response -> {
                    JsonNode results = response.get("results");
                    if (results != null && results.isArray()) {
                        return parseSearchResults(results);
                    }
                    return new ArrayList<>();
                });
    }

    /**
     * Create or update graph node
     */
    public CompletableFuture<Boolean> createGraphNode(String id, String label, String type, Map<String, Object> properties) {
        GraphNode node = new GraphNode();
        node.setId(id);
        node.setLabel(label);
        node.setType(type);
        node.setProperties(properties != null ? properties : new HashMap<>());
        node.setConnections(new ArrayList<>());
        node.setWeight(1.0);

        return makeRequest("/api/graph/node", "POST", node)
                .thenApply(response -> true)
                .exceptionally(throwable -> {
                    System.err.println("Failed to create graph node: " + throwable.getMessage());
                    return false;
                });
    }

    /**
     * Connect graph nodes
     */
    public CompletableFuture<Boolean> connectGraphNodes(String nodeId1, String nodeId2, double weight) {
        Map<String, Object> request = new HashMap<>();
        request.put("nodeId1", nodeId1);
        request.put("nodeId2", nodeId2);
        request.put("weight", weight);

        return makeRequest("/api/graph/connect", "POST", request)
                .thenApply(response -> true)
                .exceptionally(throwable -> {
                    System.err.println("Failed to connect graph nodes: " + throwable.getMessage());
                    return false;
                });
    }

    /**
     * Get graph neighbors
     */
    public CompletableFuture<List<GraphNode>> getGraphNeighbors(String nodeId, int depth) {
        Map<String, Object> request = new HashMap<>();
        request.put("depth", depth);

        return makeRequest("/api/graph/neighbors/" + nodeId, "POST", request)
                .thenApply(response -> {
                    JsonNode neighbors = response.get("neighbors");
                    if (neighbors != null && neighbors.isArray()) {
                        return parseGraphNodes(neighbors);
                    }
                    return new ArrayList<>();
                });
    }

    /**
     * Get system status
     */
    public CompletableFuture<Map<String, Object>> getStatus() {
        return makeRequest("/api/status")
                .thenApply(this::mapToMap)
                .exceptionally(throwable -> {
                    System.err.println("Failed to get status: " + throwable.getMessage());
                    return new HashMap<>();
                });
    }

    /**
     * Get system statistics
     */
    public CompletableFuture<Map<String, Object>> getStatistics() {
        return makeRequest("/api/stats")
                .thenApply(this::mapToMap)
                .exceptionally(throwable -> {
                    System.err.println("Failed to get statistics: " + throwable.getMessage());
                    return new HashMap<>();
                });
    }

    /**
     * Clear all data
     */
    public CompletableFuture<Boolean> clearAll() {
        return makeRequest("/api/clear", "POST")
                .thenApply(response -> true)
                .exceptionally(throwable -> {
                    System.err.println("Failed to clear data: " + throwable.getMessage());
                    return false;
                });
    }

    /**
     * Batch operations
     */
    public CompletableFuture<List<Map<String, Object>>> batch(List<BatchOperation> operations) {
        Map<String, Object> request = new HashMap<>();
        request.put("operations", operations);

        return makeRequest("/api/batch", "POST", request)
                .thenApply(response -> {
                    JsonNode results = response.get("results");
                    if (results != null && results.isArray()) {
                        return parseBatchResults(results);
                    }
                    return new ArrayList<>();
                });
    }

    /**
     * Health check
     */
    public CompletableFuture<Boolean> healthCheck() {
        return getStatus()
                .thenApply(status -> "healthy".equals(status.get("status")))
                .exceptionally(throwable -> {
                    System.err.println("Health check failed: " + throwable.getMessage());
                    return false;
                });
    }

    // Private helper methods

    private CompletableFuture<JsonNode> makeRequest(String endpoint) {
        return makeRequest(endpoint, "GET", null);
    }

    private CompletableFuture<JsonNode> makeRequest(String endpoint, String method, Object data) {
        Request.Builder requestBuilder = new Request.Builder()
                .url(baseUrl + endpoint)
                .addHeader("Content-Type", "application/json");

        if (apiKey != null) {
            requestBuilder.addHeader("Authorization", "Bearer " + apiKey);
        }

        Request request;
        if (data != null) {
            try {
                RequestBody body = RequestBody.create(
                    objectMapper.writeValueAsString(data),
                    MediaType.parse("application/json")
                );
                request = requestBuilder.method(method, body).build();
            } catch (Exception e) {
                return CompletableFuture.failedFuture(e);
            }
        } else {
            request = requestBuilder.method(method, null).build();
        }

        CompletableFuture<JsonNode> future = new CompletableFuture<>();
        
        client.newCall(request).enqueue(new Callback() {
            @Override
            public void onFailure(Call call, IOException e) {
                future.completeExceptionally(e);
            }

            @Override
            public void onResponse(Call call, Response response) throws IOException {
                try (ResponseBody responseBody = response.body()) {
                    if (!response.isSuccessful()) {
                        future.completeExceptionally(new IOException("HTTP error! status: " + response.code()));
                        return;
                    }
                    
                    String responseBodyString = responseBody.string();
                    JsonNode jsonNode = objectMapper.readTree(responseBodyString);
                    future.complete(jsonNode);
                }
            }
        });

        return future;
    }

    private Optional<MemoryNode> parseMemoryNode(JsonNode node) {
        try {
            return Optional.of(objectMapper.treeToValue(node, MemoryNode.class));
        } catch (Exception e) {
            return Optional.empty();
        }
    }

    private List<SearchResult> parseSearchResults(JsonNode results) {
        List<SearchResult> list = new ArrayList<>();
        for (JsonNode result : results) {
            try {
                list.add(objectMapper.treeToValue(result, SearchResult.class));
            } catch (Exception e) {
                // Skip invalid results
            }
        }
        return list;
    }

    private List<LearningPattern> parseLearningPatterns(JsonNode patterns) {
        List<LearningPattern> list = new ArrayList<>();
        for (JsonNode pattern : patterns) {
            try {
                list.add(objectMapper.treeToValue(pattern, LearningPattern.class));
            } catch (Exception e) {
                // Skip invalid patterns
            }
        }
        return list;
    }

    private ReasoningResult parseReasoningResult(JsonNode result) {
        try {
            return objectMapper.treeToValue(result, ReasoningResult.class);
        } catch (Exception e) {
            return new ReasoningResult();
        }
    }

    private List<GraphNode> parseGraphNodes(JsonNode nodes) {
        List<GraphNode> list = new ArrayList<>();
        for (JsonNode node : nodes) {
            try {
                list.add(objectMapper.treeToValue(node, GraphNode.class));
            } catch (Exception e) {
                // Skip invalid nodes
            }
        }
        return list;
    }

    private List<Map<String, Object>> parseBatchResults(JsonNode results) {
        List<Map<String, Object>> list = new ArrayList<>();
        for (JsonNode result : results) {
            list.add(mapToMap(result));
        }
        return list;
    }

    private Map<String, Object> mapToMap(JsonNode node) {
        try {
            return objectMapper.convertValue(node, new TypeReference<Map<String, Object>>(){});
        } catch (Exception e) {
            return new HashMap<>();
        }
    }

    // Configuration and data classes

    public static class BrainAIConfig {
        private String baseUrl;
        private String apiKey;
        private int timeout = 30000;
        private int memorySize = 10000;
        private double learningRate = 0.1;
        private double similarityThreshold = 0.7;
        private int maxReasoningDepth = 5;

        // Getters and setters
        public String getBaseUrl() { return baseUrl; }
        public void setBaseUrl(String baseUrl) { this.baseUrl = baseUrl; }
        
        public String getApiKey() { return apiKey; }
        public void setApiKey(String apiKey) { this.apiKey = apiKey; }
        
        public int getTimeout() { return timeout; }
        public void setTimeout(int timeout) { this.timeout = timeout; }
        
        public int getMemorySize() { return memorySize; }
        public void setMemorySize(int memorySize) { this.memorySize = memorySize; }
        
        public double getLearningRate() { return learningRate; }
        public void setLearningRate(double learningRate) { this.learningRate = learningRate; }
        
        public double getSimilarityThreshold() { return similarityThreshold; }
        public void setSimilarityThreshold(double similarityThreshold) { this.similarityThreshold = similarityThreshold; }
        
        public int getMaxReasoningDepth() { return maxReasoningDepth; }
        public void setMaxReasoningDepth(int maxReasoningDepth) { this.maxReasoningDepth = maxReasoningDepth; }

        public static class Builder {
            private BrainAIConfig config = new BrainAIConfig();

            public Builder baseUrl(String baseUrl) {
                config.setBaseUrl(baseUrl);
                return this;
            }

            public Builder apiKey(String apiKey) {
                config.setApiKey(apiKey);
                return this;
            }

            public Builder timeout(int timeout) {
                config.setTimeout(timeout);
                return this;
            }

            public Builder memorySize(int memorySize) {
                config.setMemorySize(memorySize);
                return this;
            }

            public Builder learningRate(double learningRate) {
                config.setLearningRate(learningRate);
                return this;
            }

            public Builder similarityThreshold(double similarityThreshold) {
                config.setSimilarityThreshold(similarityThreshold);
                return this;
            }

            public Builder maxReasoningDepth(int maxReasoningDepth) {
                config.setMaxReasoningDepth(maxReasoningDepth);
                return this;
            }

            public BrainAIConfig build() {
                return config;
            }
        }

        public static Builder builder() {
            return new Builder();
        }
    }

    // Enums
    public enum MemoryType {
        EPISODIC, SEMANTIC, PROCEDURAL, EMOTIONAL
    }

    public enum FeedbackType {
        POSITIVE, NEGATIVE, NEUTRAL
    }

    // Data classes
    public static class MemoryNode {
        private String id;
        private Object content;
        private MemoryType type;
        private double strength;
        private long timestamp;
        private List<String> connections;
        private Map<String, Object> metadata;

        // Getters and setters
        public String getId() { return id; }
        public void setId(String id) { this.id = id; }
        
        public Object getContent() { return content; }
        public void setContent(Object content) { this.content = content; }
        
        public MemoryType getType() { return type; }
        public void setType(MemoryType type) { this.type = type; }
        
        public double getStrength() { return strength; }
        public void setStrength(double strength) { this.strength = strength; }
        
        public long getTimestamp() { return timestamp; }
        public void setTimestamp(long timestamp) { this.timestamp = timestamp; }
        
        public List<String> getConnections() { return connections; }
        public void setConnections(List<String> connections) { this.connections = connections; }
        
        public Map<String, Object> getMetadata() { return metadata; }
        public void setMetadata(Map<String, Object> metadata) { this.metadata = metadata; }
    }

    public static class LearningPattern {
        private String pattern;
        private int frequency;
        private double strength;
        private List<String> context;
        private long lastUpdated;

        // Getters and setters
        public String getPattern() { return pattern; }
        public void setPattern(String pattern) { this.pattern = pattern; }
        
        public int getFrequency() { return frequency; }
        public void setFrequency(int frequency) { this.frequency = frequency; }
        
        public double getStrength() { return strength; }
        public void setStrength(double strength) { this.strength = strength; }
        
        public List<String> getContext() { return context; }
        public void setContext(List<String> context) { this.context = context; }
        
        public long getLastUpdated() { return lastUpdated; }
        public void setLastUpdated(long lastUpdated) { this.lastUpdated = lastUpdated; }
    }

    public static class ReasoningResult {
        private String conclusion;
        private double confidence;
        private List<String> reasoningPath;
        private List<String> supportingEvidence;
        private long timestamp;

        public ReasoningResult() {
            this.reasoningPath = new ArrayList<>();
            this.supportingEvidence = new ArrayList<>();
            this.timestamp = Instant.now().toEpochMilli();
        }

        // Getters and setters
        public String getConclusion() { return conclusion; }
        public void setConclusion(String conclusion) { this.conclusion = conclusion; }
        
        public double getConfidence() { return confidence; }
        public void setConfidence(double confidence) { this.confidence = confidence; }
        
        public List<String> getReasoningPath() { return reasoningPath; }
        public void setReasoningPath(List<String> reasoningPath) { this.reasoningPath = reasoningPath; }
        
        public List<String> getSupportingEvidence() { return supportingEvidence; }
        public void setSupportingEvidence(List<String> supportingEvidence) { this.supportingEvidence = supportingEvidence; }
        
        public long getTimestamp() { return timestamp; }
        public void setTimestamp(long timestamp) { this.timestamp = timestamp; }
    }

    public static class VectorEntry {
        private String id;
        private List<Double> vector;
        private Map<String, Object> metadata;
        private long timestamp;

        // Getters and setters
        public String getId() { return id; }
        public void setId(String id) { this.id = id; }
        
        public List<Double> getVector() { return vector; }
        public void setVector(List<Double> vector) { this.vector = vector; }
        
        public Map<String, Object> getMetadata() { return metadata; }
        public void setMetadata(Map<String, Object> metadata) { this.metadata = metadata; }
        
        public long getTimestamp() { return timestamp; }
        public void setTimestamp(long timestamp) { this.timestamp = timestamp; }
    }

    public static class GraphNode {
        private String id;
        private String label;
        private String type;
        private Map<String, Object> properties;
        private List<String> connections;
        private double weight;

        // Getters and setters
        public String getId() { return id; }
        public void setId(String id) { this.id = id; }
        
        public String getLabel() { return label; }
        public void setLabel(String label) { this.label = label; }
        
        public String getType() { return type; }
        public void setType(String type) { this.type = type; }
        
        public Map<String, Object> getProperties() { return properties; }
        public void setProperties(Map<String, Object> properties) { this.properties = properties; }
        
        public List<String> getConnections() { return connections; }
        public void setConnections(List<String> connections) { this.connections = connections; }
        
        public double getWeight() { return weight; }
        public void setWeight(double weight) { this.weight = weight; }
    }

    public static class SearchResult {
        private String id;
        private double score;
        private Object content;
        private Map<String, Object> metadata;

        // Getters and setters
        public String getId() { return id; }
        public void setId(String id) { this.id = id; }
        
        public double getScore() { return score; }
        public void setScore(double score) { this.score = score; }
        
        public Object getContent() { return content; }
        public void setContent(Object content) { this.content = content; }
        
        public Map<String, Object> getMetadata() { return metadata; }
        public void setMetadata(Map<String, Object> metadata) { this.metadata = metadata; }
    }

    public static class BatchOperation {
        private String type;
        private String endpoint;
        private String method;
        private Object data;

        public BatchOperation() {}

        public BatchOperation(String type, String endpoint, String method, Object data) {
            this.type = type;
            this.endpoint = endpoint;
            this.method = method;
            this.data = data;
        }

        // Getters and setters
        public String getType() { return type; }
        public void setType(String type) { this.type = type; }
        
        public String getEndpoint() { return endpoint; }
        public void setEndpoint(String endpoint) { this.endpoint = endpoint; }
        
        public String getMethod() { return method; }
        public void setMethod(String method) { this.method = method; }
        
        public Object getData() { return data; }
        public void setData(Object data) { this.data = data; }
    }
}