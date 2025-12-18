/**
 * Brain AI Framework - C# SDK
 * Brain-inspired AI system with persistent memory, learning, and reasoning
 * 
 * @author MiniMax Agent
 * @version 1.0.0
 * @license MIT
 */

using System;
using System.Collections.Generic;
using System.Net.Http;
using System.Text;
using System.Threading.Tasks;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;

namespace BrainAI
{
    /// <summary>
    /// Memory types for Brain AI
    /// </summary>
    public enum MemoryType
    {
        Episodic,
        Semantic,
        Procedural,
        Emotional
    }

    /// <summary>
    /// Feedback types for Brain AI
    /// </summary>
    public enum FeedbackType
    {
        Positive,
        Negative,
        Neutral
    }

    /// <summary>
    /// Configuration for Brain AI SDK
    /// </summary>
    public class BrainAIConfig
    {
        public string BaseUrl { get; private set; }
        public string ApiKey { get; private set; }
        public int Timeout { get; private set; }
        public int MemorySize { get; private set; }
        public double LearningRate { get; private set; }
        public double SimilarityThreshold { get; private set; }
        public int MaxReasoningDepth { get; private set; }

        public BrainAIConfig(string baseUrl = "http://localhost:8000")
        {
            BaseUrl = baseUrl.TrimEnd('/');
            ApiKey = null;
            Timeout = 30000;
            MemorySize = 10000;
            LearningRate = 0.1;
            SimilarityThreshold = 0.7;
            MaxReasoningDepth = 5;
        }

        public BrainAIConfig WithApiKey(string apiKey)
        {
            return new BrainAIConfig(BaseUrl)
            {
                ApiKey = apiKey,
                Timeout = Timeout,
                MemorySize = MemorySize,
                LearningRate = LearningRate,
                SimilarityThreshold = SimilarityThreshold,
                MaxReasoningDepth = MaxReasoningDepth
            };
        }

        public BrainAIConfig WithTimeout(int timeout)
        {
            return new BrainAIConfig(BaseUrl)
            {
                ApiKey = ApiKey,
                Timeout = timeout,
                MemorySize = MemorySize,
                LearningRate = LearningRate,
                SimilarityThreshold = SimilarityThreshold,
                MaxReasoningDepth = MaxReasoningDepth
            };
        }

        public BrainAIConfig WithMemorySize(int memorySize)
        {
            return new BrainAIConfig(BaseUrl)
            {
                ApiKey = ApiKey,
                Timeout = Timeout,
                MemorySize = memorySize,
                LearningRate = LearningRate,
                SimilarityThreshold = SimilarityThreshold,
                MaxReasoningDepth = MaxReasoningDepth
            };
        }

        public BrainAIConfig WithLearningRate(double learningRate)
        {
            return new BrainAIConfig(BaseUrl)
            {
                ApiKey = ApiKey,
                Timeout = Timeout,
                MemorySize = MemorySize,
                LearningRate = learningRate,
                SimilarityThreshold = SimilarityThreshold,
                MaxReasoningDepth = MaxReasoningDepth
            };
        }

        public BrainAIConfig WithSimilarityThreshold(double threshold)
        {
            return new BrainAIConfig(BaseUrl)
            {
                ApiKey = ApiKey,
                Timeout = Timeout,
                MemorySize = MemorySize,
                LearningRate = LearningRate,
                SimilarityThreshold = threshold,
                MaxReasoningDepth = MaxReasoningDepth
            };
        }

        public BrainAIConfig WithMaxReasoningDepth(int depth)
        {
            return new BrainAIConfig(BaseUrl)
            {
                ApiKey = ApiKey,
                Timeout = Timeout,
                MemorySize = MemorySize,
                LearningRate = LearningRate,
                SimilarityThreshold = SimilarityThreshold,
                MaxReasoningDepth = depth
            };
        }
    }

    /// <summary>
    /// Main Brain AI SDK class
    /// </summary>
    public class BrainAISDK
    {
        private readonly BrainAIConfig _config;
        private readonly HttpClient _httpClient;
        private readonly JsonSerializerSettings _jsonSettings;

        public BrainAISDK(BrainAIConfig config)
        {
            _config = config;
            _httpClient = new HttpClient
            {
                Timeout = TimeSpan.FromMilliseconds(config.Timeout)
            };
            
            _jsonSettings = new JsonSerializerSettings
            {
                NullValueHandling = NullValueHandling.Ignore,
                Formatting = Formatting.None
            };
        }

        /// <summary>
        /// Make HTTP request to Brain AI API
        /// </summary>
        private async Task<JObject> MakeRequest(string endpoint, string method = "GET", object data = null)
        {
            var url = $"{_config.BaseUrl}{endpoint}";
            var request = new HttpRequestMessage(new HttpMethod(method), url);
            
            // Set headers
            request.Headers.Add("Content-Type", "application/json");
            if (!string.IsNullOrEmpty(_config.ApiKey))
            {
                request.Headers.Add("Authorization", $"Bearer {_config.ApiKey}");
            }

            // Set body if provided
            if (data != null)
            {
                var jsonString = JsonConvert.SerializeObject(data, _jsonSettings);
                request.Content = new StringContent(jsonString, Encoding.UTF8, "application/json");
            }

            try
            {
                var response = await _httpClient.SendAsync(request);
                var responseContent = await response.Content.ReadAsStringAsync();

                if (!response.IsSuccessStatusCode)
                {
                    throw new BrainAIException($"HTTP error! status: {response.StatusCode}");
                }

                var jsonResponse = JObject.Parse(responseContent);
                return jsonResponse;
            }
            catch (Exception ex)
            {
                throw new BrainAIException($"Request failed: {ex.Message}", ex);
            }
        }

        /// <summary>
        /// Store a memory node in the brain
        /// </summary>
        public async Task<string> StoreMemoryAsync(object content, MemoryType memoryType = MemoryType.Semantic, Dictionary<string, object> metadata = null)
        {
            var memoryNode = new
            {
                content = content,
                type = memoryType.ToString().ToLower(),
                strength = 1.0,
                timestamp = DateTimeOffset.UtcNow.ToUnixTimeMilliseconds(),
                connections = new List<string>(),
                metadata = metadata ?? new Dictionary<string, object>()
            };

            try
            {
                var result = await MakeRequest("/api/memory", "POST", memoryNode);
                return result["id"]?.ToString();
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Failed to store memory: {ex.Message}");
                return null;
            }
        }

        /// <summary>
        /// Retrieve memory by ID
        /// </summary>
        public async Task<Dictionary<string, object>> GetMemoryAsync(string id)
        {
            try
            {
                var result = await MakeRequest($"/api/memory/{id}");
                return ParseMemoryNode(result);
            }
            catch (BrainAIException ex) when (ex.Message.Contains("404"))
            {
                return null;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Failed to get memory: {ex.Message}");
                return null;
            }
        }

        /// <summary>
        /// Search memories by content similarity
        /// </summary>
        public async Task<List<Dictionary<string, object>>> SearchMemoriesAsync(object query, int limit = 10)
        {
            var request = new
            {
                query = query,
                limit = limit,
                threshold = _config.SimilarityThreshold
            };

            try
            {
                var result = await MakeRequest("/api/memory/search", "POST", request);
                return ParseSearchResults(result["results"] as JArray);
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Failed to search memories: {ex.Message}");
                return new List<Dictionary<string, object>>();
            }
        }

        /// <summary>
        /// Connect two memories
        /// </summary>
        public async Task<bool> ConnectMemoriesAsync(string memoryId1, string memoryId2, double strength = 0.5)
        {
            var request = new
            {
                memoryId1 = memoryId1,
                memoryId2 = memoryId2,
                strength = strength
            };

            try
            {
                await MakeRequest("/api/memory/connect", "POST", request);
                return true;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Failed to connect memories: {ex.Message}");
                return false;
            }
        }

        /// <summary>
        /// Update memory strength
        /// </summary>
        public async Task<bool> UpdateMemoryStrengthAsync(string id, double delta)
        {
            var request = new { delta = delta };

            try
            {
                await MakeRequest($"/api/memory/{id}/strength", "PATCH", request);
                return true;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Failed to update memory strength: {ex.Message}");
                return false;
            }
        }

        /// <summary>
        /// Learn from experience
        /// </summary>
        public async Task<bool> LearnAsync(string pattern, List<string> context = null)
        {
            var request = new
            {
                pattern = pattern,
                context = context ?? new List<string>(),
                rate = _config.LearningRate
            };

            try
            {
                await MakeRequest("/api/learning/learn", "POST", request);
                return true;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Failed to learn: {ex.Message}");
                return false;
            }
        }

        /// <summary>
        /// Get learning patterns
        /// </summary>
        public async Task<List<Dictionary<string, object>>> GetLearningPatternsAsync()
        {
            try
            {
                var result = await MakeRequest("/api/learning/patterns");
                return ParseLearningPatterns(result["patterns"] as JArray);
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Failed to get learning patterns: {ex.Message}");
                return new List<Dictionary<string, object>>();
            }
        }

        /// <summary>
        /// Perform reasoning on a query
        /// </summary>
        public async Task<Dictionary<string, object>> ReasonAsync(string query, List<string> context = null)
        {
            var request = new
            {
                query = query,
                context = context ?? new List<string>(),
                maxDepth = _config.MaxReasoningDepth
            };

            try
            {
                var result = await MakeRequest("/api/reasoning/reason", "POST", request);
                return ParseReasoningResult(result);
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Failed to reason: {ex.Message}");
                return null;
            }
        }

        /// <summary>
        /// Add feedback for learning
        /// </summary>
        public async Task<bool> AddFeedbackAsync(FeedbackType feedbackType, string information, string reasoning = null)
        {
            var request = new
            {
                type = feedbackType.ToString().ToLower(),
                information = information,
                reasoning = reasoning ?? "",
                timestamp = DateTimeOffset.UtcNow.ToUnixTimeMilliseconds()
            };

            try
            {
                await MakeRequest("/api/feedback", "POST", request);
                return true;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Failed to add feedback: {ex.Message}");
                return false;
            }
        }

        /// <summary>
        /// Store vector for similarity search
        /// </summary>
        public async Task<string> StoreVectorAsync(List<double> vector, Dictionary<string, object> metadata = null)
        {
            var vectorEntry = new
            {
                vector = vector,
                metadata = metadata ?? new Dictionary<string, object>(),
                timestamp = DateTimeOffset.UtcNow.ToUnixTimeMilliseconds()
            };

            try
            {
                var result = await MakeRequest("/api/vector", "POST", vectorEntry);
                return result["id"]?.ToString();
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Failed to store vector: {ex.Message}");
                return null;
            }
        }

        /// <summary>
        /// Search for similar vectors
        /// </summary>
        public async Task<List<Dictionary<string, object>>> SearchSimilarVectorsAsync(List<double> vector, int limit = 10)
        {
            var request = new
            {
                vector = vector,
                limit = limit,
                threshold = _config.SimilarityThreshold
            };

            try
            {
                var result = await MakeRequest("/api/vector/search", "POST", request);
                return ParseSearchResults(result["results"] as JArray);
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Failed to search similar vectors: {ex.Message}");
                return new List<Dictionary<string, object>>();
            }
        }

        /// <summary>
        /// Create or update graph node
        /// </summary>
        public async Task<bool> CreateGraphNodeAsync(string id, string label, string nodeType, Dictionary<string, object> properties = null)
        {
            var node = new
            {
                id = id,
                label = label,
                type = nodeType,
                properties = properties ?? new Dictionary<string, object>(),
                connections = new List<string>(),
                weight = 1.0
            };

            try
            {
                await MakeRequest("/api/graph/node", "POST", node);
                return true;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Failed to create graph node: {ex.Message}");
                return false;
            }
        }

        /// <summary>
        /// Connect graph nodes
        /// </summary>
        public async Task<bool> ConnectGraphNodesAsync(string nodeId1, string nodeId2, double weight = 0.5)
        {
            var request = new
            {
                nodeId1 = nodeId1,
                nodeId2 = nodeId2,
                weight = weight
            };

            try
            {
                await MakeRequest("/api/graph/connect", "POST", request);
                return true;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Failed to connect graph nodes: {ex.Message}");
                return false;
            }
        }

        /// <summary>
        /// Get graph neighbors
        /// </summary>
        public async Task<List<Dictionary<string, object>>> GetGraphNeighborsAsync(string nodeId, int depth = 1)
        {
            var request = new { depth = depth };

            try
            {
                var result = await MakeRequest($"/api/graph/neighbors/{nodeId}", "POST", request);
                return ParseGraphNodes(result["neighbors"] as JArray);
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Failed to get graph neighbors: {ex.Message}");
                return new List<Dictionary<string, object>>();
            }
        }

        /// <summary>
        /// Get system status
        /// </summary>
        public async Task<Dictionary<string, object>> GetStatusAsync()
        {
            try
            {
                var result = await MakeRequest("/api/status");
                return result.ToObject<Dictionary<string, object>>();
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Failed to get status: {ex.Message}");
                return new Dictionary<string, object>();
            }
        }

        /// <summary>
        /// Get system statistics
        /// </summary>
        public async Task<Dictionary<string, object>> GetStatisticsAsync()
        {
            try
            {
                var result = await MakeRequest("/api/stats");
                return result.ToObject<Dictionary<string, object>>();
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Failed to get statistics: {ex.Message}");
                return new Dictionary<string, object>();
            }
        }

        /// <summary>
        /// Clear all data
        /// </summary>
        public async Task<bool> ClearAllAsync()
        {
            try
            {
                await MakeRequest("/api/clear", "POST");
                return true;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Failed to clear data: {ex.Message}");
                return false;
            }
        }

        /// <summary>
        /// Batch operations
        /// </summary>
        public async Task<List<Dictionary<string, object>>> BatchAsync(List<Dictionary<string, object>> operations)
        {
            var request = new { operations = operations };

            try
            {
                var result = await MakeRequest("/api/batch", "POST", request);
                return ParseBatchResults(result["results"] as JArray);
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Failed to perform batch operations: {ex.Message}");
                return new List<Dictionary<string, object>>();
            }
        }

        /// <summary>
        /// Health check
        /// </summary>
        public async Task<bool> HealthCheckAsync()
        {
            try
            {
                var status = await GetStatusAsync();
                return status.ContainsKey("status") && status["status"]?.ToString() == "healthy";
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Health check failed: {ex.Message}");
                return false;
            }
        }

        // Private helper methods

        private Dictionary<string, object> ParseMemoryNode(JObject data)
        {
            if (data == null) return null;

            return new Dictionary<string, object>
            {
                ["id"] = data["id"]?.ToString(),
                ["content"] = data["content"],
                ["type"] = data["type"]?.ToString(),
                ["strength"] = data["strength"]?.Value<double>() ?? 0,
                ["timestamp"] = data["timestamp"]?.Value<long>() ?? 0,
                ["connections"] = data["connections"]?.ToObject<List<string>>() ?? new List<string>(),
                ["metadata"] = data["metadata"]?.ToObject<Dictionary<string, object>>() ?? new Dictionary<string, object>()
            };
        }

        private List<Dictionary<string, object>> ParseSearchResults(JArray results)
        {
            if (results == null) return new List<Dictionary<string, object>>();

            var parsed = new List<Dictionary<string, object>>();
            foreach (var result in results)
            {
                parsed.Add(new Dictionary<string, object>
                {
                    ["id"] = result["id"]?.ToString() ?? "",
                    ["score"] = result["score"]?.Value<double>() ?? 0,
                    ["content"] = result["content"],
                    ["metadata"] = result["metadata"]?.ToObject<Dictionary<string, object>>() ?? new Dictionary<string, object>()
                });
            }
            return parsed;
        }

        private List<Dictionary<string, object>> ParseLearningPatterns(JArray patterns)
        {
            if (patterns == null) return new List<Dictionary<string, object>>();

            var parsed = new List<Dictionary<string, object>>();
            foreach (var pattern in patterns)
            {
                parsed.Add(new Dictionary<string, object>
                {
                    ["pattern"] = pattern["pattern"]?.ToString() ?? "",
                    ["frequency"] = pattern["frequency"]?.Value<int>() ?? 0,
                    ["strength"] = pattern["strength"]?.Value<double>() ?? 0,
                    ["context"] = pattern["context"]?.ToObject<List<string>>() ?? new List<string>(),
                    ["last_updated"] = pattern["lastUpdated"]?.Value<long>() ?? 0
                });
            }
            return parsed;
        }

        private Dictionary<string, object> ParseReasoningResult(JObject result)
        {
            if (result == null) return null;

            return new Dictionary<string, object>
            {
                ["conclusion"] = result["conclusion"]?.ToString() ?? "",
                ["confidence"] = result["confidence"]?.Value<double>() ?? 0,
                ["reasoning_path"] = result["reasoning_path"]?.ToObject<List<string>>() ?? new List<string>(),
                ["supporting_evidence"] = result["supporting_evidence"]?.ToObject<List<string>>() ?? new List<string>(),
                ["timestamp"] = result["timestamp"]?.Value<long>() ?? 0
            };
        }

        private List<Dictionary<string, object>> ParseGraphNodes(JArray nodes)
        {
            if (nodes == null) return new List<Dictionary<string, object>>();

            var parsed = new List<Dictionary<string, object>>();
            foreach (var node in nodes)
            {
                parsed.Add(new Dictionary<string, object>
                {
                    ["id"] = node["id"]?.ToString() ?? "",
                    ["label"] = node["label"]?.ToString() ?? "",
                    ["type"] = node["type"]?.ToString() ?? "",
                    ["properties"] = node["properties"]?.ToObject<Dictionary<string, object>>() ?? new Dictionary<string, object>(),
                    ["connections"] = node["connections"]?.ToObject<List<string>>() ?? new List<string>(),
                    ["weight"] = node["weight"]?.Value<double>() ?? 0
                });
            }
            return parsed;
        }

        private List<Dictionary<string, object>> ParseBatchResults(JArray results)
        {
            if (results == null) return new List<Dictionary<string, object>>();

            var parsed = new List<Dictionary<string, object>>();
            foreach (var result in results)
            {
                parsed.Add(result.ToObject<Dictionary<string, object>>());
            }
            return parsed;
        }
    }

    /// <summary>
    /// Exception class for Brain AI errors
    /// </summary>
    public class BrainAIException : Exception
    {
        public BrainAIException(string message) : base(message) { }
        public BrainAIException(string message, Exception innerException) : base(message, innerException) { }
    }

    /// <summary>
    /// Vector utilities for vector operations
    /// </summary>
    public static class VectorUtils
    {
        /// <summary>
        /// Calculate cosine similarity between two vectors
        /// </summary>
        public static double CosineSimilarity(List<double> vecA, List<double> vecB)
        {
            if (vecA.Count != vecB.Count)
                throw new ArgumentException("Vectors must have the same length");

            double dotProduct = 0;
            double normA = 0;
            double normB = 0;

            for (int i = 0; i < vecA.Count; i++)
            {
                dotProduct += vecA[i] * vecB[i];
                normA += vecA[i] * vecA[i];
                normB += vecB[i] * vecB[i];
            }

            double denominator = Math.Sqrt(normA) * Math.Sqrt(normB);
            return denominator == 0 ? 0 : dotProduct / denominator;
        }

        /// <summary>
        /// Normalize a vector
        /// </summary>
        public static List<double> Normalize(List<double> vector)
        {
            double norm = Math.Sqrt(vector.Sum(x => x * x));
            return norm == 0 ? vector : vector.Select(x => x / norm).ToList();
        }

        /// <summary>
        /// Calculate Euclidean distance between two vectors
        /// </summary>
        public static double EuclideanDistance(List<double> vecA, List<double> vecB)
        {
            if (vecA.Count != vecB.Count)
                throw new ArgumentException("Vectors must have the same length");

            double sum = 0;
            for (int i = 0; i < vecA.Count; i++)
            {
                double diff = vecA[i] - vecB[i];
                sum += diff * diff;
            }
            return Math.Sqrt(sum);
        }

        /// <summary>
        /// Generate random vector
        /// </summary>
        public static List<double> RandomVector(int dimensions, double min = -1, double max = 1)
        {
            var random = new Random();
            var vector = new List<double>();
            
            for (int i = 0; i < dimensions; i++)
            {
                vector.Add(min + random.NextDouble() * (max - min));
            }
            
            return vector;
        }
    }

    /// <summary>
    /// Client factory for managing Brain AI SDK instances
    /// </summary>
    public class ClientFactory
    {
        private static readonly Dictionary<string, BrainAISDK> _instances = new Dictionary<string, BrainAISDK>();

        /// <summary>
        /// Get or create a Brain AI SDK instance
        /// </summary>
        public static BrainAISDK GetInstance(BrainAIConfig config, string name = "default")
        {
            if (!_instances.ContainsKey(name))
            {
                _instances[name] = new BrainAISDK(config);
            }
            return _instances[name];
        }

        /// <summary>
        /// Remove instance
        /// </summary>
        public static void RemoveInstance(string name)
        {
            _instances.Remove(name);
        }

        /// <summary>
        /// Clear all instances
        /// </summary>
        public static void ClearAll()
        {
            _instances.Clear();
        }
    }

    /// <summary>
    /// Decorators for Brain AI (using extension methods)
    /// </summary>
    public static class BrainAIDecorators
    {
        public static void SetBrainAI(this object obj, BrainAISDK brainAI)
        {
            var brainAIProperty = obj.GetType().GetProperty("BrainAI");
            if (brainAIProperty != null && brainAIProperty.CanWrite)
            {
                brainAIProperty.SetValue(obj, brainAI);
            }
        }

        public static void StoreMemory(this object obj, object content, MemoryType type = MemoryType.Semantic, Dictionary<string, object> metadata = null)
        {
            var brainAIProperty = obj.GetType().GetProperty("BrainAI");
            if (brainAIProperty != null)
            {
                var brainAI = brainAIProperty.GetValue(obj) as BrainAISDK;
                brainAI?.StoreMemoryAsync(content, type, metadata);
            }
        }

        public static void Learn(this object obj, string pattern, List<string> context = null)
        {
            var brainAIProperty = obj.GetType().GetProperty("BrainAI");
            if (brainAIProperty != null)
            {
                var brainAI = brainAIProperty.GetValue(obj) as BrainAISDK;
                brainAI?.LearnAsync(pattern, context);
            }
        }

        public static void Reason(this object obj, string query, List<string> context = null)
        {
            var brainAIProperty = obj.GetType().GetProperty("BrainAI");
            if (brainAIProperty != null)
            {
                var brainAI = brainAIProperty.GetValue(obj) as BrainAISDK;
                brainAI?.ReasonAsync(query, context);
            }
        }
    }

    /// <summary>
    /// Example usage
    /// </summary>
    class Program
    {
        static async Task Main(string[] args)
        {
            // Create configuration
            var config = new BrainAIConfig("http://localhost:8000")
                .WithTimeout(30000)
                .WithMemorySize(10000)
                .WithLearningRate(0.1)
                .WithSimilarityThreshold(0.7)
                .WithMaxReasoningDepth(5);

            // Create SDK instance
            var sdk = new BrainAISDK(config);

            // Example: Store memory
            var content = new Dictionary<string, object>
            {
                ["text"] = "This is a test memory",
                ["context"] = "testing"
            };

            Console.WriteLine("Storing memory...");
            // Note: This would require a running Brain AI server
            // var memoryId = await sdk.StoreMemoryAsync(content, MemoryType.Semantic);
            // Console.WriteLine($"Stored memory with ID: {memoryId}");

            // Example: Search memories
            Console.WriteLine("Searching memories...");
            // var searchResults = await sdk.SearchMemoriesAsync("test memory", 5);
            // Console.WriteLine($"Found {searchResults.Count} results");
            // foreach (var result in searchResults)
            // {
            //     Console.WriteLine($"Result ID: {result["id"]}, Score: {result["score"]}");
            // }

            // Example: Learn pattern
            Console.WriteLine("Learning pattern...");
            // await sdk.LearnAsync("user_pattern", new List<string> { "context1", "context2" });
            // Console.WriteLine("Learned pattern successfully");

            // Example: Perform reasoning
            Console.WriteLine("Performing reasoning...");
            // var reasoningResult = await sdk.ReasonAsync("What is the meaning of life?", new List<string> { "philosophy" });
            // if (reasoningResult != null)
            // {
            //     Console.WriteLine($"Reasoning conclusion: {reasoningResult["conclusion"]} (confidence: {reasoningResult["confidence"]})");
            // }

            // Example: Health check
            Console.WriteLine("Checking health...");
            // var isHealthy = await sdk.HealthCheckAsync();
            // Console.WriteLine(isHealthy ? "System is healthy" : "System is unhealthy");

            // Vector utilities example
            Console.WriteLine("\nVector utilities example:");
            var vecA = new List<double> { 1.0, 2.0, 3.0, 4.0 };
            var vecB = new List<double> { 2.0, 4.0, 6.0, 8.0 };
            
            var similarity = VectorUtils.CosineSimilarity(vecA, vecB);
            var distance = VectorUtils.EuclideanDistance(vecA, vecB);
            var normalized = VectorUtils.Normalize(vecA);
            
            Console.WriteLine($"Vector A: [{string.Join(", ", vecA)}]");
            Console.WriteLine($"Vector B: [{string.Join(", ", vecB)}]");
            Console.WriteLine($"Cosine similarity: {similarity:F4}");
            Console.WriteLine($"Euclidean distance: {distance:F4}");
            Console.WriteLine($"Normalized A: [{string.Join(", ", normalized.Select(x => x:F4))}]");
        }
    }
}