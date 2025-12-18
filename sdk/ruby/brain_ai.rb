# Brain AI Framework - Ruby SDK
# Brain-inspired AI system with persistent memory, learning, and reasoning
# 
# @author MiniMax Agent
# @version 1.0.0
# @license MIT

require 'net/http'
require 'json'
require 'uri'
require 'openssl'

module BrainAI
  # Memory types enum
  class MemoryType
    EPISODIC = 'episodic'
    SEMANTIC = 'semantic'
    PROCEDURAL = 'procedural'
    EMOTIONAL = 'emotional'
  end

  # Feedback types enum
  class FeedbackType
    POSITIVE = 'positive'
    NEGATIVE = 'negative'
    NEUTRAL = 'neutral'
  end

  # Configuration class
  class BrainAIConfig
    attr_accessor :base_url, :api_key, :timeout, :memory_size, :learning_rate, 
                  :similarity_threshold, :max_reasoning_depth

    def initialize(base_url: 'http://localhost:8000')
      @base_url = base_url
      @api_key = nil
      @timeout = 30_000
      @memory_size = 10_000
      @learning_rate = 0.1
      @similarity_threshold = 0.7
      @max_reasoning_depth = 5
    end

    def with_api_key(api_key)
      @api_key = api_key
      self
    end

    def with_timeout(timeout_ms)
      @timeout = timeout_ms
      self
    end

    def with_memory_size(size)
      @memory_size = size
      self
    end

    def with_learning_rate(rate)
      @learning_rate = rate
      self
    end

    def with_similarity_threshold(threshold)
      @similarity_threshold = threshold
      self
    end

    def with_max_reasoning_depth(depth)
      @max_reasoning_depth = depth
      self
    end
  end

  # Main Brain AI SDK class
  class BrainAISDK
    def initialize(config)
      @config = config
      @base_url = config.base_url.gsub(/\/$/, '')
      setup_http_client
    end

    # Store a memory node in the brain
    def store_memory(content, memory_type = MemoryType::SEMANTIC, metadata = {})
      memory_node = {
        'content' => content,
        'type' => memory_type,
        'strength' => 1.0,
        'timestamp' => Time.now.to_i * 1000,
        'connections' => [],
        'metadata' => metadata
      }

      result = make_request('/api/memory', 'POST', memory_node)
      result['id']
    rescue => e
      puts "Failed to store memory: #{e.message}"
      nil
    end

    # Retrieve memory by ID
    def get_memory(id)
      result = make_request("/api/memory/#{id}", 'GET')
      parse_memory_node(result) if result
    rescue => e
      puts "Failed to get memory: #{e.message}"
      nil
    end

    # Search memories by content similarity
    def search_memories(query, limit = 10)
      request = {
        'query' => query,
        'limit' => limit,
        'threshold' => @config.similarity_threshold
      }

      result = make_request('/api/memory/search', 'POST', request)
      parse_search_results(result['results']) if result && result['results']
    rescue => e
      puts "Failed to search memories: #{e.message}"
      []
    end

    # Connect two memories
    def connect_memories(memory_id1, memory_id2, strength = 0.5)
      request = {
        'memoryId1' => memory_id1,
        'memoryId2' => memory_id2,
        'strength' => strength
      }

      make_request('/api/memory/connect', 'POST', request)
      true
    rescue => e
      puts "Failed to connect memories: #{e.message}"
      false
    end

    # Update memory strength
    def update_memory_strength(id, delta)
      request = { 'delta' => delta }
      make_request("/api/memory/#{id}/strength", 'PATCH', request)
      true
    rescue => e
      puts "Failed to update memory strength: #{e.message}"
      false
    end

    # Learn from experience
    def learn(pattern, context = [])
      request = {
        'pattern' => pattern,
        'context' => context,
        'rate' => @config.learning_rate
      }

      make_request('/api/learning/learn', 'POST', request)
      true
    rescue => e
      puts "Failed to learn: #{e.message}"
      false
    end

    # Get learning patterns
    def get_learning_patterns
      result = make_request('/api/learning/patterns', 'GET')
      parse_learning_patterns(result['patterns']) if result && result['patterns']
    rescue => e
      puts "Failed to get learning patterns: #{e.message}"
      []
    end

    # Perform reasoning on a query
    def reason(query, context = [])
      request = {
        'query' => query,
        'context' => context,
        'maxDepth' => @config.max_reasoning_depth
      }

      result = make_request('/api/reasoning/reason', 'POST', request)
      parse_reasoning_result(result) if result
    rescue => e
      puts "Failed to reason: #{e.message}"
      nil
    end

    # Add feedback for learning
    def add_feedback(feedback_type, information, reasoning = nil)
      request = {
        'type' => feedback_type,
        'information' => information,
        'reasoning' => reasoning,
        'timestamp' => Time.now.to_i * 1000
      }

      make_request('/api/feedback', 'POST', request)
      true
    rescue => e
      puts "Failed to add feedback: #{e.message}"
      false
    end

    # Store vector for similarity search
    def store_vector(vector, metadata = {})
      vector_entry = {
        'vector' => vector,
        'metadata' => metadata,
        'timestamp' => Time.now.to_i * 1000
      }

      result = make_request('/api/vector', 'POST', vector_entry)
      result['id']
    rescue => e
      puts "Failed to store vector: #{e.message}"
      nil
    end

    # Search for similar vectors
    def search_similar_vectors(vector, limit = 10)
      request = {
        'vector' => vector,
        'limit' => limit,
        'threshold' => @config.similarity_threshold
      }

      result = make_request('/api/vector/search', 'POST', request)
      parse_search_results(result['results']) if result && result['results']
    rescue => e
      puts "Failed to search similar vectors: #{e.message}"
      []
    end

    # Create or update graph node
    def create_graph_node(id, label, node_type, properties = {})
      node = {
        'id' => id,
        'label' => label,
        'type' => node_type,
        'properties' => properties,
        'connections' => [],
        'weight' => 1.0
      }

      make_request('/api/graph/node', 'POST', node)
      true
    rescue => e
      puts "Failed to create graph node: #{e.message}"
      false
    end

    # Connect graph nodes
    def connect_graph_nodes(node_id1, node_id2, weight = 0.5)
      request = {
        'nodeId1' => node_id1,
        'nodeId2' => node_id2,
        'weight' => weight
      }

      make_request('/api/graph/connect', 'POST', request)
      true
    rescue => e
      puts "Failed to connect graph nodes: #{e.message}"
      false
    end

    # Get graph neighbors
    def get_graph_neighbors(node_id, depth = 1)
      request = { 'depth' => depth }
      result = make_request("/api/graph/neighbors/#{node_id}", 'POST', request)
      parse_graph_nodes(result['neighbors']) if result && result['neighbors']
    rescue => e
      puts "Failed to get graph neighbors: #{e.message}"
      []
    end

    # Get system status
    def get_status
      make_request('/api/status', 'GET')
    rescue => e
      puts "Failed to get status: #{e.message}"
      {}
    end

    # Get system statistics
    def get_statistics
      make_request('/api/stats', 'GET')
    rescue => e
      puts "Failed to get statistics: #{e.message}"
      {}
    end

    # Clear all data
    def clear_all
      make_request('/api/clear', 'POST')
      true
    rescue => e
      puts "Failed to clear data: #{e.message}"
      false
    end

    # Batch operations
    def batch(operations)
      request = { 'operations' => operations }
      result = make_request('/api/batch', 'POST', request)
      result['results'] || []
    rescue => e
      puts "Failed to perform batch operations: #{e.message}"
      []
    end

    # Health check
    def health_check
      status = get_status
      status && status['status'] == 'healthy'
    rescue => e
      puts "Health check failed: #{e.message}"
      false
    end

    private

    def setup_http_client
      # HTTP client configuration for Ruby
      # Using Net::HTTP with proper SSL and timeout settings
      @http = Net::HTTP.new(URI(@base_url).host, URI(@base_url).port)
      @http.use_ssl = @base_url.start_with?('https')
      @http.read_timeout = @config.timeout / 1000
      @http.open_timeout = @config.timeout / 1000
    end

    def make_request(endpoint, method, data = nil)
      url = URI("#{@base_url}#{endpoint}")
      request = case method
      when 'GET' then Net::HTTP::Get.new(url)
      when 'POST' then Net::HTTP::Post.new(url)
      when 'PUT' then Net::HTTP::Put.new(url)
      when 'PATCH' then Net::HTTP::Patch.new(url)
      when 'DELETE' then Net::HTTP::Delete.new(url)
      else raise "Unsupported HTTP method: #{method}"
      end

      request['Content-Type'] = 'application/json'
      request['Authorization'] = "Bearer #{@config.api_key}" if @config.api_key

      if data
        request.body = JSON.generate(data)
      end

      response = @http.request(request)
      
      unless response.is_a?(Net::HTTPSuccess)
        raise "HTTP error! status: #{response.code}"
      end

      JSON.parse(response.body)
    rescue JSON::ParserError => e
      raise "Invalid JSON response: #{e.message}"
    rescue StandardError => e
      raise "Request failed: #{e.message}"
    end

    def parse_memory_node(data)
      return nil unless data
      {
        'id' => data['id'],
        'content' => data['content'],
        'type' => data['type'],
        'strength' => data['strength'],
        'timestamp' => data['timestamp'],
        'connections' => data['connections'] || [],
        'metadata' => data['metadata'] || {}
      }
    end

    def parse_search_results(results)
      return [] unless results.is_a?(Array)
      results.map do |result|
        {
          'id' => result['id'],
          'score' => result['score'],
          'content' => result['content'],
          'metadata' => result['metadata'] || {}
        }
      end
    end

    def parse_learning_patterns(patterns)
      return [] unless patterns.is_a?(Array)
      patterns.map do |pattern|
        {
          'pattern' => pattern['pattern'],
          'frequency' => pattern['frequency'],
          'strength' => pattern['strength'],
          'context' => pattern['context'] || [],
          'last_updated' => pattern['lastUpdated']
        }
      end
    end

    def parse_reasoning_result(result)
      return nil unless result
      {
        'conclusion' => result['conclusion'],
        'confidence' => result['confidence'],
        'reasoning_path' => result['reasoning_path'] || [],
        'supporting_evidence' => result['supporting_evidence'] || [],
        'timestamp' => result['timestamp']
      }
    end

    def parse_graph_nodes(nodes)
      return [] unless nodes.is_a?(Array)
      nodes.map do |node|
        {
          'id' => node['id'],
          'label' => node['label'],
          'type' => node['type'],
          'properties' => node['properties'] || {},
          'connections' => node['connections'] || [],
          'weight' => node['weight']
        }
      end
    end
  end

  # Vector utilities for vector operations
  class VectorUtils
    def self.cosine_similarity(vec_a, vec_b)
      raise "Vectors must have the same length" unless vec_a.length == vec_b.length

      dot_product = 0.0
      norm_a = 0.0
      norm_b = 0.0

      vec_a.each_with_index do |val, i|
        dot_product += val * vec_b[i]
        norm_a += val * val
        norm_b += vec_b[i] * vec_b[i]
      end

      denominator = Math.sqrt(norm_a) * Math.sqrt(norm_b)
      denominator == 0 ? 0.0 : dot_product / denominator
    end

    def self.normalize(vector)
      norm = Math.sqrt(vector.sum { |val| val * val })
      norm == 0 ? vector : vector.map { |val| val / norm }
    end

    def self.euclidean_distance(vec_a, vec_b)
      raise "Vectors must have the same length" unless vec_a.length == vec_b.length

      Math.sqrt(vec_a.each_with_index.sum { |val, i| (val - vec_b[i]) ** 2 })
    end

    def self.random_vector(dimensions, min = -1.0, max = 1.0)
      Array.new(dimensions) { rand * (max - min) + min }
    end
  end

  # Client factory for managing Brain AI SDK instances
  class ClientFactory
    @@instances = {}

    def self.get_instance(config, name = 'default')
      @@instances[name] ||= BrainAISDK.new(config)
    end

    def self.remove_instance(name)
      @@instances.delete(name)
    end

    def self.clear_all
      @@instances.clear
    end
  end

  # Decorators for Brain AI
  module Decorators
    def self.memory(type)
      proc do |method_name, method|
        define_method(method_name) do |*args, &block|
          result = method.call(*args, &block)
          
          if respond_to?(:brain_ai)
            @brain_ai.store_memory({
              method: method_name,
              args: args,
              result: result,
              timestamp: Time.now.to_i * 1000
            }, type) rescue nil
          end
          
          result
        end
      end
    end

    def self.learn
      proc do |method_name, method|
        define_method(method_name) do |*args, &block|
          result = method.call(*args, &block)
          
          if respond_to?(:brain_ai)
            @brain_ai.learn(method_name, args.map(&:to_s)) rescue nil
          end
          
          result
        end
      end
    end

    def self.reason
      proc do |method_name, method|
        define_method(method_name) do |*args, &block|
          if respond_to?(:brain_ai)
            @brain_ai.reason(method_name, args.map(&:to_s)) rescue nil
          end
          
          method.call(*args, &block)
        end
      end
    end
  end
end

# Example usage
if __FILE__ == $0
  # Create configuration
  config = BrainAI::BrainAIConfig.new('http://localhost:8000')
    .with_timeout(30_000)
    .with_memory_size(10_000)
    .with_learning_rate(0.1)
    .with_similarity_threshold(0.7)
    .with_max_reasoning_depth(5)

  # Create SDK instance
  sdk = BrainAI::BrainAISDK.new(config)

  # Example: Store memory
  content = {
    'text' => 'This is a test memory',
    'context' => 'testing'
  }

  puts "Storing memory..."
  # Note: This would require a running Brain AI server
  # memory_id = sdk.store_memory(content, BrainAI::MemoryType::SEMANTIC)
  # puts "Stored memory with ID: #{memory_id}"

  # Example: Search memories
  puts "Searching memories..."
  # search_results = sdk.search_memories('test memory', 5)
  # puts "Found #{search_results.length} results"
  # search_results.each do |result|
  #   puts "Result ID: #{result['id']}, Score: #{result['score']}"
  # end

  # Example: Learn pattern
  puts "Learning pattern..."
  # sdk.learn('user_pattern', ['context1', 'context2'])
  # puts "Learned pattern successfully"

  # Example: Perform reasoning
  puts "Performing reasoning..."
  # reasoning_result = sdk.reason('What is the meaning of life?', ['philosophy'])
  # if reasoning_result
  #   puts "Reasoning conclusion: #{reasoning_result['conclusion']} (confidence: #{reasoning_result['confidence']})"
  # end

  # Example: Health check
  puts "Checking health..."
  # is_healthy = sdk.health_check
  # if is_healthy
  #   puts "System is healthy"
  # else
  #   puts "System is unhealthy"
  # end

  # Vector utilities example
  puts "\nVector utilities example:"
  vec_a = [1.0, 2.0, 3.0, 4.0]
  vec_b = [2.0, 4.0, 6.0, 8.0]
  
  similarity = BrainAI::VectorUtils.cosine_similarity(vec_a, vec_b)
  distance = BrainAI::VectorUtils.euclidean_distance(vec_a, vec_b)
  normalized = BrainAI::VectorUtils.normalize(vec_a)
  
  puts "Vector A: #{vec_a.inspect}"
  puts "Vector B: #{vec_b.inspect}"
  puts "Cosine similarity: #{similarity.round(4)}"
  puts "Euclidean distance: #{distance.round(4)}"
  puts "Normalized A: #{normalized.inspect}"
end