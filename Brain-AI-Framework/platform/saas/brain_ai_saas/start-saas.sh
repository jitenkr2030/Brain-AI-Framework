#!/bin/bash

# Brain AI SaaS Platform Startup Script
# This script starts the complete SaaS platform with all services

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "\n${BLUE}=================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}=================================${NC}\n"
}

# Check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    print_status "Docker and Docker Compose are installed"
}

# Check if .env file exists
check_env_file() {
    if [ ! -f ".env" ]; then
        print_warning ".env file not found. Creating from template..."
        cp .env.example .env
        print_warning "Please update the .env file with your actual configuration"
        print_warning "Press Enter to continue with default configuration..."
        read -p ""
    else
        print_status ".env file found"
    fi
}

# Create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    mkdir -p backend/logs
    mkdir -p frontend/build
    mkdir -p deployment/nginx/ssl
    mkdir -p monitoring/prometheus
    mkdir -p monitoring/grafana/{provisioning,dashboards}
    mkdir -p data/{postgres,redis,prometheus,grafana}
    print_status "Directories created"
}

# Setup monitoring configuration
setup_monitoring() {
    print_status "Setting up monitoring configuration..."
    
    # Create Prometheus configuration
    cat > monitoring/prometheus/prometheus.yml << 'EOF'
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "alert_rules.yml"

scrape_configs:
  - job_name: 'brain-ai-backend'
    static_configs:
      - targets: ['backend:8000']
    metrics_path: '/metrics'
    scrape_interval: 10s

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres-exporter:9187']

  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093
EOF

    # Create Grafana datasource configuration
    mkdir -p monitoring/grafana/provisioning/datasources
    cat > monitoring/grafana/provisioning/datasources/prometheus.yml << 'EOF'
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
EOF

    # Create Grafana dashboard provider configuration
    mkdir -p monitoring/grafana/provisioning/dashboards
    cat > monitoring/grafana/provisioning/dashboards/dashboard.yml << 'EOF'
apiVersion: 1

providers:
  - name: 'Brain AI Dashboards'
    orgId: 1
    folder: ''
    type: file
    disableDeletion: false
    updateIntervalSeconds: 10
    allowUiUpdates: true
    options:
      path: /var/lib/grafana/dashboards
EOF

    print_status "Monitoring configuration created"
}

# Setup Nginx configuration
setup_nginx() {
    print_status "Setting up Nginx configuration..."
    
    cat > deployment/nginx/nginx.conf << 'EOF'
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server backend:8000;
    }
    
    upstream frontend {
        server frontend:3000;
    }
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=100r/m;
    limit_req_zone $binary_remote_addr zone=login:10m rate=5r/m;
    
    server {
        listen 80;
        server_name localhost;
        
        # Security headers
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";
        
        # Frontend
        location / {
            proxy_pass http://frontend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
        
        # API endpoints
        location /api/ {
            limit_req zone=api burst=10 nodelay;
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
        
        # Authentication endpoints with stricter rate limiting
        location /api/v1/auth/ {
            limit_req zone=login burst=3 nodelay;
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
        
        # Health check
        location /health {
            proxy_pass http://backend;
            access_log off;
        }
    }
}
EOF

    print_status "Nginx configuration created"
}

# Build and start services
start_services() {
    print_header "Starting Brain AI SaaS Platform"
    
    # Build images
    print_status "Building Docker images..."
    docker-compose build --no-cache
    
    # Start services
    print_status "Starting services..."
    docker-compose up -d
    
    # Wait for services to be healthy
    print_status "Waiting for services to start..."
    sleep 10
    
    # Check service health
    print_status "Checking service health..."
    docker-compose ps
}

# Display service information
show_service_info() {
    print_header "Brain AI SaaS Platform is Running!"
    
    echo -e "${GREEN}Services:${NC}"
    echo -e "  🏠  Frontend Dashboard:     ${BLUE}http://localhost:3000${NC}"
    echo -e "  🔧  Backend API:           ${BLUE}http://localhost:8000${NC}"
    echo -e "  📊  API Documentation:     ${BLUE}http://localhost:8000/docs${NC}"
    echo -e "  🗄️  Database Admin:        ${BLUE}http://localhost:8080${NC} (Adminer)"
    echo -e "  📈  Monitoring:            ${BLUE}http://localhost:3001${NC} (Grafana)"
    echo -e "  📊  Prometheus:            ${BLUE}http://localhost:9090${NC}"
    echo -e "  📧  Email Testing:         ${BLUE}http://localhost:8025${NC} (MailHog)"
    
    echo -e "\n${GREEN}Default Credentials:${NC}"
    echo -e "  Database:     postgres / brain_ai_password_2025"
    echo -e "  Redis:        (password required)"
    echo -e "  Grafana:      admin / brain_ai_grafana_2025"
    echo -e "  Adminer:      postgres / brain_ai_password_2025"
    
    echo -e "\n${GREEN}Useful Commands:${NC}"
    echo -e "  View logs:           ${BLUE}docker-compose logs -f${NC}"
    echo -e "  Stop services:       ${BLUE}docker-compose down${NC}"
    echo -e "  Restart services:    ${BLUE}docker-compose restart${NC}"
    echo -e "  Reset database:      ${BLUE}docker-compose down -v && docker-compose up -d${NC}"
    
    echo -e "\n${GREEN}API Testing:${NC}"
    echo -e "  Health check:        ${BLUE}curl http://localhost:8000/health${NC}"
    echo -e "  API docs:           ${BLUE}open http://localhost:8000/docs${NC}"
    
    echo -e "\n${YELLOW}Next Steps:${NC}"
    echo -e "  1. Open http://localhost:3000 to access the dashboard"
    echo -e "  2. Create a tenant and admin user"
    echo -e "  3. Start creating projects and memories"
    echo -e "  4. Monitor performance at http://localhost:3001"
    
    print_status "Brain AI SaaS Platform is ready! 🚀"
}

# Main execution
main() {
    print_header "Brain AI SaaS Platform Startup"
    
    # Change to script directory
    cd "$(dirname "$0")"
    
    # Run setup steps
    check_docker
    check_env_file
    create_directories
    setup_monitoring
    setup_nginx
    start_services
    
    # Show service information
    show_service_info
}

# Handle script arguments
case "${1:-}" in
    "stop")
        print_status "Stopping Brain AI SaaS Platform..."
        docker-compose down
        print_status "Brain AI SaaS Platform stopped"
        ;;
    "restart")
        print_status "Restarting Brain AI SaaS Platform..."
        docker-compose restart
        print_status "Brain AI SaaS Platform restarted"
        ;;
    "logs")
        docker-compose logs -f "${2:-}"
        ;;
    "reset")
        print_warning "This will delete all data! Are you sure? (y/N)"
        read -r response
        if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
            print_status "Resetting Brain AI SaaS Platform..."
            docker-compose down -v
            docker-compose up -d
            print_status "Brain AI SaaS Platform reset complete"
        else
            print_status "Reset cancelled"
        fi
        ;;
    "status")
        docker-compose ps
        ;;
    *)
        main
        ;;
esac
