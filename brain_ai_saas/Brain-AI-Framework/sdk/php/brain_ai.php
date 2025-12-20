<?php
/**
 * Brain AI Framework - PHP SDK
 * Brain-inspired AI system with persistent memory, learning, and reasoning
 * 
 * @author MiniMax Agent
 * @version 1.0.0
 * @license MIT
 */

class BrainAIException extends Exception {}

class BrainAIConfig {
    private $baseUrl;
    private $apiKey;
    private $timeout;
    private $memorySize;
    private $learningRate;
    private $similarityThreshold;
    private $maxReasoningDepth;

    public function __construct($baseUrl = 'http://localhost:8000') {
        $this->baseUrl = rtrim($baseUrl, '/');
        $this->apiKey = null;
        $this->timeout = 30000;
        $this->memorySize = 10000;
        $this->learningRate = 0.1;
        $this->similarityThreshold = 0.7;
        $this->maxReasoningDepth = 5;
    }

    public function withApiKey($apiKey) {
        $this->apiKey = $apiKey;
        return $this;
    }

    public function withTimeout($timeout) {
        $this->timeout = $timeout;
        return $this;
    }

    public function withMemorySize($memorySize) {
        $this->memorySize = $memorySize;
        return $this;
    }

    public function withLearningRate($learningRate) {
        $this->learningRate = $learningRate;
        return $this;
    }

    public function withSimilarityThreshold($similarityThreshold) {
        $this->similarityThreshold = $similarityThreshold;
        return $this;
    }

    public function withMaxReasoningDepth($maxReasoningDepth) {
        $this->maxReasoningDepth = $maxReasoningDepth;
        return $this;
    }

    public function getBaseUrl() { return $this->baseUrl; }
    public function getApiKey() { return $this->apiKey; }
    public function getTimeout() { return $this->timeout; }
    public function getMemorySize() { return $this->memorySize; }
    public function getLearningRate() { return $this->learningRate; }
    public function getSimilarityThreshold() { return $this->similarityThreshold; }
    public function getMaxReasoningDepth() { return $this->maxReasoningDepth; }
}

class BrainAISDK {
    private $config;
    private $baseUrl;

    public function __construct(BrainAIConfig $config) {
        $this->config = $config;
        $this->baseUrl = $config->getBaseUrl();
    }

    /**
     * Make HTTP request to Brain AI API
     */
    private function makeRequest($endpoint, $method = 'GET', $data = null) {
        $url = $this->baseUrl . $endpoint;
        
        $ch = curl_init();
        
        $options = [
            CURLOPT_URL => $url,
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_TIMEOUT => $this->config->getTimeout() / 1000,
            CURLOPT_CONNECTTIMEOUT => $this->config->getTimeout() / 1000,
            CURLOPT_HTTPHEADER => [
                'Content-Type: application/json',
            ],
            CURLOPT_CUSTOMREQUEST => $method,
        ];

        if ($this->config->getApiKey()) {
            $options[CURLOPT_HTTPHEADER][] = 'Authorization: Bearer ' . $this->config->getApiKey();
        }

        if ($data !== null) {
            $options[CURLOPT_POSTFIELDS] = json_encode($data);
        }

        curl_setopt_array($ch, $options);
        
        $response = curl_exec($ch);
        $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        $error = curl_error($ch);
        curl_close($ch);

        if ($error) {
            throw new BrainAIException("cURL error: $error");
        }

        if ($httpCode >= 400) {
            throw new BrainAIException("HTTP error! status: $httpCode");
        }

        $decoded = json_decode($response, true);
        if (json_last_error() !== JSON_ERROR_NONE) {
            throw new BrainAIException("Invalid JSON response: " . json_last_error_msg());
        }

        return $decoded;
    }

    /**
     * Store a memory node in the brain
     */
    public function storeMemory($content, $memoryType = 'semantic', $metadata = []) {
        $memoryNode = [
            'content' => $content,
            'type' => $memoryType,
            'strength' => 1.0,
            'timestamp' => round(microtime(true) * 1000),
            'connections' => [],
            'metadata' => $metadata,
        ];

        try {
            $result = $this->makeRequest('/api/memory', 'POST', $memoryNode);
            return $result['id'] ?? null;
        } catch (Exception $e) {
            error_log("Failed to store memory: " . $e->getMessage());
            return null;
        }
    }

    /**
     * Retrieve memory by ID
     */
    public function getMemory($id) {
        try {
            $result = $this->makeRequest("/api/memory/$id");
            return $this->parseMemoryNode($result);
        } catch (Exception $e) {
            if (strpos($e->getMessage(), '404') !== false) {
                return null;
            }
            error_log("Failed to get memory: " . $e->getMessage());
            return null;
        }
    }

    /**
     * Search memories by content similarity
     */
    public function searchMemories($query, $limit = 10) {
        $request = [
            'query' => $query,
            'limit' => $limit,
            'threshold' => $this->config->getSimilarityThreshold(),
        ];

        try {
            $result = $this->makeRequest('/api/memory/search', 'POST', $request);
            return $this->parseSearchResults($result['results'] ?? []);
        } catch (Exception $e) {
            error_log("Failed to search memories: " . $e->getMessage());
            return [];
        }
    }

    /**
     * Connect two memories
     */
    public function connectMemories($memoryId1, $memoryId2, $strength = 0.5) {
        $request = [
            'memoryId1' => $memoryId1,
            'memoryId2' => $memoryId2,
            'strength' => $strength,
        ];

        try {
            $this->makeRequest('/api/memory/connect', 'POST', $request);
            return true;
        } catch (Exception $e) {
            error_log("Failed to connect memories: " . $e->getMessage());
            return false;
        }
    }

    /**
     * Update memory strength
     */
    public function updateMemoryStrength($id, $delta) {
        $request = ['delta' => $delta];

        try {
            $this->makeRequest("/api/memory/$id/strength", 'PATCH', $request);
            return true;
        } catch (Exception $e) {
            error_log("Failed to update memory strength: " . $e->getMessage());
            return false;
        }
    }

    /**
     * Learn from experience
     */
    public function learn($pattern, $context = []) {
        $request = [
            'pattern' => $pattern,
            'context' => $context,
            'rate' => $this->config->getLearningRate(),
        ];

        try {
            $this->makeRequest('/api/learning/learn', 'POST', $request);
            return true;
        } catch (Exception $e) {
            error_log("Failed to learn: " . $e->getMessage());
            return false;
        }
    }

    /**
     * Get learning patterns
     */
    public function getLearningPatterns() {
        try {
            $result = $this->makeRequest('/api/learning/patterns');
            return $this->parseLearningPatterns($result['patterns'] ?? []);
        } catch (Exception $e) {
            error_log("Failed to get learning patterns: " . $e->getMessage());
            return [];
        }
    }

    /**
     * Perform reasoning on a query
     */
    public function reason($query, $context = []) {
        $request = [
            'query' => $query,
            'context' => $context,
            'maxDepth' => $this->config->getMaxReasoningDepth(),
        ];

        try {
            $result = $this->makeRequest('/api/reasoning/reason', 'POST', $request);
            return $this->parseReasoningResult($result);
        } catch (Exception $e) {
            error_log("Failed to reason: " . $e->getMessage());
            return null;
        }
    }

    /**
     * Add feedback for learning
     */
    public function addFeedback($feedbackType, $information, $reasoning = null) {
        $request = [
            'type' => strtolower($feedbackType),
            'information' => $information,
            'reasoning' => $reasoning,
            'timestamp' => round(microtime(true) * 1000),
        ];

        try {
            $this->makeRequest('/api/feedback', 'POST', $request);
            return true;
        } catch (Exception $e) {
            error_log("Failed to add feedback: " . $e->getMessage());
            return false;
        }
    }

    /**
     * Store vector for similarity search
     */
    public function storeVector($vector, $metadata = []) {
        $vectorEntry = [
            'vector' => $vector,
            'metadata' => $metadata,
            'timestamp' => round(microtime(true) * 1000),
        ];

        try {
            $result = $this->makeRequest('/api/vector', 'POST', $vectorEntry);
            return $result['id'] ?? null;
        } catch (Exception $e) {
            error_log("Failed to store vector: " . $e->getMessage());
            return null;
        }
    }

    /**
     * Search for similar vectors
     */
    public function searchSimilarVectors($vector, $limit = 10) {
        $request = [
            'vector' => $vector,
            'limit' => $limit,
            'threshold' => $this->config->getSimilarityThreshold(),
        ];

        try {
            $result = $this->makeRequest('/api/vector/search', 'POST', $request);
            return $this->parseSearchResults($result['results'] ?? []);
        } catch (Exception $e) {
            error_log("Failed to search similar vectors: " . $e->getMessage());
            return [];
        }
    }

    /**
     * Create or update graph node
     */
    public function createGraphNode($id, $label, $nodeType, $properties = []) {
        $node = [
            'id' => $id,
            'label' => $label,
            'type' => $nodeType,
            'properties' => $properties,
            'connections' => [],
            'weight' => 1.0,
        ];

        try {
            $this->makeRequest('/api/graph/node', 'POST', $node);
            return true;
        } catch (Exception $e) {
            error_log("Failed to create graph node: " . $e->getMessage());
            return false;
        }
    }

    /**
     * Connect graph nodes
     */
    public function connectGraphNodes($nodeId1, $nodeId2, $weight = 0.5) {
        $request = [
            'nodeId1' => $nodeId1,
            'nodeId2' => $nodeId2,
            'weight' => $weight,
        ];

        try {
            $this->makeRequest('/api/graph/connect', 'POST', $request);
            return true;
        } catch (Exception $e) {
            error_log("Failed to connect graph nodes: " . $e->getMessage());
            return false;
        }
    }

    /**
     * Get graph neighbors
     */
    public function getGraphNeighbors($nodeId, $depth = 1) {
        $request = ['depth' => $depth];

        try {
            $result = $this->makeRequest("/api/graph/neighbors/$nodeId", 'POST', $request);
            return $this->parseGraphNodes($result['neighbors'] ?? []);
        } catch (Exception $e) {
            error_log("Failed to get graph neighbors: " . $e->getMessage());
            return [];
        }
    }

    /**
     * Get system status
     */
    public function getStatus() {
        try {
            return $this->makeRequest('/api/status');
        } catch (Exception $e) {
            error_log("Failed to get status: " . $e->getMessage());
            return [];
        }
    }

    /**
     * Get system statistics
     */
    public function getStatistics() {
        try {
            return $this->makeRequest('/api/stats');
        } catch (Exception $e) {
            error_log("Failed to get statistics: " . $e->getMessage());
            return [];
        }
    }

    /**
     * Clear all data
     */
    public function clearAll() {
        try {
            $this->makeRequest('/api/clear', 'POST');
            return true;
        } catch (Exception $e) {
            error_log("Failed to clear data: " . $e->getMessage());
            return false;
        }
    }

    /**
     * Batch operations
     */
    public function batch($operations) {
        $request = ['operations' => $operations];

        try {
            $result = $this->makeRequest('/api/batch', 'POST', $request);
            return $result['results'] ?? [];
        } catch (Exception $e) {
            error_log("Failed to perform batch operations: " . $e->getMessage());
            return [];
        }
    }

    /**
     * Health check
     */
    public function healthCheck() {
        try {
            $status = $this->getStatus();
            return isset($status['status']) && $status['status'] === 'healthy';
        } catch (Exception $e) {
            error_log("Health check failed: " . $e->getMessage());
            return false;
        }
    }

    /**
     * Parse memory node from API response
     */
    private function parseMemoryNode($data) {
        if (!$data) return null;
        
        return [
            'id' => $data['id'] ?? null,
            'content' => $data['content'] ?? null,
            'type' => $data['type'] ?? null,
            'strength' => $data['strength'] ?? 0,
            'timestamp' => $data['timestamp'] ?? 0,
            'connections' => $data['connections'] ?? [],
            'metadata' => $data['metadata'] ?? [],
        ];
    }

    /**
     * Parse search results from API response
     */
    private function parseSearchResults($results) {
        if (!is_array($results)) return [];
        
        $parsed = [];
        foreach ($results as $result) {
            $parsed[] = [
                'id' => $result['id'] ?? '',
                'score' => $result['score'] ?? 0,
                'content' => $result['content'] ?? null,
                'metadata' => $result['metadata'] ?? [],
            ];
        }
        return $parsed;
    }

    /**
     * Parse learning patterns from API response
     */
    private function parseLearningPatterns($patterns) {
        if (!is_array($patterns)) return [];
        
        $parsed = [];
        foreach ($patterns as $pattern) {
            $parsed[] = [
                'pattern' => $pattern['pattern'] ?? '',
                'frequency' => $pattern['frequency'] ?? 0,
                'strength' => $pattern['strength'] ?? 0,
                'context' => $pattern['context'] ?? [],
                'last_updated' => $pattern['lastUpdated'] ?? 0,
            ];
        }
        return $parsed;
    }

    /**
     * Parse reasoning result from API response
     */
    private function parseReasoningResult($result) {
        if (!$result) return null;
        
        return [
            'conclusion' => $result['conclusion'] ?? '',
            'confidence' => $result['confidence'] ?? 0,
            'reasoning_path' => $result['reasoning_path'] ?? [],
            'supporting_evidence' => $result['supporting_evidence'] ?? [],
            'timestamp' => $result['timestamp'] ?? 0,
        ];
    }

    /**
     * Parse graph nodes from API response
     */
    private function parseGraphNodes($nodes) {
        if (!is_array($nodes)) return [];
        
        $parsed = [];
        foreach ($nodes as $node) {
            $parsed[] = [
                'id' => $node['id'] ?? '',
                'label' => $node['label'] ?? '',
                'type' => $node['type'] ?? '',
                'properties' => $node['properties'] ?? [],
                'connections' => $node['connections'] ?? [],
                'weight' => $node['weight'] ?? 0,
            ];
        }
        return $parsed;
    }
}

/**
 * Vector utilities for vector operations
 */
class VectorUtils {
    /**
     * Calculate cosine similarity between two vectors
     */
    public static function cosineSimilarity($vecA, $vecB) {
        if (count($vecA) !== count($vecB)) {
            throw new BrainAIException("Vectors must have the same length");
        }

        $dotProduct = 0;
        $normA = 0;
        $normB = 0;

        for ($i = 0; $i < count($vecA); $i++) {
            $dotProduct += $vecA[$i] * $vecB[$i];
            $normA += $vecA[$i] * $vecA[$i];
            $normB += $vecB[$i] * $vecB[$i];
        }

        $denominator = sqrt($normA) * sqrt($normB);
        return $denominator === 0 ? 0 : $dotProduct / $denominator;
    }

    /**
     * Normalize a vector
     */
    public static function normalize($vector) {
        $norm = sqrt(array_sum(array_map(function($x) { return $x * $x; }, $vector)));
        return $norm === 0 ? $vector : array_map(function($x) use ($norm) { return $x / $norm; }, $vector);
    }

    /**
     * Calculate Euclidean distance between two vectors
     */
    public static function euclideanDistance($vecA, $vecB) {
        if (count($vecA) !== count($vecB)) {
            throw new BrainAIException("Vectors must have the same length");
        }

        $sum = 0;
        for ($i = 0; $i < count($vecA); $i++) {
            $diff = $vecA[$i] - $vecB[$i];
            $sum += $diff * $diff;
        }

        return sqrt($sum);
    }

    /**
     * Generate random vector
     */
    public static function randomVector($dimensions, $min = -1, $max = 1) {
        $vector = [];
        for ($i = 0; $i < $dimensions; $i++) {
            $vector[] = $min + mt_rand() / mt_getrandmax() * ($max - $min);
        }
        return $vector;
    }
}

/**
 * Client factory for managing Brain AI SDK instances
 */
class ClientFactory {
    private static $instances = [];

    /**
     * Get or create a Brain AI SDK instance
     */
    public static function getInstance(BrainAIConfig $config, $name = 'default') {
        if (!isset(self::$instances[$name])) {
            self::$instances[$name] = new BrainAISDK($config);
        }
        return self::$instances[$name];
    }

    /**
     * Remove instance
     */
    public static function removeInstance($name) {
        unset(self::$instances[$name]);
    }

    /**
     * Clear all instances
     */
    public static function clearAll() {
        self::$instances = [];
    }
}

/**
 * Decorators for Brain AI (using traits)
 */
trait BrainAIDecorators {
    private $brainAI;

    public function setBrainAI(BrainAISDK $brainAI) {
        $this->brainAI = $brainAI;
    }

    protected function storeMemory($content, $type = 'semantic', $metadata = []) {
        if ($this->brainAI) {
            $this->brainAI->storeMemory($content, $type, $metadata);
        }
    }

    protected function learn($pattern, $context = []) {
        if ($this->brainAI) {
            $this->brainAI->learn($pattern, $context);
        }
    }

    protected function reason($query, $context = []) {
        if ($this->brainAI) {
            $this->brainAI->reason($query, $context);
        }
    }
}

// Example usage
if (basename(__FILE__) === basename($_SERVER['SCRIPT_NAME'])) {
    // Create configuration
    $config = new BrainAIConfig('http://localhost:8000');
    $config->withTimeout(30000)
            ->withMemorySize(10000)
            ->withLearningRate(0.1)
            ->withSimilarityThreshold(0.7)
            ->withMaxReasoningDepth(5);

    // Create SDK instance
    $sdk = new BrainAISDK($config);

    // Example: Store memory
    $content = [
        'text' => 'This is a test memory',
        'context' => 'testing'
    ];

    echo "Storing memory...\n";
    // Note: This would require a running Brain AI server
    // $memoryId = $sdk->storeMemory($content, 'semantic');
    // echo "Stored memory with ID: $memoryId\n";

    // Example: Search memories
    echo "Searching memories...\n";
    // $searchResults = $sdk->searchMemories('test memory', 5);
    // echo "Found " . count($searchResults) . " results\n";
    // foreach ($searchResults as $result) {
    //     echo "Result ID: {$result['id']}, Score: {$result['score']}\n";
    // }

    // Example: Learn pattern
    echo "Learning pattern...\n";
    // $sdk->learn('user_pattern', ['context1', 'context2']);
    // echo "Learned pattern successfully\n";

    // Example: Perform reasoning
    echo "Performing reasoning...\n";
    // $reasoningResult = $sdk->reason('What is the meaning of life?', ['philosophy']);
    // if ($reasoningResult) {
    //     echo "Reasoning conclusion: {$reasoningResult['conclusion']} (confidence: {$reasoningResult['confidence']})\n";
    // }

    // Example: Health check
    echo "Checking health...\n";
    // $isHealthy = $sdk->healthCheck();
    // if ($isHealthy) {
    //     echo "System is healthy\n";
    // } else {
    //     echo "System is unhealthy\n";
    // }

    // Vector utilities example
    echo "\nVector utilities example:\n";
    $vecA = [1.0, 2.0, 3.0, 4.0];
    $vecB = [2.0, 4.0, 6.0, 8.0];
    
    $similarity = VectorUtils::cosineSimilarity($vecA, $vecB);
    $distance = VectorUtils::euclideanDistance($vecA, $vecB);
    $normalized = VectorUtils::normalize($vecA);
    
    echo "Vector A: [" . implode(', ', $vecA) . "]\n";
    echo "Vector B: [" . implode(', ', $vecB) . "]\n";
    echo "Cosine similarity: " . round($similarity, 4) . "\n";
    echo "Euclidean distance: " . round($distance, 4) . "\n";
    echo "Normalized A: [" . implode(', ', array_map(function($x) { return round($x, 4); }, $normalized)) . "]\n";
}
?>