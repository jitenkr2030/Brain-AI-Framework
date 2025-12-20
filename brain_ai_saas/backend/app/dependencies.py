"""
Brain AI SaaS Dependencies
Authentication, authorization, rate limiting, and other middleware
"""

from typing import Optional, Dict, Any, Callable
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
import redis
import time
import logging
import json

from app.config import settings
from app.database import db
from app.models.user import User, UserSession
from app.models.tenant import Tenant

logger = logging.getLogger(__name__)
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Redis connection for caching and rate limiting
redis_client = None


def get_redis_client() -> redis.Redis:
    """Get Redis client"""
    global redis_client
    if redis_client is None:
        redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
    return redis_client


async def setup_metrics():
    """Setup Prometheus metrics"""
    try:
        from prometheus_client import Counter, Histogram, Gauge, start_http_server
        
        # Define metrics
        global http_requests_total, http_request_duration, active_users, memory_operations
        http_requests_total = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
        http_request_duration = Histogram('http_request_duration_seconds', 'HTTP request duration')
        active_users = Gauge('active_users', 'Number of active users')
        memory_operations = Counter('memory_operations_total', 'Memory operations', ['operation'])
        
        # Start metrics server
        start_http_server(8001)
        logger.info("📊 Prometheus metrics server started on port 8001")
        
    except ImportError:
        logger.warning("⚠️ Prometheus client not available, metrics disabled")
    except Exception as e:
        logger.error(f"❌ Failed to setup metrics: {e}")


# Global metrics (if prometheus client not available)
http_requests_total = None
http_request_duration = None
active_users = None
memory_operations = None


class Metrics:
    """Metrics helper class"""
    
    @staticmethod
    def increment_counter(name: str, labels: Dict[str, str] = None):
        """Increment a counter metric"""
        if http_requests_total and name == 'http_requests_total':
            http_requests_total.labels(**labels).inc()
    
    @staticmethod
    def observe_duration(duration: float):
        """Observe a duration metric"""
        if http_request_duration:
            http_request_duration.observe(duration)
    
    @staticmethod
    def set_gauge(name: str, value: float):
        """Set a gauge metric"""
        if active_users and name == 'active_users':
            active_users.set(value)


metrics = Metrics()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify and decode a JWT token"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """Get current authenticated user"""
    token = credentials.credentials
    payload = verify_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id: str = payload.get("sub")
    tenant_id: str = payload.get("tenant_id")
    
    if not user_id or not tenant_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user from database
    user = await db.fetchrow(
        "SELECT * FROM users WHERE id = $1 AND tenant_id = $2 AND is_active = true",
        user_id,
        tenant_id
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return User(**dict(user))


async def get_current_tenant(current_user: User = Depends(get_current_user)) -> Dict[str, Any]:
    """Get current tenant information"""
    tenant = await db.fetchrow(
        "SELECT * FROM tenants WHERE id = $1 AND status = 'active'",
        current_user.tenant_id
    )
    
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tenant not found or inactive"
        )
    
    return dict(tenant)


async def get_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """Require admin role"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


async def rate_limit_middleware(request: Request, call_next: Callable):
    """Rate limiting middleware"""
    start_time = time.time()
    
    # Skip rate limiting for health checks
    if request.url.path in ["/health", "/health/detailed", "/metrics"]:
        response = await call_next(request)
        return response
    
    # Get client IP
    client_ip = request.client.host
    
    # Check rate limit
    redis_client = get_redis_client()
    rate_limit_key = f"rate_limit:{client_ip}"
    
    current_requests = redis_client.get(rate_limit_key)
    if current_requests is None:
        redis_client.setex(rate_limit_key, 60, 1)
    else:
        requests_count = int(current_requests)
        if requests_count >= settings.RATE_LIMIT_PER_MINUTE:
            # Log rate limit hit
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            return Response(
                content=json.dumps({"detail": "Rate limit exceeded"}),
                status_code=429,
                media_type="application/json",
                headers={"Retry-After": "60"}
            )
        redis_client.incr(rate_limit_key)
    
    # Process request
    response = await call_next(request)
    
    # Record metrics
    duration = time.time() - start_time
    metrics.observe_duration(duration)
    
    labels = {
        'method': request.method,
        'endpoint': request.url.path,
        'status': str(response.status_code)
    }
    metrics.increment_counter('http_requests_total', labels)
    
    return response


class RateLimiter:
    """Rate limiter using Redis"""
    
    def __init__(self, key: str, limit: int, window: int = 60):
        self.key = f"rate_limit:{key}"
        self.limit = limit
        self.window = window
        self.redis = get_redis_client()
    
    async def is_allowed(self) -> bool:
        """Check if request is allowed"""
        current = self.redis.get(self.key)
        if current is None:
            self.redis.setex(self.key, self.window, 1)
            return True
        
        count = int(current)
        if count >= self.limit:
            return False
        
        self.redis.incr(self.key)
        return True
    
    async def reset(self):
        """Reset rate limit"""
        self.redis.delete(self.key)


async def check_tenant_limits(tenant_id: str) -> Dict[str, Any]:
    """Check tenant usage against plan limits"""
    # Get tenant and plan info
    tenant = await db.fetchrow(
        "SELECT t.*, s.plan FROM tenants t LEFT JOIN subscriptions s ON t.id = s.tenant_id WHERE t.id = $1",
        tenant_id
    )
    
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    
    plan = tenant.get('plan', 'free')
    
    # Get current usage
    usage_stats = await db.fetchrow("""
        SELECT 
            COUNT(DISTINCT p.id) as project_count,
            COUNT(m.id) as memory_count,
            COUNT(au.id) as api_call_count
        FROM tenants t
        LEFT JOIN projects p ON t.id = p.tenant_id
        LEFT JOIN memories m ON p.id = m.project_id
        LEFT JOIN api_usage au ON t.id = au.tenant_id 
            AND au.created_at >= DATE_TRUNC('month', NOW())
        WHERE t.id = $1
        GROUP BY t.id
    """, tenant_id)
    
    # Get plan limits
    from app.models.subscription import PLANS
    plan_limits = PLANS.get(plan)
    
    if not plan_limits:
        raise HTTPException(status_code=400, detail="Invalid plan")
    
    # Check limits
    limits_check = {
        "project_count": {
            "used": usage_stats['project_count'] if usage_stats else 0,
            "limit": plan_limits.max_projects if plan_limits.max_projects != -1 else None,
            "exceeded": False
        },
        "memory_count": {
            "used": usage_stats['memory_count'] if usage_stats else 0,
            "limit": plan_limits.max_memories if plan_limits.max_memories != -1 else None,
            "exceeded": False
        },
        "api_call_count": {
            "used": usage_stats['api_call_count'] if usage_stats else 0,
            "limit": plan_limits.max_api_calls_per_month if plan_limits.max_api_calls_per_month != -1 else None,
            "exceeded": False
        }
    }
    
    # Check if any limits are exceeded
    for limit_type, limit_info in limits_check.items():
        if limit_info["limit"] is not None and limit_info["used"] >= limit_info["limit"]:
            limit_info["exceeded"] = True
    
    return {
        "plan": plan,
        "limits": limits_check,
        "plan_limits": plan_limits
    }


class TenantContext:
    """Tenant context manager"""
    
    def __init__(self, tenant_data: Dict[str, Any]):
        self.tenant = tenant_data
    
    def check_limit(self, resource_type: str) -> bool:
        """Check if resource usage is within limits"""
        # This would be implemented based on the check_tenant_limits logic
        return True
    
    def get_usage_percentage(self, resource_type: str) -> float:
        """Get usage percentage for a resource type"""
        # This would be implemented based on actual usage tracking
        return 0.0


# Cache decorators
def cache_result(ttl: int = 300):
    """Cache decorator for expensive operations"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"cache:{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            redis_client = get_redis_client()
            
            # Try to get from cache
            cached_result = redis_client.get(cache_key)
            if cached_result:
                return json.loads(cached_result)
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Cache result
            redis_client.setex(cache_key, ttl, json.dumps(result, default=str))
            
            return result
        return wrapper
    return decorator


# Metrics helper
class Timer:
    """Timer context manager for metrics"""
    
    def __init__(self, metric_name: str):
        self.metric_name = metric_name
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        metrics.observe_duration(duration)
        if memory_operations:
            memory_operations.labels(operation=self.metric_name).inc()


# Export common dependencies
get_current_tenant_dependency = Depends(get_current_tenant)
get_current_user_dependency = Depends(get_current_user)
get_admin_user_dependency = Depends(get_admin_user)
