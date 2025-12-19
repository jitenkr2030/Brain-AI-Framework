# Installation Guide

Complete installation instructions for Brain AI Framework across all supported programming languages and platforms.

## 📋 Table of Contents

- [System Requirements](#system-requirements)
- [Server Setup](#server-setup)
- [Python SDK](#python-sdk)
- [JavaScript/TypeScript SDK](#javascripttypescript-sdk)
- [Java SDK](#java-sdk)
- [Go SDK](#go-sdk)
- [Rust SDK](#rust-sdk)
- [Ruby SDK](#ruby-sdk)
- [PHP SDK](#php-sdk)
- [C# SDK](#c-sdk)
- [Docker Installation](#docker-installation)
- [Cloud Deployment](#cloud-deployment)
- [Troubleshooting](#troubleshooting)

## 🔧 System Requirements

### Minimum Requirements
- **RAM**: 2GB available memory
- **Storage**: 1GB free disk space
- **Network**: Internet connection for API access
- **Python**: 3.8+ (for Python SDK)
- **Node.js**: 14+ (for JavaScript SDK)
- **Java**: JDK 8+ (for Java SDK)

### Recommended Requirements
- **RAM**: 8GB+ for optimal performance
- **Storage**: 10GB+ for large datasets
- **CPU**: Multi-core processor for concurrent operations

## 🖥️ Server Setup

Before installing any SDK, you need a Brain AI server running.

### Option 1: Local Development Server

#### Using Docker (Recommended)
```bash
# Pull and run Brain AI server
docker pull brainai/server:latest
docker run -p 8000:8000 brainai/server:latest

# Or with custom configuration
docker run -p 8000:8000 \
  -e BRAIN_AI_API_KEY=your-api-key \
  -e BRAIN_AI_MEMORY_SIZE=10000 \
  brainai/server:latest
```

#### Using Python Package
```bash
# Install Brain AI server
pip install brain-ai-server

# Start the server
brain-ai-server --host 0.0.0.0 --port 8000 --api-key your-api-key
```

#### Manual Setup
```bash
# Clone the repository
git clone https://github.com/brain-ai/framework.git
cd framework

# Install dependencies
pip install -r requirements.txt

# Start the server
python -m brain_ai.app.main
```

### Option 2: Cloud Server
```bash
# Get API key from https://brain-ai.com
export BRAIN_AI_API_KEY="your-api-key-here"
export BRAIN_AI_BASE_URL="https://api.brain-ai.com"
```

## 🐍 Python SDK

### Installation

#### Standard Installation
```bash
pip install brain-ai-sdk
```

#### Development Installation
```bash
git clone https://github.com/brain-ai/python-sdk.git
cd python-sdk
pip install -e .
```

#### With Extras
```bash
# Install with async support
pip install brain-ai-sdk[async]

# Install with ML integrations
pip install brain-ai-sdk[ml]

# Install all extras
pip install brain-ai-sdk[async,ml,dev]
```

### Configuration
```python
# Basic configuration
from brain_ai import BrainAISDK, BrainAIConfig

config = BrainAIConfig(
    base_url="http://localhost:8000",
    api_key="your-api-key-here"
)

sdk = BrainAISDK(config)
```

### Environment Variables
```bash
# Set environment variables
export BRAIN_AI_BASE_URL="http://localhost:8000"
export BRAIN_AI_API_KEY="your-api-key"
export BRAIN_AI_TIMEOUT="30000"
```

### Verification
```python
import asyncio
from brain_ai import BrainAISDK

async def test_installation():
    sdk = BrainAISDK()  # Uses environment variables
    
    # Test connection
    status = await sdk.get_status()
    print(f"✅ Brain AI is running: {status['status']}")
    
    # Test memory storage
    memory_id = await sdk.store_memory(
        content="Test memory",
        type="semantic"
    )
    print(f"✅ Memory storage works: {memory_id}")

asyncio.run(test_installation())
```

## 🌐 JavaScript/TypeScript SDK

### Installation

#### NPM Installation
```bash
# Standard installation
npm install brain-ai-sdk

# Or with yarn
yarn add brain-ai-sdk

# TypeScript types included
npm install @types/brain-ai-sdk
```

#### Development Installation
```bash
git clone https://github.com/brain-ai/javascript-sdk.git
cd javascript-sdk
npm install
npm run build
npm link  # Link for local development
```

#### CDN Installation
```html
<!-- For browser usage -->
<script src="https://cdn.brain-ai.com/sdk/brain-ai.min.js"></script>
<script>
    const sdk = new BrainAISDK({
        baseUrl: 'http://localhost:8000'
    });
</script>
```

### Configuration
```typescript
// TypeScript configuration
import { BrainAISDK, BrainAIConfig } from 'brain-ai-sdk';

const config = new BrainAIConfig({
    baseUrl: 'http://localhost:8000',
    apiKey: 'your-api-key-here',
    timeout: 30000,
    memorySize: 10000
});

const sdk = new BrainAISDK(config);
```

### Environment Setup
```bash
# .env file
BRAIN_AI_BASE_URL=http://localhost:8000
BRAIN_AI_API_KEY=your-api-key-here
BRAIN_AI_TIMEOUT=30000
```

### Verification
```javascript
// Test installation
import { BrainAISDK } from 'brain-ai-sdk';

async function testInstallation() {
    const sdk = new BrainAISDK(); // Uses env vars
    
    // Test connection
    const status = await sdk.getStatus();
    console.log(`✅ Brain AI is running: ${status.status}`);
    
    // Test memory storage
    const memoryId = await sdk.storeMemory(
        { text: "Test memory" },
        'semantic'
    );
    console.log(`✅ Memory storage works: ${memoryId}`);
}

testInstallation().catch(console.error);
```

## ☕ Java SDK

### Installation

#### Maven
```xml
<!-- pom.xml -->
<dependency>
    <groupId>com.brainai</groupId>
    <artifactId>brain-ai-sdk</artifactId>
    <version>1.0.0</version>
</dependency>
```

#### Gradle
```gradle
// build.gradle
dependencies {
    implementation 'com.brainai:brain-ai-sdk:1.0.0'
}
```

#### Manual Download
```bash
# Download JAR from releases
wget https://github.com/brain-ai/java-sdk/releases/download/v1.0.0/brain-ai-sdk-1.0.0.jar

# Add to your classpath
java -cp ".:brain-ai-sdk-1.0.0.jar" YourMainClass
```

### Configuration
```java
import com.brainai.sdk.BrainAISDK;
import com.brainai.sdk.BrainAIConfig;

public class Example {
    public static void main(String[] args) {
        BrainAIConfig config = BrainAIConfig.builder()
            .baseUrl("http://localhost:8000")
            .apiKey("your-api-key-here")
            .timeout(30000)
            .memorySize(10000)
            .build();
            
        BrainAISDK sdk = new BrainAISDK(config);
    }
}
```

### Environment Configuration
```bash
# application.properties
brain.ai.base.url=http://localhost:8000
brain.ai.api.key=your-api-key-here
brain.ai.timeout=30000
```

### Verification
```java
import java.util.concurrent.CompletableFuture;

public class TestInstallation {
    public static void main(String[] args) {
        BrainAISDK sdk = new BrainAISDK(BrainAIConfig.builder().build());
        
        CompletableFuture<Void> test = sdk.getStatus()
            .thenAccept(status -> {
                System.out.println("✅ Brain AI is running: " + status.get("status"));
            })
            .thenCompose(result -> {
                Map<String, Object> content = Map.of("text", "Test memory");
                return sdk.storeMemory(content, MemoryType.SEMANTIC, null);
            })
            .thenAccept(memoryId -> {
                System.out.println("✅ Memory storage works: " + memoryId);
            });
            
        test.join();
    }
}
```

## 🔷 Go SDK

### Installation

#### Go Modules
```bash
go mod init your-project
go get github.com/brain-ai/go-sdk
```

#### Traditional Installation
```bash
# Ensure Go modules are enabled
export GO111MODULE=on

go get github.com/brain-ai/go-sdk
```

### Configuration
```go
package main

import (
    "context"
    "fmt"
    
    "github.com/brain-ai/go-sdk"
)

func main() {
    config := brainai.BrainAIConfig{
        BaseURL: "http://localhost:8000",
        APIKey:  "your-api-key-here",
        Timeout: 30000,
    }
    
    sdk := brainai.NewBrainAISDK(config)
}
```

### Environment Variables
```bash
# .env file or shell
export BRAIN_AI_BASE_URL="http://localhost:8000"
export BRAIN_AI_API_KEY="your-api-key-here"
export BRAIN_AI_TIMEOUT="30000"
```

### Verification
```go
func testInstallation() error {
    sdk := brainai.NewBrainAISDK(brainai.BrainAIConfig{})
    
    // Test connection
    status, err := sdk.GetStatus()
    if err != nil {
        return err
    }
    fmt.Printf("✅ Brain AI is running: %v\n", status["status"])
    
    // Test memory storage
    memoryID, err := sdk.StoreMemory(
        map[string]interface{}{
            "text": "Test memory",
        },
        brainai.SemanticMemory,
        nil,
    )
    if err != nil {
        return err
    }
    fmt.Printf("✅ Memory storage works: %s\n", memoryID)
    
    return nil
}
```

## 🦀 Rust SDK

### Installation

#### Cargo
```toml
# Cargo.toml
[dependencies]
brain-ai-sdk = "1.0.0"
tokio = { version = "1.0", features = ["full"] }
serde_json = "1.0"
```

#### Development Version
```toml
[dependencies]
brain-ai-sdk = { git = "https://github.com/brain-ai/rust-sdk.git" }
```

### Configuration
```rust
use brain_ai::{BrainAISDK, BrainAIConfig};

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let config = BrainAIConfig::new("http://localhost:8000")
        .with_api_key("your-api-key-here")
        .with_timeout(30)
        .with_memory_size(10000);
    
    let sdk = BrainAISDK::new(config);
}
```

### Environment Configuration
```bash
# .env file
BRAIN_AI_BASE_URL=http://localhost:8000
BRAIN_AI_API_KEY=your-api-key-here
BRAIN_AI_TIMEOUT=30
```

### Verification
```rust
#[tokio::main]
async fn test_installation() -> Result<(), Box<dyn std::error::Error>> {
    let sdk = BrainAISDK::new(BrainAIConfig::default());
    
    // Test connection
    let status = sdk.get_status().await?;
    println!("✅ Brain AI is running: {}", status["status"]);
    
    // Test memory storage
    let memory_id = sdk.store_memory(
        serde_json::json!({"text": "Test memory"}),
        MemoryType::Semantic,
        None,
    ).await?;
    
    println!("✅ Memory storage works: {}", memory_id);
    
    Ok(())
}
```

## 💎 Ruby SDK

### Installation

#### RubyGems
```bash
# Standard installation
gem install brain-ai-sdk

# Or add to Gemfile
echo "gem 'brain-ai-sdk'" >> Gemfile
bundle install
```

#### Development Installation
```bash
git clone https://github.com/brain-ai/ruby-sdk.git
cd ruby-sdk
gem build brain_ai_sdk.gemspec
gem install brain_ai_sdk-1.0.0.gem
```

### Configuration
```ruby
require 'brain_ai'

config = BrainAI::BrainAIConfig.new('http://localhost:8000')
  .with_api_key('your-api-key-here')
  .with_timeout(30_000)

sdk = BrainAI::BrainAISDK.new(config)
```

### Environment Variables
```bash
# .env file
BRAIN_AI_BASE_URL=http://localhost:8000
BRAIN_AI_API_KEY=your-api-key-here
BRAIN_AI_TIMEOUT=30000
```

### Verification
```ruby
def test_installation
  sdk = BrainAI::BrainAISDK.new(BrainAI::BrainAIConfig.new)
  
  # Test connection
  status = sdk.get_status
  puts "✅ Brain AI is running: #{status['status']}"
  
  # Test memory storage
  memory_id = sdk.store_memory(
    { text: 'Test memory' },
    BrainAI::MemoryType::SEMANTIC
  )
  puts "✅ Memory storage works: #{memory_id}"
rescue => e
  puts "❌ Error: #{e.message}"
end

test_installation
```

## 🐘 PHP SDK

### Installation

#### Composer
```bash
# Standard installation
composer require brain-ai/sdk

# Or add to composer.json
{
    "require": {
        "brain-ai/sdk": "^1.0"
    }
}
composer install
```

#### Manual Installation
```bash
# Download SDK
wget https://github.com/brain-ai/php-sdk/releases/download/v1.0.0/brain-ai-sdk.zip
unzip brain-ai-sdk.zip
```

### Configuration
```php
<?php
require 'vendor/autoload.php';

use BrainAI\BrainAIConfig;
use BrainAI\BrainAISDK;

$config = new BrainAIConfig('http://localhost:8000');
$config->withApiKey('your-api-key-here');

$sdk = new BrainAISDK($config);
?>
```

### Environment Configuration
```bash
# .env file
BRAIN_AI_BASE_URL=http://localhost:8000
BRAIN_AI_API_KEY=your-api-key-here
BRAIN_AI_TIMEOUT=30000
```

### Verification
```php
<?php
function test_installation() {
    $sdk = new BrainAISDK(new BrainAIConfig());
    
    try {
        // Test connection
        $status = $sdk->getStatus();
        echo "✅ Brain AI is running: " . $status['status'] . "\n";
        
        // Test memory storage
        $memoryId = $sdk->storeMemory(
            ['text' => 'Test memory'],
            'semantic'
        );
        echo "✅ Memory storage works: " . $memoryId . "\n";
    } catch (Exception $e) {
        echo "❌ Error: " . $e->getMessage() . "\n";
    }
}

test_installation();
?>
```

## 🏷️ C# SDK

### Installation

#### NuGet Package Manager
```bash
# Package Manager Console
Install-Package BrainAI.SDK

# Or via dotnet CLI
dotnet add package BrainAI.SDK
```

#### Manual Reference
```xml
<!-- Add to your .csproj file -->
<PackageReference Include="BrainAI.SDK" Version="1.0.0" />
```

### Configuration
```csharp
using BrainAI;

var config = new BrainAIConfig("http://localhost:8000")
    .WithApiKey("your-api-key-here")
    .WithTimeout(30000)
    .WithMemorySize(10000);

var sdk = new BrainAISDK(config);
```

### Environment Configuration
```json
// appsettings.json
{
    "BrainAI": {
        "BaseUrl": "http://localhost:8000",
        "ApiKey": "your-api-key-here",
        "Timeout": 30000
    }
}
```

### Verification
```csharp
using System;
using System.Threading.Tasks;

class Program
{
    static async Task Main(string[] args)
    {
        var sdk = new BrainAISDK(new BrainAIConfig());
        
        try
        {
            // Test connection
            var status = await sdk.GetStatusAsync();
            Console.WriteLine($"✅ Brain AI is running: {status["status"]}");
            
            // Test memory storage
            var memoryId = await sdk.StoreMemoryAsync(
                new { Text = "Test memory" },
                MemoryType.Semantic
            );
            Console.WriteLine($"✅ Memory storage works: {memoryId}");
        }
        catch (Exception e)
        {
            Console.WriteLine($"❌ Error: {e.Message}");
        }
    }
}
```

## 🐳 Docker Installation

### Development Container
```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "-m", "brain_ai.app.main"]
```

```bash
# Build and run
docker build -t brain-ai-dev .
docker run -p 8000:8000 brain-ai-dev
```

### Production Container
```yaml
# docker-compose.yml
version: '3.8'
services:
  brain-ai:
    image: brainai/server:latest
    ports:
      - "8000:8000"
    environment:
      - BRAIN_AI_API_KEY=${BRAIN_AI_API_KEY}
      - BRAIN_AI_MEMORY_SIZE=100000
    volumes:
      - brain_ai_data:/app/data
    restart: unless-stopped

volumes:
  brain_ai_data:
```

```bash
# Run production setup
docker-compose up -d
```

### Multi-Language Development Environment
```yaml
# docker-compose.dev.yml
version: '3.8'
services:
  brain-ai-server:
    image: brainai/server:latest
    ports:
      - "8000:8000"
    environment:
      - BRAIN_AI_API_KEY=dev-key
    volumes:
      - ./sdk:/workspace/sdk

  python-dev:
    image: python:3.11
    working_dir: /workspace
    volumes:
      - ./sdk/python:/workspace
    command: python -m pytest

  node-dev:
    image: node:18
    working_dir: /workspace
    volumes:
      - ./sdk/javascript:/workspace
    command: npm test
```

## ☁️ Cloud Deployment

### AWS Deployment
```yaml
# aws-deployment.yaml
AWSTemplateFormatVersion: '2010-09-09'
Resources:
  BrainAIServer:
    Type: AWS::ECS::Service
    Properties:
      Cluster: !Ref ECSCluster
      TaskDefinition: !Ref TaskDefinition
      DesiredCount: 2
```

### Google Cloud Platform
```bash
# Deploy to GCP
gcloud run deploy brain-ai-server \
  --image brainai/server:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### Azure Deployment
```bash
# Deploy to Azure
az container create \
  --resource-group brain-ai-rg \
  --name brain-ai-server \
  --image brainai/server:latest \
  --ports 8000 \
  --environment-variables \
    BRAIN_AI_API_KEY=your-api-key
```

## 🔧 Troubleshooting

### Common Installation Issues

#### Python Issues
```bash
# Permission errors
pip install --user brain-ai-sdk

# Version conflicts
pip install --upgrade pip
pip install --force-reinstall brain-ai-sdk

# Virtual environment issues
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
pip install brain-ai-sdk
```

#### Node.js Issues
```bash
# Permission errors
sudo npm install -g brain-ai-sdk

# Version conflicts
npm install -g npm@latest
npm install brain-ai-sdk --force

# Yarn issues
yarn config set registry https://registry.npmjs.org/
yarn add brain-ai-sdk
```

#### Java Issues
```xml
<!-- Maven repository issues -->
<repositories>
    <repository>
        <id>brainai-releases</id>
        <url>https://maven.brain-ai.com/releases</url>
    </repository>
</repositories>
```

#### Go Issues
```bash
# Module issues
go mod tidy
go mod download

# Proxy issues
export GOPROXY=https://goproxy.io,direct
go get github.com/brain-ai/go-sdk
```

### Network Issues
```python
# Test network connectivity
import requests

try:
    response = requests.get("http://localhost:8000/api/health")
    print(f"✅ Server is reachable: {response.status_code}")
except requests.exceptions.ConnectionError:
    print("❌ Cannot connect to Brain AI server")
    print("Make sure the server is running on http://localhost:8000")
```

### Performance Issues
```python
# Check system resources
import psutil

def check_system_health():
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    print(f"CPU Usage: {cpu_percent}%")
    print(f"Memory Usage: {memory.percent}%")
    print(f"Disk Usage: {disk.percent}%")
    
    if cpu_percent > 80:
        print("⚠️ High CPU usage detected")
    if memory.percent > 80:
        print("⚠️ High memory usage detected")

check_system_health()
```

## 📊 Verification Checklist

- [ ] Brain AI server is running and accessible
- [ ] SDK is installed correctly for your language
- [ ] API key is configured (if required)
- [ ] Connection test passes
- [ ] Memory storage test passes
- [ ] Search functionality works
- [ ] No error messages in logs

## 🆘 Getting Help

If you encounter issues during installation:

1. **Check the [Troubleshooting Guide](troubleshooting.md)**
2. **Visit our [GitHub Issues](https://github.com/brain-ai/framework/issues)**
3. **Join our [Discord Community](https://discord.gg/brain-ai)**
4. **Email support: support@brain-ai.com**

---

*Installation complete! Ready to build amazing AI applications? 🚀*