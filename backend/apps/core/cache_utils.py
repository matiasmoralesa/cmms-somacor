"""
Cache utilities for CMMS system
"""
from django.core.cache import cache
from django.conf import settings
from functools import wraps
import hashlib
import json
from typing import Any, Callable, Optional


def generate_cache_key(prefix: str, *args, **kwargs) -> str:
    """
    Generate a unique cache key based on prefix and arguments
    
    Args:
        prefix: Cache key prefix
        *args: Positional arguments to include in key
        **kwargs: Keyword arguments to include in key
    
    Returns:
        Unique cache key string
    """
    # Crear string con todos los argumentos
    key_parts = [prefix]
    
    if args:
        key_parts.extend([str(arg) for arg in args])
    
    if kwargs:
        # Ordenar kwargs para consistencia
        sorted_kwargs = sorted(kwargs.items())
        key_parts.append(json.dumps(sorted_kwargs, sort_keys=True))
    
    # Generar hash si la key es muy larga
    key_string = ':'.join(key_parts)
    if len(key_string) > 200:
        key_hash = hashlib.md5(key_string.encode()).hexdigest()
        return f"{prefix}:{key_hash}"
    
    return key_string


def cache_result(timeout: int = 300, key_prefix: str = 'default'):
    """
    Decorator to cache function results
    
    Args:
        timeout: Cache timeout in seconds (default: 5 minutes)
        key_prefix: Prefix for cache key
    
    Example:
        @cache_result(timeout=600, key_prefix='asset_list')
        def get_assets(status=None):
            return Asset.objects.filter(status=status)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generar cache key
            cache_key = generate_cache_key(
                f"{key_prefix}:{func.__name__}",
                *args,
                **kwargs
            )
            
            # Intentar obtener del cache
            result = cache.get(cache_key)
            if result is not None:
                return result
            
            # Ejecutar función y cachear resultado
            result = func(*args, **kwargs)
            cache.set(cache_key, result, timeout)
            
            return result
        
        return wrapper
    return decorator


def invalidate_cache(key_prefix: str, *args, **kwargs):
    """
    Invalidate cache for specific key
    
    Args:
        key_prefix: Cache key prefix to invalidate
        *args: Additional arguments for key generation
        **kwargs: Additional keyword arguments for key generation
    """
    cache_key = generate_cache_key(key_prefix, *args, **kwargs)
    cache.delete(cache_key)


def invalidate_cache_pattern(pattern: str):
    """
    Invalidate all cache keys matching a pattern
    
    Args:
        pattern: Pattern to match (e.g., 'asset:*')
    
    Note: This requires Redis backend
    """
    try:
        from django_redis import get_redis_connection
        redis_conn = get_redis_connection("default")
        
        # Obtener todas las keys que coinciden con el patrón
        keys = redis_conn.keys(f"*{pattern}*")
        if keys:
            redis_conn.delete(*keys)
    except Exception as e:
        # Si no es Redis o hay error, intentar con cache.clear()
        print(f"Error invalidating cache pattern: {e}")


class CacheManager:
    """
    Manager class for cache operations
    """
    
    # Cache timeouts (in seconds)
    TIMEOUT_SHORT = 60  # 1 minute
    TIMEOUT_MEDIUM = 300  # 5 minutes
    TIMEOUT_LONG = 900  # 15 minutes
    TIMEOUT_HOUR = 3600  # 1 hour
    TIMEOUT_DAY = 86400  # 24 hours
    
    @staticmethod
    def get_or_set(key: str, callback: Callable, timeout: int = TIMEOUT_MEDIUM) -> Any:
        """
        Get value from cache or set it using callback
        
        Args:
            key: Cache key
            callback: Function to call if cache miss
            timeout: Cache timeout in seconds
        
        Returns:
            Cached or computed value
        """
        result = cache.get(key)
        if result is None:
            result = callback()
            cache.set(key, result, timeout)
        return result
    
    @staticmethod
    def set(key: str, value: Any, timeout: int = TIMEOUT_MEDIUM):
        """Set cache value"""
        cache.set(key, value, timeout)
    
    @staticmethod
    def get(key: str, default: Any = None) -> Any:
        """Get cache value"""
        return cache.get(key, default)
    
    @staticmethod
    def delete(key: str):
        """Delete cache key"""
        cache.delete(key)
    
    @staticmethod
    def delete_many(keys: list):
        """Delete multiple cache keys"""
        cache.delete_many(keys)
    
    @staticmethod
    def clear():
        """Clear all cache"""
        cache.clear()
    
    # Specific cache keys for CMMS
    @staticmethod
    def get_asset_cache_key(asset_id: str) -> str:
        """Get cache key for asset"""
        return f"asset:{asset_id}"
    
    @staticmethod
    def get_work_order_cache_key(wo_id: str) -> str:
        """Get cache key for work order"""
        return f"work_order:{wo_id}"
    
    @staticmethod
    def get_user_cache_key(user_id: str) -> str:
        """Get cache key for user"""
        return f"user:{user_id}"
    
    @staticmethod
    def get_stats_cache_key(stat_type: str) -> str:
        """Get cache key for statistics"""
        return f"stats:{stat_type}"
    
    @staticmethod
    def invalidate_asset_cache(asset_id: str):
        """Invalidate cache for specific asset"""
        cache.delete(CacheManager.get_asset_cache_key(asset_id))
        # También invalidar listas relacionadas
        invalidate_cache_pattern("asset_list")
    
    @staticmethod
    def invalidate_work_order_cache(wo_id: str):
        """Invalidate cache for specific work order"""
        cache.delete(CacheManager.get_work_order_cache_key(wo_id))
        invalidate_cache_pattern("work_order_list")
    
    @staticmethod
    def invalidate_stats_cache():
        """Invalidate all statistics cache"""
        invalidate_cache_pattern("stats:")


# Singleton instance
cache_manager = CacheManager()
