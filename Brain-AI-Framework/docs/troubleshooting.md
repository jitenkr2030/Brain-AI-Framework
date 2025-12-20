# Troubleshooting Guide

Comprehensive troubleshooting guide for the Brain AI Framework covering common issues, solutions, and debugging techniques.

## 📋 Table of Contents

- [Common Issues](#common-issues)
- [Connection Problems](#connection-problems)
- [Authentication Issues](#authentication-issues)
- [Performance Issues](#performance-issues)
- [Memory and Storage Issues](#memory-and-storage-issues)
- [Learning and Reasoning Problems](#learning-and-reasoning-problems)
- [SDK-Specific Issues](#sdk-specific-issues)
- [Environment-Specific Problems](#environment-specific-problems)
- [Debugging Techniques](#debugging-techniques)
- [Performance Monitoring](#performance-monitoring)
- [Getting Help](#getting-help)

## 🔧 Common Issues

### Connection Timeouts

**Symptoms:**
- Requests taking too long or timing out
- "Connection refused" errors
- "Request timeout" exceptions

**Causes:**
- Server is not running
- Network connectivity issues
- Firewall blocking connections
- Incorrect server URL

**Solutions:**

```python
# Test basic connectivity
import requests
import asyncio
from brain_ai import BrainAISDK, BrainAIConfig

async def test_connection():
    try:
        # Test server connectivity
        response = requests.get("http://localhost:8000/api/health", timeout=5)
        print(f"✅ Server is reachable: {response.status_code}")
        
        # Test Brain AI SDK
        config = BrainAIConfig("http://localhost:8000")
        sdk = BrainAISDK(config)
        status = await sdk.get_status()
        print(f"✅ Brain AI SDK working: {status['status']}")
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Brain AI server")
        print("Make sure the server is running on http://localhost:8000")
        
    except asyncio.TimeoutError:
        print("⏰ Request timed out")
        print("Check network connectivity and server performance")
        
    except Exception as e:
        print(f"❌ Connection error: {e}")

# Run the test
asyncio.run(test_connection())
```

```javascript
// JavaScript connectivity test
async function testConnection() {
    try {
        // Test server connectivity
        const response = await fetch('http://localhost:8000/api/health', {
            method: 'GET',
            timeout: 5000
        });
        console.log(`✅ Server is reachable: ${response.status}`);
        
        // Test Brain AI SDK
        const { BrainAISDK } = await import('brain-ai-sdk');
        const sdk = new BrainAISDK({ baseUrl: 'http://localhost:8000' });
        const status = await sdk.getStatus();
        console.log(`✅ Brain AI SDK working: ${status.status}`);
        
    } catch (error) {
        if (error.name === 'TypeError' && error.message.includes('fetch')) {
            console.log('❌ Cannot connect to Brain AI server');
            console.log('Make sure the server is running on http://localhost:8000');
        } else if (error.message.includes('timeout')) {
            console.log('⏰ Request timed out');
            console.log('Check network connectivity and server performance');
        } else {
            console.log(`❌ Connection error: ${error.message}`);
        }
    }
}

testConnection();
```

### Invalid API Key Errors

**Symptoms:**
- "Unauthorized" or "Invalid API key" messages
- HTTP 401 errors
- Authentication failures

**Causes:**
- Missing or incorrect API key
- API key expired
- Wrong environment variable name

**Solutions:**

```python
# Check API key configuration
import os
from brain_ai import BrainAISDK, BrainAIConfig

def check_api_key():
    # Method 1: Environment variable
    api_key = os.getenv("BRAIN_AI_API_KEY")
    if api_key:
        print(f"✅ API key found in environment: {api_key[:10]}...")
    else:
        print("❌ API key not found in environment")
    
    # Method 2: Direct configuration
    config = BrainAIConfig(
        base_url="http://localhost:8000",
        api_key="your-actual-api-key-here"
    )
    
    try:
        sdk = BrainAISDK(config)
        # Test with a simple request
        status = asyncio.run(sdk.get_status())
        print("✅ API key is valid")
    except Exception as e:
        print(f"❌ API key validation failed: {e}")

# Check different environment variable names
env_vars_to_check = [
    "BRAIN_AI_API_KEY",
    "BRAIN_AI_KEY", 
    "BRAINAI_API_KEY",
    "API_KEY"
]

for var_name in env_vars_to_check:
    value = os.getenv(var_name)
    if value:
        print(f"Found {var_name}: {value[:10]}...")
    else:
        print(f"Missing {var_name}")
```

### Memory Issues

**Symptoms:**
- Out of memory errors
- Slow performance
- Memory leaks

**Causes:**
- Too much data stored
- Memory not being freed
- Improper cleanup

**Solutions:**

```python
# Memory management
import asyncio
from brain_ai import BrainAISDK, BrainAIConfig

async def manage_memory():
    config = BrainAIConfig(
        base_url="http://localhost:8000",
        memory_size=10000  # Set appropriate limit
    )
    sdk = BrainAISDK(config)
    
    # Monitor memory usage
    stats = await sdk.get_statistics()
    memory_usage = stats.get('memory_usage', 0)
    
    print(f"Memory usage: {memory_usage:.1%}")
    
    if memory_usage > 0.8:
        print("⚠️ High memory usage detected")
        
        # Clean up old data
        await cleanup_old_memories(sdk)
        
        # Force garbage collection
        import gc
        gc.collect()
    
    # Check for memory leaks
    await detect_memory_leaks(sdk)

async def cleanup_old_memories(sdk):
    """Clean up old or low-value memories"""
    # Get memory statistics
    stats = await sdk.get_statistics()
    total_memories = stats.get('total_memories', 0)
    
    if total_memories > 8000:  # 80% of capacity
        print("🧹 Cleaning up old memories...")
        
        # Find low-value memories to delete
        low_value_memories = await sdk.search_memories(
            {"strength": {"<": 0.1}},  # Very weak memories
            1000
        )
        
        # Delete weak memories
        deleted_count = 0
        for memory in low_value_memories:
            await sdk.delete_memory(memory['id'])
            deleted_count += 1
        
        print(f"🗑️ Deleted {deleted_count} low-value memories")

async def detect_memory_leaks(sdk):
    """Detect potential memory leaks"""
    # Monitor memory growth over time
    for i in range(5):
        stats = await sdk.get_statistics()
        memory_usage = stats.get('memory_usage', 0)
        print(f"Memory check {i+1}: {memory_usage:.1%}")
        
        if i > 0:
            prev_usage = previous_memory_usage
            growth = memory_usage - prev_usage
            
            if growth > 0.1:  # 10% growth
                print(f"⚠️ Memory growth detected: {growth:.1%}")
                print("Consider investigating memory leaks")
        
        previous_memory_usage = memory_usage
        await asyncio.sleep(10)  # Wait 10 seconds between checks
```

## 🔌 Connection Problems

### DNS Resolution Issues

**Symptoms:**
- "Name or service not known" errors
- DNS lookup failures

**Solutions:**

```python
# DNS troubleshooting
import socket
import asyncio
from brain_ai import BrainAISDK, BrainAIConfig

def troubleshoot_dns():
    server_url = "http://localhost:8000"
    
    try:
        # Extract hostname from URL
        from urllib.parse import urlparse
        parsed = urlparse(server_url)
        hostname = parsed.hostname
        port = parsed.port or 80
        
        print(f"🔍 Resolving hostname: {hostname}")
        
        # Test DNS resolution
        ip_address = socket.gethostbyname(hostname)
        print(f"✅ DNS resolution successful: {hostname} -> {ip_address}")
        
        # Test port connectivity
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((hostname, port))
        sock.close()
        
        if result == 0:
            print(f"✅ Port {port} is accessible")
        else:
            print(f"❌ Port {port} is not accessible")
            
    except socket.gaierror as e:
        print(f"❌ DNS resolution failed: {e}")
        print("Try these solutions:")
        print("1. Check your internet connection")
        print("2. Verify the server URL is correct")
        print("3. Try using IP address instead of hostname")
        print("4. Check DNS settings")
        
    except Exception as e:
        print(f"❌ Connection test failed: {e}")

# Alternative using async DNS
async def async_dns_test():
    import aiohttp
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:8000/api/health") as resp:
                print(f"✅ DNS and connection test successful: {resp.status}")
    except aiohttp.ClientConnectorError as e:
        print(f"❌ Connection error: {e}")
        print("Server might be down or URL is incorrect")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
```

### SSL/TLS Certificate Issues

**Symptoms:**
- SSL certificate errors
- "Certificate verification failed" messages
- HTTPS connection failures

**Solutions:**

```python
# SSL troubleshooting
import ssl
import requests
from brain_ai import BrainAISDK, BrainAIConfig

def troubleshoot_ssl():
    server_url = "https://api.brain-ai.com"
    
    # Check SSL certificate
    try:
        # Disable SSL verification temporarily (for testing only)
        response = requests.get(server_url, verify=False)
        print("✅ Server responds without SSL verification")
        
        # Check certificate details
        response = requests.get(server_url, verify=True)
        cert = response.raw.connection.sock.getpeercert()
        
        print("📋 Certificate information:")
        print(f"Subject: {cert['subject']}")
        print(f"Issuer: {cert['issuer']}")
        print(f"Valid until: {cert['notAfter']}")
        
    except requests.exceptions.SSLError as e:
        print(f"❌ SSL error: {e}")
        print("Solutions:")
        print("1. Update your system's certificate store")
        print("2. Check if the server's SSL certificate is valid")
        print("3. Try updating the server URL to use HTTP temporarily")
        
    except Exception as e:
        print(f"❌ SSL troubleshooting failed: {e}")

# Custom SSL context for Brain AI SDK
def create_custom_ssl_context():
    # Create custom SSL context
    ssl_context = ssl.create_default_context()
    
    # Load custom certificates if needed
    # ssl_context.load_verify_locations('/path/to/certificate.pem')
    
    # Disable certificate verification (not recommended for production)
    # ssl_context.check_hostname = False
    # ssl_context.verify_mode = ssl.CERT_NONE
    
    return ssl_context

# Use custom SSL context
async def test_with_custom_ssl():
    config = BrainAIConfig(
        base_url="https://api.brain-ai.com",
        ssl_context=create_custom_ssl_context()
    )
    sdk = BrainAISDK(config)
    
    try:
        status = await sdk.get_status()
        print("✅ Custom SSL configuration works")
    except Exception as e:
        print(f"❌ Custom SSL configuration failed: {e}")
```

## 🔐 Authentication Issues

### API Key Problems

**Symptoms:**
- 401 Unauthorized responses
- "Invalid API key" messages
- Authentication failures

**Solutions:**

```python
# API key troubleshooting
import os
import asyncio
from brain_ai import BrainAISDK, BrainAIConfig

async def troubleshoot_api_key():
    # Method 1: Check environment variables
    print("🔍 Checking environment variables...")
    env_vars = [
        "BRAIN_AI_API_KEY",
        "BRAIN_AI_KEY",
        "BRAINAI_API_KEY", 
        "API_KEY"
    ]
    
    found_keys = []
    for var in env_vars:
        value = os.getenv(var)
        if value:
            found_keys.append((var, value))
            print(f"✅ Found {var}: {value[:10]}...")
    
    if not found_keys:
        print("❌ No API key found in environment variables")
        print("Set BRAIN_AI_API_KEY environment variable")
        return
    
    # Method 2: Test each found key
    for var_name, key_value in found_keys:
        print(f"\n🧪 Testing {var_name}...")
        try:
            config = BrainAIConfig(
                base_url="http://localhost:8000",  # Use local server for testing
                api_key=key_value
            )
            sdk = BrainAISDK(config)
            
            # Test with a simple request
            status = await sdk.get_status()
            print(f"✅ {var_name} is valid")
            
        except Exception as e:
            error_msg = str(e).lower()
            if "unauthorized" in error_msg or "401" in error_msg:
                print(f"❌ {var_name} is invalid or expired")
            elif "forbidden" in error_msg:
                print(f"❌ {var_name} lacks required permissions")
            else:
                print(f"❌ {var_name} test failed: {e}")

# Method 3: Generate new API key
async def generate_new_api_key():
    """Help users generate a new API key"""
    print("🔑 To generate a new API key:")
    print("1. Visit https://brain-ai.com/dashboard")
    print("2. Go to API Keys section")
    print("3. Click 'Generate New Key'")
    print("4. Copy the new key")
    print("5. Set it as environment variable: export BRAIN_AI_API_KEY=your-new-key")
```

### Token Expiration

**Symptoms:**
- Authentication works initially but fails later
- Tokens expiring unexpectedly
- Session timeouts

**Solutions:**

```python
# Token management
import time
from datetime import datetime, timedelta
from brain_ai import BrainAISDK, BrainAIConfig

class TokenManager:
    def __init__(self):
        self.token = None
        self.token_expiry = None
        self.refresh_token = None
        
    async def authenticate(self, config):
        """Authenticate and manage tokens"""
        try:
            # Attempt to get status (implicit authentication)
            sdk = BrainAISDK(config)
            status = await sdk.get_status()
            
            if status.get('authenticated'):
                print("✅ Authentication successful")
                return True
            else:
                print("❌ Authentication failed")
                return False
                
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            return False
    
    def is_token_expired(self):
        """Check if current token is expired"""
        if not self.token_expiry:
            return True
        
        return datetime.now() >= self.token_expiry
    
    async def refresh_authentication(self, config):
        """Refresh authentication token"""
        if not self.refresh_token:
            print("❌ No refresh token available")
            return False
        
        try:
            # In practice, you would call a refresh endpoint
            # This is a simplified example
            print("🔄 Refreshing authentication token...")
            
            # Simulate token refresh
            self.token = "new-token"
            self.token_expiry = datetime.now() + timedelta(hours=1)
            
            print("✅ Token refreshed successfully")
            return True
            
        except Exception as e:
            print(f"❌ Token refresh failed: {e}")
            return False

# Usage
async def manage_authentication():
    token_manager = TokenManager()
    
    config = BrainAIConfig(
        base_url="http://localhost:8000",
        api_key="your-api-key"
    )
    
    # Authenticate
    await token_manager.authenticate(config)
    
    # Check token periodically
    while True:
        if token_manager.is_token_expired():
            print("🔑 Token expired, refreshing...")
            await token_manager.refresh_authentication(config)
        
        # Do work...
        await asyncio.sleep(60)  # Check every minute
```

## ⚡ Performance Issues

### Slow Response Times

**Symptoms:**
- Requests taking too long
- High latency
- Timeout errors

**Solutions:**

```python
# Performance optimization
import asyncio
import time
from brain_ai import BrainAISDK, BrainAIConfig

async def optimize_performance():
    config = BrainAIConfig(
        base_url="http://localhost:8000",
        timeout=5000,              # Shorter timeout
        memory_size=5000,          # Smaller memory for faster access
        similarity_threshold=0.8,  # Higher threshold for faster matching
        max_reasoning_depth=3      # Shallow reasoning
    )
    sdk = BrainAISDK(config)
    
    # Measure performance
    start_time = time.time()
    
    try:
        # Test basic operations
        memory_id = await sdk.store_memory(
            content={"test": "performance measurement"},
            type="semantic"
        )
        
        search_results = await sdk.search_memories("test", limit=5)
        
        end_time = time.time()
        response_time = (end_time - start_time) * 1000
        
        print(f"⏱️ Response time: {response_time:.2f}ms")
        
        if response_time > 1000:
            print("⚠️ Slow response time detected")
            await diagnose_performance_issues(sdk)
        
    except asyncio.TimeoutError:
        print("⏰ Request timed out")
        print("Consider reducing memory size or increasing timeout")

async def diagnose_performance_issues(sdk):
    """Diagnose performance issues"""
    print("🔍 Diagnosing performance issues...")
    
    # Check server status
    try:
        status = await sdk.get_status()
        server_load = status.get('cpu_usage', 0)
        memory_usage = status.get('memory_usage', 0)
        
        print(f"Server CPU usage: {server_load:.1%}")
        print(f"Server memory usage: {memory_usage:.1%}")
        
        if server_load > 0.8:
            print("⚠️ High server CPU usage")
            print("Consider scaling up the server or optimizing queries")
        
        if memory_usage > 0.8:
            print("⚠️ High server memory usage")
            print("Consider increasing server memory or clearing old data")
            
    except Exception as e:
        print(f"❌ Could not get server status: {e}")
    
    # Check network latency
    import aiohttp
    try:
        async with aiohttp.ClientSession() as session:
            start = time.time()
            async with session.get("http://localhost:8000/api/health") as resp:
                await resp.text()
            latency = (time.time() - start) * 1000
            print(f"🌐 Network latency: {latency:.2f}ms")
            
            if latency > 100:
                print("⚠️ High network latency")
                print("Consider using a closer server or optimizing network")
                
    except Exception as e:
        print(f"❌ Could not measure network latency: {e}")

# Caching for performance
class PerformanceOptimizer:
    def __init__(self, sdk):
        self.sdk = sdk
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes
    
    async def cached_search(self, query, limit=10):
        cache_key = f"search_{hash(str(query))}_{limit}"
        current_time = time.time()
        
        # Check cache
        if cache_key in self.cache:
            cached_result, timestamp = self.cache[cache_key]
            if current_time - timestamp < self.cache_ttl:
                print("📦 Using cached result")
                return cached_result
        
        # Perform search
        results = await self.sdk.search_memories(query, limit)
        
        # Cache result
        self.cache[cache_key] = (results, current_time)
        
        return results
```

### Memory Leaks

**Symptoms:**
- Increasing memory usage over time
- Out of memory errors
- Degrading performance

**Solutions:**

```python
# Memory leak detection and prevention
import asyncio
import gc
import psutil
from brain_ai import BrainAISDK, BrainAIConfig

class MemoryLeakDetector:
    def __init__(self):
        self.measurements = []
        self.sdk = None
    
    async def monitor_memory(self, sdk):
        """Monitor memory usage over time"""
        self.sdk = sdk
        
        for i in range(10):
            # Get process memory usage
            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024
            
            # Get Brain AI memory statistics
            try:
                stats = await sdk.get_statistics()
                ai_memory = stats.get('memory_usage', 0)
            except:
                ai_memory = 0
            
            measurement = {
                'timestamp': time.time(),
                'process_memory_mb': memory_mb,
                'ai_memory_usage': ai_memory,
                'measurement_number': i + 1
            }
            
            self.measurements.append(measurement)
            
            print(f"Memory check {i+1}: Process={memory_mb:.1f}MB, AI={ai_memory:.1%}")
            
            # Check for memory growth
            if i > 0:
                prev_measurement = self.measurements[i-1]
                growth_mb = memory_mb - prev_measurement['process_memory_mb']
                growth_percent = (growth_mb / prev_measurement['process_memory_mb']) * 100
                
                if growth_percent > 10:  # 10% growth
                    print(f"⚠️ Memory growth detected: {growth_percent:.1f}%")
                    await self.investigate_memory_leak()
            
            await asyncio.sleep(10)  # Wait 10 seconds between measurements
    
    async def investigate_memory_leak(self):
        """Investigate potential memory leaks"""
        print("🔍 Investigating memory leak...")
        
        # Force garbage collection
        gc.collect()
        
        # Check for unclosed resources
        if self.sdk:
            # Get current memory statistics
            stats = await self.sdk.get_statistics()
            total_memories = stats.get('total_memories', 0)
            
            print(f"Total memories: {total_memories}")
            
            if total_memories > 50000:
                print("⚠️ High memory count detected")
                await self.cleanup_memories()
    
    async def cleanup_memories(self):
        """Clean up old or weak memories"""
        if not self.sdk:
            return
        
        print("🧹 Cleaning up memories...")
        
        # Find weak memories
        weak_memories = await self.sdk.search_memories(
            {"strength": {"<": 0.05}},  # Very weak memories
            1000
        )
        
        deleted_count = 0
        for memory in weak_memories:
            try:
                await self.sdk.delete_memory(memory['id'])
                deleted_count += 1
            except Exception as e:
                print(f"Failed to delete memory {memory['id']}: {e}")
        
        print(f"🗑️ Deleted {deleted_count} weak memories")
        
        # Force garbage collection after cleanup
        gc.collect()

# Usage
async def detect_memory_leaks():
    config = BrainAIConfig("http://localhost:8000")
    sdk = BrainAISDK(config)
    
    detector = MemoryLeakDetector()
    await detector.monitor_memory(sdk)
```

## 📚 Learning and Reasoning Problems

### AI Not Learning

**Symptoms:**
- AI responses don't improve over time
- No new patterns being learned
- Repeated mistakes

**Solutions:**

```python
# Learning optimization
import asyncio
from brain_ai import BrainAISDK, BrainAIConfig

async def optimize_learning():
    config = BrainAIConfig(
        base_url="http://localhost:8000",
        learning_rate=0.2,           # Increase learning rate
        similarity_threshold=0.6,    # Lower threshold for more patterns
        max_reasoning_depth=5        # Deeper reasoning
    )
    sdk = BrainAISDK(config)
    
    # Check current learning patterns
    patterns = await sdk.get_learning_patterns()
    print(f"📊 Current learning patterns: {len(patterns)}")
    
    if len(patterns) == 0:
        print("❌ No learning patterns detected")
        print("The AI may need more data or better learning configuration")
        
        # Add some training data
        await provide_training_data(sdk)
    
    # Provide feedback to improve learning
    await provide_feedback(sdk)
    
    # Monitor learning progress
    await monitor_learning_progress(sdk)

async def provide_training_data(sdk):
    """Provide training data to improve learning"""
    print("🎓 Providing training data...")
    
    # Store some example memories with clear patterns
    training_memories = [
        {
            "content": {"text": "User prefers detailed explanations"},
            "type": "emotional",
            "metadata": {"pattern": "user_preference"}
        },
        {
            "content": {"text": "User asks follow-up questions frequently"},
            "type": "episodic", 
            "metadata": {"pattern": "user_behavior"}
        },
        {
            "content": {"text": "User responds well to examples"},
            "type": "emotional",
            "metadata": {"pattern": "learning_style"}
        }
    ]
    
    for memory_data in training_memories:
        await sdk.store_memory(
            content=memory_data["content"],
            type=memory_data["type"],
            metadata=memory_data["metadata"]
        )
    
    print("✅ Training data added")

async def provide_feedback(sdk):
    """Provide feedback to improve learning"""
    print("📝 Providing feedback...")
    
    feedback_examples = [
        ("positive", "User was very satisfied with the explanation", "Clear and detailed response"),
        ("positive", "User found the solution helpful", "Problem was solved effectively"),
        ("negative", "User was confused by the response", "Too technical for user level"),
        ("negative", "User asked for clarification", "Response was unclear")
    ]
    
    for feedback_type, information, reasoning in feedback_examples:
        await sdk.add_feedback(feedback_type, information, reasoning)
    
    print("✅ Feedback provided")

async def monitor_learning_progress(sdk):
    """Monitor learning progress over time"""
    print("📈 Monitoring learning progress...")
    
    for i in range(5):
        patterns = await sdk.get_learning_patterns()
        
        strong_patterns = [p for p in patterns if p['strength'] > 0.7]
        learning_accuracy = len(strong_patterns) / len(patterns) if patterns else 0
        
        print(f"Progress check {i+1}:")
        print(f"  Total patterns: {len(patterns)}")
        print(f"  Strong patterns: {len(strong_patterns)}")
        print(f"  Learning accuracy: {learning_accuracy:.1%}")
        
        if learning_accuracy > 0.8:
            print("✅ Good learning progress!")
            break
        elif learning_accuracy < 0.3:
            print("⚠️ Poor learning progress")
            print("Consider providing more feedback or adjusting learning rate")
        
        await asyncio.sleep(5)  # Wait 5 seconds between checks

# Test learning with specific scenarios
async def test_learning_scenarios(sdk):
    """Test learning with specific scenarios"""
    print("🧪 Testing learning scenarios...")
    
    # Scenario 1: User preferences
    await sdk.learn("user_prefers_examples", ["user_feedback", "positive_response"])
    await sdk.add_feedback("positive", "User loved the examples", "Visual examples work well")
    
    # Scenario 2: Error patterns
    await sdk.learn("common_error_pattern", ["user_confusion", "technical_issues"])
    await sdk.add_feedback("negative", "User was confused by jargon", "Simplify language")
    
    # Scenario 3: Success patterns
    await sdk.learn("success_pattern", ["user_satisfaction", "problem_solved"])
    await sdk.add_feedback("positive", "Problem was solved quickly", "Direct approach works")
    
    # Check if patterns were learned
    patterns = await sdk.get_learning_patterns()
    print(f"✅ Learned {len(patterns)} new patterns from scenarios")
```

## 🐛 SDK-Specific Issues

### Python SDK Issues

```python
# Python-specific troubleshooting
import asyncio
import sys
import traceback
from brain_ai import BrainAISDK, BrainAIConfig

async def troubleshoot_python_sdk():
    """Troubleshoot Python SDK specific issues"""
    
    # Check Python version
    python_version = sys.version_info
    print(f"🐍 Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    if python_version < (3, 8):
        print("⚠️ Python version is too old. Upgrade to Python 3.8+")
        return
    
    # Check installed packages
    try:
        import brain_ai
        print(f"✅ Brain AI SDK version: {brain_ai.__version__}")
    except ImportError:
        print("❌ Brain AI SDK not installed")
        print("Install with: pip install brain-ai-sdk")
        return
    
    # Test async functionality
    print("🔄 Testing async functionality...")
    try:
        config = BrainAIConfig("http://localhost:8000")
        sdk = BrainAISDK(config)
        
        # Test async operations
        status = await sdk.get_status()
        print("✅ Async operations working")
        
    except asyncio.TimeoutError:
        print("⏰ Async timeout - check server connection")
    except Exception as e:
        print(f"❌ Async error: {e}")
        traceback.print_exc()
    
    # Test type hints
    print("🔍 Testing type hints...")
    try:
        # This will work if type hints are properly installed
        config: BrainAIConfig = BrainAIConfig()
        print("✅ Type hints working")
    except Exception as e:
        print(f"⚠️ Type hints issue: {e}")
    
    # Check event loop issues
    print("🔄 Checking event loop...")
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            print("✅ Event loop is running")
        else:
            print("⚠️ Event loop is not running")
    except RuntimeError:
        print("⚠️ No event loop found")
        print("Make sure to use asyncio.run() or create event loop properly")

# Common Python error solutions
def solve_common_python_errors():
    """Solutions to common Python SDK errors"""
    
    print("🔧 Common Python SDK error solutions:")
    
    print("\n1. ImportError: No module named 'brain_ai'")
    print("   Solution: pip install brain-ai-sdk")
    
    print("\n2. TypeError: object of type 'coroutine' has no len()")
    print("   Solution: Make sure to await async functions")
    print("   ❌ results = sdk.search_memories('query', 10)")
    print("   ✅ results = await sdk.search_memories('query', 10)")
    
    print("\n3. RuntimeError: Event loop is closed")
    print("   Solution: Use asyncio.run() or proper event loop management")
    print("   ✅ asyncio.run(main())")
    
    print("\n4. MemoryError or high memory usage")
    print("   Solution: Configure memory limits and clean up")
    print("   config = BrainAIConfig(memory_size=5000)")
    
    print("\n5. SSL Certificate errors")
    print("   Solution: Update certificates or disable verification (dev only)")
    print("   config = BrainAIConfig(ssl_verify=False)")
```

### JavaScript SDK Issues

```javascript
// JavaScript-specific troubleshooting
async function troubleshootJavaScriptSDK() {
    console.log("🔍 Troubleshooting JavaScript SDK...");
    
    // Check Node.js version
    const nodeVersion = process.version;
    console.log(`📦 Node.js version: ${nodeVersion}`);
    
    // Check if brain-ai-sdk is installed
    try {
        const brainAI = await import('brain-ai-sdk');
        console.log("✅ Brain AI SDK installed");
Version        console.log(`: ${brainAI.version || 'unknown'}`);
    } catch (error) {
        if (error.code === 'MODULE_NOT_FOUND') {
            console.log("❌ Brain AI SDK not installed");
            console.log("Install with: npm install brain-ai-sdk");
        } else {
            console.log(`❌ Import error: ${error.message}`);
        }
    }
    
    // Test async/await functionality
    console.log("🔄 Testing async/await...");
    try {
        const { BrainAISDK } = await import('brain-ai-sdk');
        const sdk = new BrainAISDK({ baseUrl: 'http://localhost:8000' });
        
        const status = await sdk.getStatus();
        console.log("✅ Async/await working");
        
    } catch (error) {
        if (error.name === 'TypeError') {
            console.log("❌ Async/await error - make sure to use await");
            console.log("❌ const status = sdk.getStatus();");
            console.log("✅ const status = await sdk.getStatus();");
        } else {
            console.log(`❌ Async error: ${error.message}`);
        }
    }
    
    // Test promise handling
    console.log("📋 Testing promise handling...");
    try {
        const { BrainAISDK } = await import('brain-ai-sdk');
        const sdk = new BrainAISDK({ baseUrl: 'http://localhost:8000' });
        
        // Using .then() instead of await
        sdk.getStatus()
            .then(status => {
                console.log("✅ Promise handling working");
            })
            .catch(error => {
                console.log(`❌ Promise error: ${error.message}`);
            });
            
    } catch (error) {
        console.log(`❌ Promise test error: ${error.message}`);
    }
}

// Common JavaScript error solutions
function solveCommonJSErrors() {
    console.log("🔧 Common JavaScript SDK error solutions:");
    
    console.log("\n1. Cannot find module 'brain-ai-sdk'");
    console.log("   Solution: npm install brain-ai-sdk");
    console.log("   Or: yarn add brain-ai-sdk");
    
    console.log("\n2. TypeError: Cannot read properties of undefined");
    console.log("   Solution: Check if SDK is properly imported");
    console.log("   ❌ const sdk = new BrainAI();");
    console.log("   ✅ const { BrainAISDK } = require('brain-ai-sdk');");
    console.log("   ✅ const sdk = new BrainAISDK(config);");
    
    console.log("\n3. SyntaxError: await is only valid in async functions");
    console.log("   Solution: Make function async or use .then()");
    console.log("   ✅ async function main() { await sdk.method(); }");
    
    console.log("\n4. Network errors in browser");
    console.log("   Solution: Check CORS settings and network connectivity");
    console.log("   Use browser developer tools to debug network requests");
    
    console.log("\n5. Timeout errors");
    console.log("   Solution: Increase timeout or check server performance");
    console.log("   config = { baseUrl, timeout: 60000 }");
}

// Browser-specific troubleshooting
function troubleshootBrowserSDK() {
    console.log("🌐 Troubleshooting browser SDK...");
    
    // Check if fetch API is available
    if (typeof fetch === 'undefined') {
        console.log("❌ Fetch API not available");
        console.log("Solution: Use a polyfill or update browser");
    } else {
        console.log("✅ Fetch API available");
    }
    
    // Check CORS issues
    console.log("🔍 Checking CORS...");
    fetch('http://localhost:8000/api/health')
        .then(response => {
            console.log("✅ CORS is working");
        })
        .catch(error => {
            console.log("❌ CORS issue detected");
            console.log("Solution: Configure server CORS headers");
        });
    
    // Check localStorage for API keys
    const apiKey = localStorage.getItem('brainAIKey');
    if (apiKey) {
        console.log("✅ API key found in localStorage");
    } else {
        console.log("❌ API key not found in localStorage");
        console.log("Solution: localStorage.setItem('brainAIKey', 'your-key')");
    }
}
```

### Java SDK Issues

```java
// Java-specific troubleshooting
import com.brainai.sdk.BrainAISDK;
import com.brainai.sdk.BrainAIConfig;
import java.util.concurrent.CompletableFuture;
import java.util.Map;

public class JavaSDKTroubleshooting {
    
    public static void main(String[] args) {
        troubleshootJavaSDK();
    }
    
    public static void troubleshootJavaSDK() {
        System.out.println("🔍 Troubleshooting Java SDK...");
        
        // Check Java version
        String javaVersion = System.getProperty("java.version");
        System.out.println("☕ Java version: " + javaVersion);
        
        // Check if Brain AI SDK is available
        try {
            BrainAIConfig config = BrainAIConfig.builder()
                .baseUrl("http://localhost:8000")
                .build();
            System.out.println("✅ Brain AI SDK classes available");
        } catch (NoClassDefFoundError e) {
            System.out.println("❌ Brain AI SDK not found in classpath");
            System.out.println("Solution: Add dependency to pom.xml or build.gradle");
        } catch (Exception e) {
            System.out.println("❌ SDK initialization error: " + e.getMessage());
        }
        
        // Test CompletableFuture handling
        System.out.println("🔄 Testing CompletableFuture...");
        testCompletableFuture();
    }
    
    private static void testCompletableFuture() {
        try {
            BrainAIConfig config = BrainAIConfig.builder()
                .baseUrl("http://localhost:8000")
                .build();
            BrainAISDK sdk = new BrainAISDK(config);
            
            // Test async operations
            CompletableFuture<Map<String, Object>> statusFuture = sdk.getStatus();
            
            statusFuture.thenAccept(status -> {
                System.out.println("✅ CompletableFuture working");
                System.out.println("Status: " + status.get("status"));
            }).exceptionally(throwable -> {
                System.out.println("❌ CompletableFuture error: " + throwable.getMessage());
                return null;
            });
            
            // Wait for completion (in real app, don't block)
            Thread.sleep(2000);
            
        } catch (Exception e) {
            System.out.println("❌ CompletableFuture test failed: " + e.getMessage());
        }
    }
    
    // Common Java error solutions
    public static void solveCommonJavaErrors() {
        System.out.println("🔧 Common Java SDK error solutions:");
        
        System.out.println("\n1. NoClassDefFoundError: BrainAISDK");
        System.out.println("   Solution: Add Maven dependency:");
        System.out.println("   <dependency>");
        System.out.println("     <groupId>com.brainai</groupId>");
        System.out.println("     <artifactId>brain-ai-sdk</artifactId>");
        System.out.println("     <version>1.0.0</version>");
        System.out.println("   </dependency>");
        
        System.out.println("\n2. TimeoutException in CompletableFuture");
        System.out.println("   Solution: Increase timeout or check server");
        System.out.println("   config.timeout(60000) // 60 seconds");
        
        System.out.println("\n3. IllegalStateException: No current event loop");
        System.out.println("   Solution: Use CompletableFuture correctly");
        System.out.println("   CompletableFuture.supplyAsync(() -> sdk.getStatus())");
        
        System.out.println("\n4. OutOfMemoryError");
        System.out.println("   Solution: Increase JVM heap size");
        System.out.println("   java -Xmx2g YourApplication");
    }
}
```

## 🐳 Environment-Specific Problems

### Docker Issues

```dockerfile
# Dockerfile troubleshooting
FROM python:3.11-slim

# Set environment variables
ENV BRAIN_AI_BASE_URL=http://localhost:8000
ENV BRAIN_AI_API_KEY=${BRAIN_AI_API_KEY}

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . /app
WORKDIR /app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

CMD ["python", "app.py"]
```

```bash
# Docker troubleshooting commands
#!/bin/bash

echo "🔍 Docker troubleshooting..."

# Check if container is running
if ! docker ps | grep -q brain-ai-app; then
    echo "❌ Container not running"
    echo "Start with: docker run brain-ai-app"
else
    echo "✅ Container is running"
fi

# Check container logs
echo "📋 Container logs:"
docker logs brain-ai-app

# Check network connectivity
echo "🌐 Testing network connectivity..."
docker exec brain-ai-app python -c "
import requests
try:
    response = requests.get('http://localhost:8000/api/health', timeout=5)
    print(f'✅ Network OK: {response.status_code}')
except Exception as e:
    print(f'❌ Network error: {e}')
"

# Check environment variables
echo "🔧 Environment variables:"
docker exec brain-ai-app env | grep BRAIN_AI

# Check resource usage
echo "📊 Resource usage:"
docker stats brain-ai-app --no-stream
```

### Kubernetes Issues

```yaml
# kubernetes-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: brain-ai-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: brain-ai-app
  template:
    metadata:
      labels:
        app: brain-ai-app
    spec:
      containers:
      - name: brain-ai-app
        image: brain-ai/app:latest
        ports:
        - containerPort: 8000
        env:
        - name: BRAIN_AI_BASE_URL
          value: "http://brain-ai-server:8000"
        - name: BRAIN_AI_API_KEY
          valueFrom:
            secretKeyRef:
              name: brain-ai-secrets
              key: api-key
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /api/health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /api/health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: brain-ai-app-service
spec:
  selector:
    app: brain-ai-app
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
```

## 🔍 Debugging Techniques

### Logging Configuration

```python
# Enhanced logging for debugging
import logging
import asyncio
from brain_ai import BrainAISDK, BrainAIConfig

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('brain_ai_debug.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('brain_ai')

class DebugBrainAISDK(BrainAISDK):
    """Enhanced SDK with debugging capabilities"""
    
    async def store_memory(self, content, memory_type, metadata=None):
        logger.debug(f"Storing memory: type={memory_type}, content={content}")
        try:
            result = await super().store_memory(content, memory_type, metadata)
            logger.debug(f"Memory stored successfully: {result}")
            return result
        except Exception as e:
            logger.error(f"Failed to store memory: {e}")
            raise
    
    async def search_memories(self, query, limit=10):
        logger.debug(f"Searching memories: query={query}, limit={limit}")
        try:
            results = await super().search_memories(query, limit)
            logger.debug(f"Search completed: {len(results)} results")
            return results
        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise
    
    async def reason(self, query, context=None):
        logger.debug(f"Reasoning: query={query}, context={context}")
        try:
            result = await super().reason(query, context)
            logger.debug(f"Reasoning completed: {result}")
            return result
        except Exception as e:
            logger.error(f"Reasoning failed: {e}")
            raise

# Usage with debugging
async def debug_brain_ai():
    config = BrainAIConfig("http://localhost:8000")
    sdk = DebugBrainAISDK(config)
    
    # Enable detailed logging
    logger.info("Starting Brain AI debugging session")
    
    try:
        # Test operations with logging
        memory_id = await sdk.store_memory(
            content={"test": "debugging"},
            type="semantic"
        )
        
        results = await sdk.search_memories("debugging", limit=5)
        
        reasoning = await sdk.reason("What is debugging?")
        
        logger.info("Debugging session completed successfully")
        
    except Exception as e:
        logger.error(f"Debugging session failed: {e}", exc_info=True)
```

### Performance Profiling

```python
# Performance profiling
import time
import cProfile
import pstats
import asyncio
from brain_ai import BrainAISDK, BrainAIConfig

class PerformanceProfiler:
    def __init__(self):
        self.profiler = cProfile.Profile()
        self.operations = []
    
    def start_profiling(self):
        self.profiler.enable()
    
    def stop_profiling(self):
        self.profiler.disable()
    
    def profile_operation(self, operation_name, operation_func):
        """Profile a specific operation"""
        print(f"🔍 Profiling {operation_name}...")
        
        start_time = time.time()
        self.start_profiling()
        
        try:
            result = operation_func()
            success = True
            error = None
        except Exception as e:
            result = None
            success = False
            error = str(e)
        finally:
            self.stop_profiling()
        
        end_time = time.time()
        duration = (end_time - start_time) * 1000
        
        operation_data = {
            'name': operation_name,
            'duration_ms': duration,
            'success': success,
            'error': error,
            'result_count': len(result) if isinstance(result, list) else 1
        }
        
        self.operations.append(operation_data)
        
        print(f"✅ {operation_name}: {duration:.2f}ms ({'success' if success else 'failed'})")
        
        return result
    
    def generate_report(self):
        """Generate performance report"""
        print("\n📊 Performance Report")
        print("=" * 50)
        
        total_time = sum(op['duration_ms'] for op in self.operations)
        
        for operation in self.operations:
            percentage = (operation['duration_ms'] / total_time) * 100
            status = "✅" if operation['success'] else "❌"
            
            print(f"{status} {operation['name']:<20} {operation['duration_ms']:>8.2f}ms ({percentage:>5.1f}%)")
            
            if operation['error']:
                print(f"    Error: {operation['error']}")
        
        print("=" * 50)
        print(f"Total time: {total_time:.2f}ms")
        
        # Generate detailed profile stats
        stats = pstats.Stats(self.profiler)
        stats.sort_stats('cumulative')
        
        print("\n🔍 Top 10 time-consuming functions:")
        stats.print_stats(10)
        
        return {
            'total_time': total_time,
            'operations': self.operations,
            'profile_stats': stats
        }

# Usage
async def profile_brain_ai():
    config = BrainAIConfig("http://localhost:8000")
    sdk = BrainAISDK(config)
    profiler = PerformanceProfiler()
    
    # Profile different operations
    def profile_store_memory():
        return asyncio.run(sdk.store_memory(
            content={"test": "performance profiling"},
            type="semantic"
        ))
    
    def profile_search():
        return asyncio.run(sdk.search_memories("test", limit=10))
    
    def profile_reason():
        return asyncio.run(sdk.reason("What is performance profiling?"))
    
    # Run profiles
    profiler.profile_operation("Store Memory", profile_store_memory)
    profiler.profile_operation("Search Memories", profile_search)
    profiler.profile_operation("Reasoning", profile_reason)
    
    # Generate report
    report = profiler.generate_report()
    
    return report
```

## 📊 Performance Monitoring

### Real-time Monitoring

```python
# Real-time performance monitoring
import asyncio
import time
from brain_ai import BrainAISDK, BrainAIConfig
from datetime import datetime

class PerformanceMonitor:
    def __init__(self, sdk):
        self.sdk = sdk
        self.metrics = []
        self.alerts = []
    
    async def monitor_performance(self, duration_seconds=300):
        """Monitor performance for specified duration"""
        print(f"🔍 Starting performance monitoring for {duration_seconds} seconds...")
        
        start_time = time.time()
        check_count = 0
        
        while (time.time() - start_time) < duration_seconds:
            check_count += 1
            
            # Collect metrics
            metrics = await self.collect_metrics()
            self.metrics.append(metrics)
            
            # Check for issues
            await self.check_alerts(metrics)
            
            # Print status
            self.print_status(metrics, check_count)
            
            await asyncio.sleep(10)  # Check every 10 seconds
        
        # Generate final report
        self.generate_report()
    
    async def collect_metrics(self):
        """Collect performance metrics"""
        try:
            # Get system status
            status = await self.sdk.get_status()
            
            # Get statistics
            stats = await self.sdk.get_statistics()
            
            # Test response time
            start = time.time()
            await self.sdk.get_status()
            response_time = (time.time() - start) * 1000
            
            metrics = {
                'timestamp': datetime.now(),
                'cpu_usage': status.get('cpu_usage', 0),
                'memory_usage': status.get('memory_usage', 0),
                'response_time_ms': response_time,
                'total_memories': stats.get('total_memories', 0),
                'learning_patterns': len(stats.get('patterns', [])),
                'active_connections': status.get('active_connections', 0)
            }
            
            return metrics
            
        except Exception as e:
            return {
                'timestamp': datetime.now(),
                'error': str(e),
                'response_time_ms': -1
            }
    
    async def check_alerts(self, metrics):
        """Check for performance alerts"""
        if 'error' in metrics:
            self.alerts.append({
                'timestamp': metrics['timestamp'],
                'type': 'error',
                'message': metrics['error']
            })
            return
        
        # CPU alert
        if metrics['cpu_usage'] > 0.8:
            self.alerts.append({
                'timestamp': metrics['timestamp'],
                'type': 'cpu',
                'message': f"High CPU usage: {metrics['cpu_usage']:.1%}"
            })
        
        # Memory alert
        if metrics['memory_usage'] > 0.8:
            self.alerts.append({
                'timestamp': metrics['timestamp'],
                'type': 'memory',
                'message': f"High memory usage: {metrics['memory_usage']:.1%}"
            })
        
        # Response time alert
        if metrics['response_time_ms'] > 1000:
            self.alerts.append({
                'timestamp': metrics['timestamp'],
                'type': 'response_time',
                'message': f"Slow response time: {metrics['response_time_ms']:.0f}ms"
            })
    
    def print_status(self, metrics, check_count):
        """Print current status"""
        if 'error' in metrics:
            print(f"Check {check_count}: ❌ Error - {metrics['error']}")
            return
        
        cpu = metrics['cpu_usage']
        memory = metrics['memory_usage']
        response_time = metrics['response_time_ms']
        
        status_icon = "🟢"
        if cpu > 0.8 or memory > 0.8 or response_time > 1000:
            status_icon = "🔴"
        elif cpu > 0.6 or memory > 0.6 or response_time > 500:
            status_icon = "🟡"
        
        print(f"{status_icon} Check {check_count}: CPU={cpu:.0%} Memory={memory:.0%} RT={response_time:.0f}ms")
    
    def generate_report(self):
        """Generate final performance report"""
        print("\n📊 Performance Monitoring Report")
        print("=" * 60)
        
        if not self.metrics:
            print("No metrics collected")
            return
        
        # Calculate averages
        valid_metrics = [m for m in self.metrics if 'error' not in m]
        
        if valid_metrics:
            avg_cpu = sum(m['cpu_usage'] for m in valid_metrics) / len(valid_metrics)
            avg_memory = sum(m['memory_usage'] for m in valid_metrics) / len(valid_metrics)
            avg_response_time = sum(m['response_time_ms'] for m in valid_metrics) / len(valid_metrics)
            
            print(f"Average CPU Usage: {avg_cpu:.1%}")
            print(f"Average Memory Usage: {avg_memory:.1%}")
            print(f"Average Response Time: {avg_response_time:.0f}ms")
        
        # Alert summary
        if self.alerts:
            print(f"\n⚠️ Alerts ({len(self.alerts)} total):")
            for alert in self.alerts[-5:]:  # Show last 5 alerts
                print(f"  {alert['timestamp'].strftime('%H:%M:%S')} - {alert['message']}")
        else:
            print("\n✅ No alerts triggered")
        
        # Recommendations
        self.generate_recommendations()
    
    def generate_recommendations(self):
        """Generate performance recommendations"""
        print("\n💡 Performance Recommendations:")
        
        if not self.metrics:
            return
        
        valid_metrics = [m for m in self.metrics if 'error' not in m]
        if not valid_metrics:
            return
        
        avg_cpu = sum(m['cpu_usage'] for m in valid_metrics) / len(valid_metrics)
        avg_memory = sum(m['memory_usage'] for m in valid_metrics) / len(valid_metrics)
        avg_response_time = sum(m['response_time_ms'] for m in valid_metrics) / len(valid_metrics)
        
        if avg_cpu > 0.7:
            print("  • Consider scaling up CPU resources")
            print("  • Optimize complex queries")
        
        if avg_memory > 0.7:
            print("  • Consider increasing memory allocation")
            print("  • Clean up old/unused memories")
        
        if avg_response_time > 500:
            print("  • Check network connectivity")
            print("  • Consider using caching")
            print("  • Optimize database queries")
        
        if avg_cpu < 0.3 and avg_memory < 0.3:
            print("  • Resources are well-utilized")
            print("  • Current configuration is optimal")

# Usage
async def run_performance_monitoring():
    config = BrainAIConfig("http://localhost:8000")
    sdk = BrainAISDK(config)
    
    monitor = PerformanceMonitor(sdk)
    await monitor.monitor_performance(duration_seconds=60)  # Monitor for 1 minute
```

## 🆘 Getting Help

### Support Channels

1. **Documentation**: Check the comprehensive documentation
2. **GitHub Issues**: Report bugs and request features
3. **Community Forum**: Get help from other developers
4. **Discord Server**: Real-time chat and support
5. **Email Support**: Direct support for enterprise users

### Issue Reporting Template

When reporting issues, please include:

```markdown
## Issue Description
Brief description of the problem

## Environment
- Brain AI Framework version: [e.g., 1.0.0]
- Programming language: [e.g., Python 3.11]
- Operating System: [e.g., Ubuntu 22.04]
- Server URL: [e.g., http://localhost:8000]

## Steps to Reproduce
1. Step one
2. Step two
3. Step three

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Error Messages
Full error message and stack trace

## Configuration
Relevant configuration settings

## Additional Context
Any other relevant information
```

### Debug Information Collection

```python
# Debug information collection script
import sys
import platform
import os
import asyncio
from brain_ai import BrainAISDK, BrainAIConfig

async def collect_debug_info():
    """Collect debug information for support"""
    print("🔍 Collecting debug information...")
    
    debug_info = {
        'system': {
            'platform': platform.platform(),
            'python_version': sys.version,
            'architecture': platform.architecture(),
            'processor': platform.processor()
        },
        'brain_ai': {},
        'configuration': {},
        'errors': []
    }
    
    # Test Brain AI connection
    try:
        config = BrainAIConfig("http://localhost:8000")
        sdk = BrainAISDK(config)
        
        # Get status
        status = await sdk.get_status()
        debug_info['brain_ai']['status'] = status
        
        # Get statistics
        stats = await sdk.get_statistics()
        debug_info['brain_ai']['statistics'] = stats
        
        # Test basic operations
        memory_id = await sdk.store_memory(
            content={"test": "debug info collection"},
            type="semantic"
        )
        debug_info['brain_ai']['memory_test'] = "success"
        
    except Exception as e:
        debug_info['errors'].append({
            'operation': 'brain_ai_connection',
            'error': str(e),
            'type': type(e).__name__
        })
    
    # Environment variables
    brain_ai_env_vars = [key for key in os.environ.keys() if 'BRAIN_AI' in key.upper()]
    debug_info['environment_variables'] = {
        var: os.getenv(var) for var in brain_ai_env_vars
    }
    
    # Print debug info
    print("\n📋 Debug Information:")
    print("=" * 50)
    
    for category, data in debug_info.items():
        if category == 'errors':
            continue
        
        print(f"\n{category.upper()}:")
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, str) and len(value) > 100:
                    value = value[:100] + "..."
                print(f"  {key}: {value}")
        else:
            print(f"  {data}")
    
    if debug_info['errors']:
        print("\n❌ ERRORS:")
        for error in debug_info['errors']:
            print(f"  {error['operation']}: {error['error']}")
    
    return debug_info

# Save debug info to file
def save_debug_info(debug_info):
    import json
    from datetime import datetime
    
    filename = f"brain_ai_debug_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(filename, 'w') as f:
        json.dump(debug_info, f, indent=2, default=str)
    
    print(f"💾 Debug information saved to: {filename}")

# Usage
async def main():
    debug_info = await collect_debug_info()
    save_debug_info(debug_info)

if __name__ == "__main__":
    asyncio.run(main())
```

---

*This troubleshooting guide covers the most common issues you might encounter with Brain AI. If you don't find your issue here, please reach out to our support team with the debug information from the script above.*