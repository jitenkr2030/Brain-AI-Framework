# Configuration Guide

Comprehensive guide to configuring the Brain AI Framework for different environments, use cases, and performance requirements.

## 📋 Table of Contents

- [Basic Configuration](#basic-configuration)
- [Advanced Configuration](#advanced-configuration)
- [Environment-Specific Settings](#environment-specific-settings)
- [Performance Tuning](#performance-tuning)
- [Security Configuration](#security-configuration)
- [Scaling Configuration](#scaling-configuration)
- [Monitoring Configuration](#monitoring-configuration)
- [Language-Specific Configuration](#language-specific-configuration)

## ⚙️ Basic Configuration

### Configuration Structure

All Brain AI SDKs share a common configuration structure with these key parameters:

```python
# Basic configuration parameters
config = {
    "base_url": "http://localhost:8000",        # Brain AI server URL
    "api_key": "your-api-key",                  # Authentication key
    "timeout": 30000,                           # Request timeout in milliseconds
    "memory_size": 10000,                       # Maximum memory entries
    "learning_rate": 0.1,                       # Learning rate (0.0 to 1.0)
    "similarity_threshold": 0.7,                # Similarity threshold (0.0 to 1.0)
    "max_reasoning_depth": 5                    # Maximum reasoning depth
}
```

### Quick Setup Examples

#### Python
```python
from brain_ai import BrainAISDK, BrainAIConfig

# Simple configuration
config = BrainAIConfig("http://localhost:8000")
sdk = BrainAISDK(config)

# With all parameters
config = BrainAIConfig(
    base_url="http://localhost:8000",
    api_key="your-api-key",
    timeout=30000,
    memory_size=10000,
    learning_rate=0.1,
    similarity_threshold=0.7,
    max_reasoning_depth=5
)
sdk = BrainAISDK(config)
```

#### JavaScript/TypeScript
```javascript
import { BrainAISDK, BrainAIConfig } from 'brain-ai-sdk';

// Simple configuration
const config = new BrainAIConfig({
    baseUrl: 'http://localhost:8000'
});
const sdk = new BrainAISDK(config);

// With all parameters
const config = new BrainAIConfig({
    baseUrl: 'http://localhost:8000',
    apiKey: 'your-api-key',
    timeout: 30000,
    memorySize: 10000,
    learningRate: 0.1,
    similarityThreshold: 0.7,
    maxReasoningDepth: 5
});
const sdk = new BrainAISDK(config);
```

#### Java
```java
import com.brainai.sdk.BrainAISDK;
import com.brainai.sdk.BrainAIConfig;

// Builder pattern configuration
BrainAIConfig config = BrainAIConfig.builder()
    .baseUrl("http://localhost:8000")
    .apiKey("your-api-key")
    .timeout(30000)
    .memorySize(10000)
    .learningRate(0.1)
    .similarityThreshold(0.7)
    .maxReasoningDepth(5)
    .build();

BrainAISDK sdk = new BrainAISDK(config);
```

## 🚀 Advanced Configuration

### Memory Management

Configure memory allocation and behavior for different use cases.

```python
# High-capacity memory configuration
high_capacity_config = BrainAIConfig(
    base_url="http://localhost:8000",
    memory_size=100000,           # 100K memories
    learning_rate=0.05,          # Conservative learning
    similarity_threshold=0.8,     # High precision
    max_reasoning_depth=10        # Deep reasoning
)

# Fast-learning configuration
fast_learning_config = BrainAIConfig(
    base_url="http://localhost:8000",
    memory_size=10000,
    learning_rate=0.3,           # Fast adaptation
    similarity_threshold=0.6,     # More permissive
    max_reasoning_depth=3         # Quick responses
)

# Research/Analysis configuration
research_config = BrainAIConfig(
    base_url="http://localhost:8000",
    memory_size=50000,
    learning_rate=0.02,          # Very conservative
    similarity_threshold=0.9,     # High accuracy requirement
    max_reasoning_depth=15        # Deep analysis
)
```

### Vector Operations

Configure vector similarity search parameters.

```python
# Precise vector search
precise_vector_config = BrainAIConfig(
    base_url="http://localhost:8000",
    similarity_threshold=0.9,     # Very precise matches
    max_similar_vectors=10,       # Limit results
    vector_dimension=512,         # Standard dimension
    distance_metric="cosine"      # Cosine similarity
)

# Broad vector search
broad_vector_config = BrainAIConfig(
    base_url="http://localhost:8000",
    similarity_threshold=0.5,     # Broader matches
    max_similar_vectors=50,       # More results
    vector_dimension=768,         # Higher dimension
    distance_metric="euclidean"   # Euclidean distance
)
```

### Learning System

Configure how the AI learns and adapts.

```python
# Conservative learning (for production)
conservative_config = BrainAIConfig(
    base_url="http://localhost:8000",
    learning_rate=0.05,           # Slow adaptation
    forget_rate=0.01,             # Slow forgetting
    pattern_threshold=0.8,        # High confidence required
    stability_window=1000,        # Large stability window
    adaptation_threshold=0.9      # Only adapt with high confidence
)

# Aggressive learning (for development/testing)
aggressive_config = BrainAIConfig(
    base_url="http://localhost:8000",
    learning_rate=0.3,            # Fast adaptation
    forget_rate=0.1,              # Fast forgetting
    pattern_threshold=0.5,        # Lower confidence requirement
    stability_window=100,         # Small stability window
    adaptation_threshold=0.6      # Adapt with moderate confidence
)
```

## 🌍 Environment-Specific Settings

### Development Environment

```python
# Development configuration
dev_config = BrainAIConfig(
    base_url="http://localhost:8000",
    api_key="dev-api-key",
    timeout=10000,                # Quick responses for development
    memory_size=1000,             # Smaller memory for testing
    learning_rate=0.2,            # Faster learning for experimentation
    similarity_threshold=0.6,     # More permissive matching
    max_reasoning_depth=3,        # Simpler reasoning
    debug_mode=True,              # Enable debug logging
    verbose_errors=True,          # Detailed error messages
    auto_clear_on_start=True      # Clear data on startup
)
```

### Testing Environment

```python
# Testing configuration
test_config = BrainAIConfig(
    base_url="http://test-brain-ai:8000",
    api_key="test-api-key",
    timeout=5000,                 # Fast timeout for tests
    memory_size=100,              # Minimal memory for tests
    learning_rate=0.0,            # Disable learning for tests
    similarity_threshold=1.0,     # Exact matches only
    max_reasoning_depth=1,        # No reasoning
    isolated_mode=True,           # Isolated test environment
    mock_responses=False,         # Use real responses
    test_data_path="/test-data"   # Path to test data
)
```

### Staging Environment

```python
# Staging configuration
staging_config = BrainAIConfig(
    base_url="https://staging-api.brain-ai.com",
    api_key=os.getenv("STAGING_API_KEY"),
    timeout=30000,
    memory_size=25000,            # Medium capacity
    learning_rate=0.1,            # Moderate learning
    similarity_threshold=0.75,    # Balanced matching
    max_reasoning_depth=6,        # Standard reasoning
    monitoring_enabled=True,      # Enable monitoring
    performance_logging=True,     # Log performance metrics
    backup_enabled=True           # Enable data backup
)
```

### Production Environment

```python
# Production configuration
prod_config = BrainAIConfig(
    base_url="https://api.brain-ai.com",
    api_key=os.getenv("PROD_API_KEY"),
    timeout=30000,
    memory_size=100000,           # Large capacity
    learning_rate=0.05,           # Conservative learning
    similarity_threshold=0.8,     # High precision
    max_reasoning_depth=8,        # Deep reasoning
    ssl_verify=True,              # SSL certificate verification
    rate_limiting=True,           # Enable rate limiting
    monitoring_enabled=True,      # Production monitoring
    alerting_enabled=True,        # Alert on issues
    backup_enabled=True,          # Regular backups
    encryption_enabled=True,      # Data encryption
    audit_logging=True           # Audit all operations
)
```

## ⚡ Performance Tuning

### High-Throughput Configuration

```python
# Optimized for high throughput
throughput_config = BrainAIConfig(
    base_url="http://localhost:8000",
    timeout=10000,                # Shorter timeout
    connection_pool_size=20,      # Large connection pool
    max_concurrent_requests=50,   # High concurrency
    batch_size=100,               # Larger batches
    cache_enabled=True,           # Enable caching
    cache_size=10000,             # Large cache
    cache_ttl=3600,               # 1 hour TTL
    async_mode=True,              # Async operations
    streaming_enabled=True        # Enable streaming
)
```

### Low-Latency Configuration

```python
# Optimized for low latency
latency_config = BrainAIConfig(
    base_url="http://localhost:8000",
    timeout=5000,                 # Quick timeout
    connection_pool_size=10,      # Moderate pool
    max_concurrent_requests=10,   # Lower concurrency
    batch_size=10,                # Small batches
    cache_enabled=True,           # Enable caching
    cache_size=5000,              # Medium cache
    cache_ttl=300,                # 5 minute TTL
    priority_queue_enabled=True,  # Priority queuing
    preloading_enabled=True       # Preload common data
)
```

### Memory-Optimized Configuration

```python
# Optimized for low memory usage
memory_config = BrainAIConfig(
    base_url="http://localhost:8000",
    memory_size=5000,             # Smaller memory
    learning_rate=0.03,           # Conservative learning
    compression_enabled=True,     # Compress stored data
    garbage_collection_interval=300, # Frequent GC
    max_memory_usage=0.8,         # 80% memory limit
    swap_enabled=True,            # Enable swap for overflow
    persistence_optimized=True,   # Optimize for storage
    cleanup_enabled=True          # Automatic cleanup
)
```

### CPU-Optimized Configuration

```python
# Optimized for CPU efficiency
cpu_config = BrainAIConfig(
    base_url="http://localhost:8000",
    learning_rate=0.02,           # Minimal CPU usage
    similarity_threshold=0.85,    # Reduce computation
    max_reasoning_depth=4,        # Shallow reasoning
    vector_dimension=256,         # Smaller vectors
    algorithm_optimization="fast", # Fast algorithms
    parallel_processing=True,     # Parallel operations
    cpu_affinity=[0, 1, 2, 3],   # CPU affinity
    thread_pool_size=8           # Optimized thread pool
)
```

## 🔒 Security Configuration

### Authentication Settings

```python
# Secure authentication configuration
secure_config = BrainAIConfig(
    base_url="https://api.brain-ai.com",
    api_key=os.getenv("SECURE_API_KEY"),
    token_expiry=3600,            # 1 hour token expiry
    refresh_token_enabled=True,   # Enable token refresh
    mfa_required=True,            # Multi-factor authentication
    ip_whitelist=["192.168.1.0/24"], # IP whitelist
    rate_limit_per_minute=100,    # Rate limiting
    request_signing=True,         # Sign requests
    encryption_level="AES-256",   # Strong encryption
    audit_trail_enabled=True,     # Log all access
    session_timeout=1800          # 30 minute sessions
)
```

### Data Protection

```python
# Data protection configuration
data_protection_config = BrainAIConfig(
    base_url="https://api.brain-ai.com",
    encryption_at_rest=True,      # Encrypt stored data
    encryption_in_transit=True,   # Encrypt data in transit
    key_rotation_interval=86400,  # Rotate keys daily
    data_masking_enabled=True,    # Mask sensitive data
    pi_identification=True,       # Identify PII
    data_retention_policy=90,     # 90 day retention
    right_to_erasure=True,        # Support data deletion
    consent_management=True,      # Manage user consent
    anonymization_enabled=True    # Anonymize data
)
```

### Network Security

```python
# Network security configuration
network_security_config = BrainAIConfig(
    base_url="https://api.brain-ai.com",
    ssl_verify=True,              # SSL certificate verification
    ssl_cipher_suites=["TLS_AES_256_GCM_SHA384"], # Strong ciphers
    certificate_pinning=True,     # Certificate pinning
    dns_sec_enabled=True,         # DNSSEC
    firewall_integration=True,    # Firewall integration
    intrusion_detection=True,     # IDS integration
    ddos_protection=True,         # DDoS protection
    geographic_restrictions=["US", "EU"], # Geographic restrictions
    compliance_mode="GDPR"        # GDPR compliance
)
```

## 📈 Scaling Configuration

### Horizontal Scaling

```python
# Horizontal scaling configuration
scaling_config = BrainAIConfig(
    base_url="http://brain-ai-cluster:8000",
    load_balancer_enabled=True,   # Enable load balancing
    health_check_interval=30,     # 30 second health checks
    failover_enabled=True,        # Enable failover
    auto_scaling_enabled=True,    # Auto-scale based on load
    min_instances=3,              # Minimum instances
    max_instances=50,             # Maximum instances
    scale_up_threshold=0.8,       # Scale up at 80% CPU
    scale_down_threshold=0.3,     # Scale down at 30% CPU
    instance_warmup_time=300,     # 5 minute warmup
    session_affinity=True         # Session affinity
)
```

### Vertical Scaling

```python
# Vertical scaling configuration
vertical_scaling_config = BrainAIConfig(
    base_url="http://brain-ai-server:8000",
    auto_scaling_enabled=True,    # Auto-scale resources
    cpu_scaling_enabled=True,     # Scale CPU
    memory_scaling_enabled=True,  # Scale memory
    storage_scaling_enabled=True, # Scale storage
    scaling_cooldown=300,         # 5 minute cooldown
    resource_monitoring=True,     # Monitor resources
    predictive_scaling=True,      # Predictive scaling
    performance_baselines={       # Performance baselines
        "cpu_threshold": 70,
        "memory_threshold": 80,
        "response_time": 100
    }
)
```

### Database Scaling

```python
# Database scaling configuration
database_scaling_config = BrainAIConfig(
    base_url="http://brain-ai-server:8000",
    database_cluster_enabled=True, # Database clustering
    read_replicas_enabled=True,    # Read replicas
    write_master_enabled=True,     # Write master
    sharding_enabled=True,         # Data sharding
    partitioning_enabled=True,     # Data partitioning
    connection_pooling=True,       # Connection pooling
    query_optimization=True,       # Query optimization
    index_optimization=True,       # Index optimization
    backup_scaling=True           # Scalable backups
)
```

## 📊 Monitoring Configuration

### Application Monitoring

```python
# Application monitoring configuration
monitoring_config = BrainAIConfig(
    base_url="http://brain-ai-server:8000",
    metrics_enabled=True,          # Enable metrics collection
    metrics_interval=60,           # 60 second intervals
    custom_metrics_enabled=True,   # Custom metrics
    performance_tracking=True,     # Performance tracking
    error_tracking=True,           # Error tracking
    user_analytics_enabled=True,   # User analytics
    business_metrics_enabled=True, # Business metrics
    real_time_alerts=True,         # Real-time alerts
    dashboard_enabled=True,        # Monitoring dashboard
    reporting_enabled=True        # Automated reporting
)
```

### Infrastructure Monitoring

```python
# Infrastructure monitoring configuration
infrastructure_monitoring_config = BrainAIConfig(
    base_url="http://brain-ai-server:8000",
    server_monitoring=True,        # Server monitoring
    network_monitoring=True,       # Network monitoring
    storage_monitoring=True,       # Storage monitoring
    cpu_monitoring=True,           # CPU monitoring
    memory_monitoring=True,        # Memory monitoring
    disk_monitoring=True,          # Disk monitoring
    network_latency_monitoring=True, # Network latency
    uptime_monitoring=True,        # Uptime monitoring
    log_aggregation=True,          # Log aggregation
    log_analysis_enabled=True     # Log analysis
)
```

### Business Monitoring

```python
# Business monitoring configuration
business_monitoring_config = BrainAIConfig(
    base_url="http://brain-ai-server:8000",
    user_journey_tracking=True,    # Track user journeys
    conversion_tracking=True,      # Track conversions
    revenue_tracking=True,         # Track revenue
    cost_tracking=True,            # Track costs
    roi_measurement=True,          # Measure ROI
    kpi_tracking=True,             # Track KPIs
    business_intelligence=True,    # Business intelligence
    predictive_analytics=True,     # Predictive analytics
    anomaly_detection=True,        # Detect anomalies
    trend_analysis_enabled=True   # Analyze trends
)
```

## 🌍 Language-Specific Configuration

### Python Configuration

```python
# Python-specific configuration
import os
from brain_ai import BrainAISDK, BrainAIConfig

# Environment-based configuration
def get_python_config():
    environment = os.getenv("ENVIRONMENT", "development")
    
    configs = {
        "development": BrainAIConfig(
            base_url="http://localhost:8000",
            timeout=10000,
            memory_size=1000,
            learning_rate=0.2,
            debug=True,
            async_mode=True
        ),
        "testing": BrainAIConfig(
            base_url="http://test-brain-ai:8000",
            timeout=5000,
            memory_size=100,
            learning_rate=0.0,
            isolated_mode=True
        ),
        "production": BrainAIConfig(
            base_url=os.getenv("BRAIN_AI_URL"),
            timeout=30000,
            memory_size=100000,
            learning_rate=0.05,
            ssl_verify=True,
            rate_limiting=True,
            monitoring_enabled=True
        )
    }
    
    return configs.get(environment, configs["development"])

# Async configuration
async_config = BrainAIConfig(
    base_url="http://localhost:8000",
    async_mode=True,
    connection_pool_size=20,
    max_concurrent_requests=50,
    timeout=30000
)

# Python with FastAPI integration
from fastapi import FastAPI

def configure_fastapi_integration():
    app = FastAPI()
    
    @app.on_event("startup")
    async def startup_event():
        config = get_python_config()
        app.state.brain_ai = BrainAISDK(config)
    
    return app
```

### JavaScript/TypeScript Configuration

```javascript
// JavaScript/TypeScript configuration
import { BrainAISDK, BrainAIConfig } from 'brain-ai-sdk';

// Environment-based configuration
function getJSConfig() {
    const environment = process.env.NODE_ENV || 'development';
    
    const configs = {
        development: {
            baseUrl: 'http://localhost:8000',
            timeout: 10000,
            memorySize: 1000,
            learningRate: 0.2,
            debug: true,
            retries: 3
        },
        testing: {
            baseUrl: 'http://test-brain-ai:8000',
            timeout: 5000,
            memorySize: 100,
            learningRate: 0.0,
            isolatedMode: true
        },
        production: {
            baseUrl: process.env.BRAIN_AI_URL,
            timeout: 30000,
            memorySize: 100000,
            learningRate: 0.05,
            sslVerify: true,
            rateLimiting: true
        }
    };
    
    return configs[environment] || configs.development;
}

// Browser configuration
function getBrowserConfig() {
    return new BrainAIConfig({
        baseUrl: window.location.origin + '/api/brain-ai',
        timeout: 10000,
        apiKey: localStorage.getItem('brainAIKey'),
        enableCaching: true,
        offlineMode: true
    });
}

// Node.js configuration
function getNodeConfig() {
    return new BrainAIConfig({
        baseUrl: process.env.BRAIN_AI_URL,
        timeout: 30000,
        apiKey: process.env.BRAIN_AI_KEY,
        connectionPool: {
            maxSockets: 10,
            maxFreeSockets: 5,
            timeout: 60000
        }
    });
}

// TypeScript type-safe configuration
interface BrainAIEnvConfig {
    baseUrl: string;
    apiKey?: string;
    timeout: number;
    memorySize: number;
    learningRate: number;
    similarityThreshold: number;
    maxReasoningDepth: number;
}

function getTypeScriptConfig(): BrainAIEnvConfig {
    return {
        baseUrl: process.env.BRAIN_AI_URL || 'http://localhost:8000',
        apiKey: process.env.BRAIN_AI_KEY,
        timeout: parseInt(process.env.BRAIN_AI_TIMEOUT || '30000'),
        memorySize: parseInt(process.env.BRAIN_AI_MEMORY_SIZE || '10000'),
        learningRate: parseFloat(process.env.BRAIN_AI_LEARNING_RATE || '0.1'),
        similarityThreshold: parseFloat(process.env.BRAIN_AI_SIMILARITY_THRESHOLD || '0.7'),
        maxReasoningDepth: parseInt(process.env.BRAIN_AI_MAX_REASONING_DEPTH || '5')
    };
}
```

### Java Configuration

```java
// Java-specific configuration
import com.brainai.sdk.BrainAISDK;
import com.brainai.sdk.BrainAIConfig;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class BrainAIConfiguration {
    
    @Value("${brain.ai.url:http://localhost:8000}")
    private String baseUrl;
    
    @Value("${brain.ai.key:}")
    private String apiKey;
    
    @Value("${brain.ai.timeout:30000}")
    private int timeout;
    
    @Value("${brain.ai.memory.size:10000}")
    private int memorySize;
    
    @Value("${brain.ai.learning.rate:0.1}")
    private double learningRate;
    
    @Bean
    public BrainAISDK brainAISDK() {
        BrainAIConfig config = BrainAIConfig.builder()
            .baseUrl(baseUrl)
            .apiKey(apiKey)
            .timeout(timeout)
            .memorySize(memorySize)
            .learningRate(learningRate)
            .similarityThreshold(0.7)
            .maxReasoningDepth(5)
            .build();
            
        return new BrainAISDK(config);
    }
    
    // Spring Boot specific configuration
    @Bean
    public BrainAIConfig brainAIConfig() {
        return BrainAIConfig.builder()
            .baseUrl(baseUrl)
            .apiKey(apiKey)
            .timeout(timeout)
            .memorySize(memorySize)
            .learningRate(learningRate)
            .connectionPoolSize(10)
            .maxRetries(3)
            .retryDelay(1000)
            .circuitBreakerEnabled(true)
            .build();
    }
}
```

### Go Configuration

```go
// Go-specific configuration
package config

import (
    "context"
    "os"
    "strconv"
    "time"
    
    "github.com/brain-ai/go-sdk"
)

type BrainAIConfig struct {
    BaseURL             string
    APIKey              string
    Timeout             time.Duration
    MemorySize          int
    LearningRate        float64
    SimilarityThreshold float64
    MaxReasoningDepth   int
    ConnectionPool      int
    MaxRetries          int
    RetryDelay          time.Duration
}

func GetBrainAIConfig() *BrainAIConfig {
    timeoutStr := getEnv("BRAIN_AI_TIMEOUT", "30s")
    retryDelayStr := getEnv("BRAIN_AI_RETRY_DELAY", "1s")
    
    timeout, _ := time.ParseDuration(timeoutStr)
    retryDelay, _ := time.ParseDuration(retryDelayStr)
    
    return &BrainAIConfig{
        BaseURL:             getEnv("BRAIN_AI_URL", "http://localhost:8000"),
        APIKey:              getEnv("BRAIN_AI_KEY", ""),
        Timeout:             timeout,
        MemorySize:          getEnvAsInt("BRAIN_AI_MEMORY_SIZE", 10000),
        LearningRate:        getEnvAsFloat("BRAIN_AI_LEARNING_RATE", 0.1),
        SimilarityThreshold: getEnvAsFloat("BRAIN_AI_SIMILARITY_THRESHOLD", 0.7),
        MaxReasoningDepth:   getEnvAsInt("BRAIN_AI_MAX_REASONING_DEPTH", 5),
        ConnectionPool:      getEnvAsInt("BRAIN_AI_CONNECTION_POOL", 10),
        MaxRetries:          getEnvAsInt("BRAIN_AI_MAX_RETRIES", 3),
        RetryDelay:          retryDelay,
    }
}

func (c *BrainAIConfig) ToBrainAISDK() brainai.BrainAIConfig {
    return brainai.BrainAIConfig{
        BaseURL:             c.BaseURL,
        APIKey:              c.APIKey,
        Timeout:             int(c.Timeout.Milliseconds()),
        MemorySize:          c.MemorySize,
        LearningRate:        c.LearningRate,
        SimilarityThreshold: c.SimilarityThreshold,
        MaxReasoningDepth:   c.MaxReasoningDepth,
    }
}

// Helper functions
func getEnv(key, defaultValue string) string {
    if value := os.Getenv(key); value != "" {
        return value
    }
    return defaultValue
}

func getEnvAsInt(key string, defaultValue int) int {
    if value := os.Getenv(key); value != "" {
        if intValue, err := strconv.Atoi(value); err == nil {
            return intValue
        }
    }
    return defaultValue
}

func getEnvAsFloat(key string, defaultValue float64) float64 {
    if value := os.Getenv(key); value != "" {
        if floatValue, err := strconv.ParseFloat(value, 64); err == nil {
            return floatValue
        }
    }
    return defaultValue
}

// Context-aware configuration
func GetConfigWithContext(ctx context.Context) brainai.BrainAIConfig {
    config := GetBrainAIConfig()
    
    // Override with context values if present
    if timeout := ctx.Value("timeout"); timeout != nil {
        if t, ok := timeout.(time.Duration); ok {
            config.Timeout = t
        }
    }
    
    return config.ToBrainAISDK()
}
```

### C# Configuration

```csharp
// C#-specific configuration
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using BrainAI;

public class BrainAIOptions
{
    public string BaseUrl { get; set; } = "http://localhost:8000";
    public string ApiKey { get; set; }
    public int Timeout { get; set; } = 30000;
    public int MemorySize { get; set; } = 10000;
    public double LearningRate { get; set; } = 0.1;
    public double SimilarityThreshold { get; set; } = 0.7;
    public int MaxReasoningDepth { get; set; } = 5;
    public int ConnectionPoolSize { get; set; } = 10;
    public bool EnableCaching { get; set; } = true;
    public bool EnableMonitoring { get; set; } = false;
}

public static class BrainAIExtensions
{
    public static IServiceCollection AddBrainAI(
        this IServiceCollection services, 
        IConfiguration configuration)
    {
        services.Configure<BrainAIOptions>(configuration.GetSection("BrainAI"));
        services.AddSingleton<BrainAISDK>(provider =>
        {
            var options = provider.GetRequiredService<IOptions<BrainAIOptions>>().Value;
            var config = new BrainAIConfig(options.BaseUrl)
                .WithApiKey(options.ApiKey)
                .WithTimeout(options.Timeout)
                .WithMemorySize(options.MemorySize)
                .WithLearningRate(options.LearningRate)
                .WithSimilarityThreshold(options.SimilarityThreshold)
                .WithMaxReasoningDepth(options.MaxReasoningDepth);
                
            return new BrainAISDK(config);
        });
        
        return services;
    }
}

// appsettings.json
{
  "BrainAI": {
    "BaseUrl": "http://localhost:8000",
    "ApiKey": "${BRAIN_AI_API_KEY}",
    "Timeout": 30000,
    "MemorySize": 10000,
    "LearningRate": 0.1,
    "SimilarityThreshold": 0.7,
    "MaxReasoningDepth": 5,
    "ConnectionPoolSize": 10,
    "EnableCaching": true,
    "EnableMonitoring": false
  }
}

// Usage in ASP.NET Core
public class HomeController : Controller
{
    private readonly BrainAISDK _brainAI;
    
    public HomeController(BrainAISDK brainAI)
    {
        _brainAI = brainAI;
    }
    
    public async Task<IActionResult> Index()
    {
        var status = await _brainAI.GetStatusAsync();
        return View(status);
    }
}
```

## 🔧 Configuration Best Practices

### Environment Variables

```bash
# .env file
BRAIN_AI_BASE_URL=http://localhost:8000
BRAIN_AI_API_KEY=your-api-key
BRAIN_AI_TIMEOUT=30000
BRAIN_AI_MEMORY_SIZE=10000
BRAIN_AI_LEARNING_RATE=0.1
BRAIN_AI_SIMILARITY_THRESHOLD=0.7
BRAIN_AI_MAX_REASONING_DEPTH=5
BRAIN_AI_ENVIRONMENT=development
```

### Configuration Validation

```python
def validate_config(config):
    """Validate configuration parameters"""
    errors = []
    
    if not config.base_url:
        errors.append("base_url is required")
    
    if config.timeout < 1000 or config.timeout > 300000:
        errors.append("timeout must be between 1000 and 300000")
    
    if config.memory_size < 1:
        errors.append("memory_size must be positive")
    
    if not (0.0 <= config.learning_rate <= 1.0):
        errors.append("learning_rate must be between 0.0 and 1.0")
    
    if not (0.0 <= config.similarity_threshold <= 1.0):
        errors.append("similarity_threshold must be between 0.0 and 1.0")
    
    if config.max_reasoning_depth < 1 or config.max_reasoning_depth > 20:
        errors.append("max_reasoning_depth must be between 1 and 20")
    
    if errors:
        raise ValueError(f"Configuration validation failed: {', '.join(errors)}")
    
    return True
```

### Configuration Profiles

```python
# configuration_profiles.py
class ConfigurationProfiles:
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"

class ConfigFactory:
    @staticmethod
    def create_config(profile: str, custom_params: dict = None) -> BrainAIConfig:
        """Factory method for creating configured SDK instances"""
        
        base_configs = {
            ConfigurationProfiles.DEVELOPMENT: BrainAIConfig(
                base_url="http://localhost:8000",
                timeout=10000,
                memory_size=1000,
                learning_rate=0.2,
                debug=True
            ),
            ConfigurationProfiles.TESTING: BrainAIConfig(
                base_url="http://test-brain-ai:8000",
                timeout=5000,
                memory_size=100,
                learning_rate=0.0,
                isolated_mode=True
            ),
            ConfigurationProfiles.STAGING: BrainAIConfig(
                base_url="https://staging-api.brain-ai.com",
                timeout=30000,
                memory_size=25000,
                learning_rate=0.1,
                monitoring_enabled=True
            ),
            ConfigurationProfiles.PRODUCTION: BrainAIConfig(
                base_url="https://api.brain-ai.com",
                timeout=30000,
                memory_size=100000,
                learning_rate=0.05,
                ssl_verify=True,
                monitoring_enabled=True,
                alerting_enabled=True
            )
        }
        
        config = base_configs.get(profile)
        if not config:
            raise ValueError(f"Unknown configuration profile: {profile}")
        
        # Apply custom parameters
        if custom_params:
            for key, value in custom_params.items():
                if hasattr(config, key):
                    setattr(config, key, value)
        
        return config
```

---

*This configuration guide provides comprehensive options for customizing Brain AI to your specific needs. Choose the configuration that best fits your use case and environment requirements.*