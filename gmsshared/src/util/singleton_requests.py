"""
Singleton wrapper around the requests library with rate limiting capabilities.
"""

import threading
import time
from typing import Any, Dict, Optional, Union, ClassVar
import requests
from requests.adapters import HTTPAdapter
from requests.models import Response
from requests.sessions import Session


class RateLimiter:
    """Token bucket rate limiter implementation."""
    
    def __init__(self, max_requests: int = 100, time_window: float = 60.0):
        """
        Initialize rate limiter.
        
        Args:
            max_requests: Maximum number of requests allowed in the time window
            time_window: Time window in seconds for the rate limit
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.tokens = max_requests
        self.last_update = time.time()
        self._lock = threading.Lock()
    
    def acquire(self) -> bool:
        """
        Acquire a token for making a request.
        
        Returns:
            True if token acquired, False if rate limited
        """
        with self._lock:
            now = time.time()
            # Add tokens based on elapsed time
            elapsed = now - self.last_update
            self.tokens = min(
                self.max_requests,
                self.tokens + (elapsed * self.max_requests / self.time_window)
            )
            self.last_update = now
            
            if self.tokens >= 1:
                self.tokens -= 1
                return True
            return False
    
    def wait_for_token(self) -> None:
        """Wait until a token is available."""
        while not self.acquire():
            time.sleep(0.1)


class NamedSingletonMeta(type):
    """Metaclass for thread-safe named singleton implementation.
    
    Creates one singleton instance per name, allowing multiple named instances
    of the same class with different configurations.
    """
    
    _instances: ClassVar[Dict[str, Any]] = {}
    _lock: ClassVar[threading.Lock] = threading.Lock()
    
    def __call__(cls, name: str = 'default', *args, **kwargs):
        """Create or return existing named instance.
        
        Args:
            name: Name of the instance (default: 'default')
            *args, **kwargs: Arguments for instance creation
            
        Returns:
            Named singleton instance
        """
        instance_key = f"{cls.__name__}_{name}"
        
        if instance_key not in cls._instances:
            with cls._lock:
                if instance_key not in cls._instances:
                    instance = super().__call__(*args, **kwargs)
                    instance._instance_name = name
                    cls._instances[instance_key] = instance
        
        return cls._instances[instance_key]


class SingletonRequests(metaclass=NamedSingletonMeta):
    """
    Named singleton wrapper around requests library with rate limiting.
    
    This class provides the exact same interface as the requests library
    while adding rate limiting capabilities. Multiple named instances can
    be created, each with their own rate limiting configuration.
    """
    
    def __init__(self, 
                 max_requests: int = 100,
                 time_window: float = 60.0,
                 wait_on_rate_limit: bool = True):
        """
        Initialize the named singleton requests wrapper.
        
        Note: The 'name' parameter is handled by the metaclass and not passed here.
        
        Args:
            max_requests: Maximum requests per time window
            time_window: Time window in seconds
            wait_on_rate_limit: If True, wait when rate limited; if False, raise exception
        """
        if hasattr(self, '_initialized'):
            return
            
        self._rate_limiter = RateLimiter(max_requests, time_window)
        self._wait_on_rate_limit = wait_on_rate_limit
        self._session = requests.Session()
        self._lock = threading.Lock()
        self._instance_name = getattr(self, '_instance_name', 'default')
        self._initialized = True
    
    def _check_rate_limit(self) -> None:
        """Check rate limit before making request."""
        if self._wait_on_rate_limit:
            self._rate_limiter.wait_for_token()
        elif not self._rate_limiter.acquire():
            raise requests.exceptions.HTTPError("Rate limit exceeded")
    
    def configure_rate_limit(self, max_requests: int, time_window: float) -> None:
        """
        Reconfigure rate limiting parameters.
        
        Args:
            max_requests: Maximum requests per time window
            time_window: Time window in seconds
        """
        with self._lock:
            self._rate_limiter = RateLimiter(max_requests, time_window)
    
    def set_wait_on_rate_limit(self, wait: bool) -> None:
        """
        Set whether to wait or raise exception when rate limited.
        
        Args:
            wait: If True, wait when rate limited; if False, raise exception
        """
        self._wait_on_rate_limit = wait
    
    # Core HTTP methods
    def get(self, url: str, params=None, **kwargs) -> Response:
        """Send a GET request."""
        self._check_rate_limit()
        return self._session.get(url, params=params, **kwargs)
    
    def post(self, url: str, data=None, json=None, **kwargs) -> Response:
        """Send a POST request."""
        self._check_rate_limit()
        return self._session.post(url, data=data, json=json, **kwargs)
    
    def put(self, url: str, data=None, **kwargs) -> Response:
        """Send a PUT request."""
        self._check_rate_limit()
        return self._session.put(url, data=data, **kwargs)
    
    def patch(self, url: str, data=None, **kwargs) -> Response:
        """Send a PATCH request."""
        self._check_rate_limit()
        return self._session.patch(url, data=data, **kwargs)
    
    def delete(self, url: str, **kwargs) -> Response:
        """Send a DELETE request."""
        self._check_rate_limit()
        return self._session.delete(url, **kwargs)
    
    def head(self, url: str, **kwargs) -> Response:
        """Send a HEAD request."""
        self._check_rate_limit()
        return self._session.head(url, **kwargs)
    
    def options(self, url: str, **kwargs) -> Response:
        """Send an OPTIONS request."""
        self._check_rate_limit()
        return self._session.options(url, **kwargs)
    
    def request(self, method: str, url: str, **kwargs) -> Response:
        """Send a request with the specified method."""
        self._check_rate_limit()
        return self._session.request(method, url, **kwargs)
    
    # Session management methods
    def close(self) -> None:
        """Close the underlying session."""
        self._session.close()
    
    def mount(self, prefix: str, adapter: HTTPAdapter) -> None:
        """Mount an adapter to the session."""
        self._session.mount(prefix, adapter)
    
    def prepare_request(self, request):
        """Prepare a request."""
        return self._session.prepare_request(request)
    
    # Property access for session attributes
    @property
    def headers(self):
        """Get session headers."""
        return self._session.headers
    
    @headers.setter
    def headers(self, value):
        """Set session headers."""
        self._session.headers = value
    
    @property
    def cookies(self):
        """Get session cookies."""
        return self._session.cookies
    
    @cookies.setter
    def cookies(self, value):
        """Set session cookies."""
        self._session.cookies = value
    
    @property
    def auth(self):
        """Get session auth."""
        return self._session.auth
    
    @auth.setter
    def auth(self, value):
        """Set session auth."""
        self._session.auth = value
    
    @property
    def proxies(self):
        """Get session proxies."""
        return self._session.proxies
    
    @proxies.setter
    def proxies(self, value):
        """Set session proxies."""
        self._session.proxies = value
    
    @property
    def stream(self):
        """Get session stream setting."""
        return self._session.stream
    
    @stream.setter
    def stream(self, value):
        """Set session stream setting."""
        self._session.stream = value
    
    @property
    def verify(self):
        """Get session verify setting."""
        return self._session.verify
    
    @verify.setter
    def verify(self, value):
        """Set session verify setting."""
        self._session.verify = value
    
    @property
    def cert(self):
        """Get session cert setting."""
        return self._session.cert
    
    @cert.setter
    def cert(self, value):
        """Set session cert setting."""
        self._session.cert = value
    
    @property
    def max_redirects(self):
        """Get session max_redirects setting."""
        return self._session.max_redirects
    
    @max_redirects.setter
    def max_redirects(self, value):
        """Set session max_redirects setting."""
        self._session.max_redirects = value
    
    @property
    def trust_env(self):
        """Get session trust_env setting."""
        return self._session.trust_env
    
    @trust_env.setter
    def trust_env(self, value):
        """Set session trust_env setting."""
        self._session.trust_env = value
    
    # Context manager support
    def __enter__(self):
        """Enter context manager."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager."""
        self.close()
    
    # Rate limiting status methods
    def get_rate_limit_status(self) -> Dict[str, Any]:
        """
        Get current rate limiting status.
        
        Returns:
            Dictionary with rate limiting information
        """
        with self._rate_limiter._lock:
            return {
                'instance_name': self._instance_name,
                'max_requests': self._rate_limiter.max_requests,
                'time_window': self._rate_limiter.time_window,
                'tokens_available': self._rate_limiter.tokens,
                'wait_on_rate_limit': self._wait_on_rate_limit
            }
    
    @property
    def instance_name(self) -> str:
        """Get the name of this singleton instance."""
        return self._instance_name
    
    @classmethod
    def get_instance(cls, name: str = 'default') -> 'SingletonRequests':
        """
        Get an existing named instance without creating a new one.
        
        Args:
            name: Name of the instance
            
        Returns:
            Named singleton instance if it exists
            
        Raises:
            KeyError: If named instance doesn't exist
        """
        instance_key = f"{cls.__name__}_{name}"
        if instance_key not in cls._instances:
            raise KeyError(f"No instance named '{name}' exists. Create it first with SingletonRequests('{name}')")
        return cls._instances[instance_key]
    
    @classmethod
    def list_instances(cls) -> Dict[str, 'SingletonRequests']:
        """
        List all existing named instances.
        
        Returns:
            Dictionary mapping instance names to instances
        """
        result = {}
        prefix = f"{cls.__name__}_"
        
        for key, instance in cls._instances.items():
            if key.startswith(prefix):
                name = key[len(prefix):]
                result[name] = instance
        
        return result
    
    @classmethod
    def remove_instance(cls, name: str) -> bool:
        """
        Remove a named instance (for cleanup/testing).
        
        Args:
            name: Name of the instance to remove
            
        Returns:
            True if instance was removed, False if it didn't exist
        """
        instance_key = f"{cls.__name__}_{name}"
        
        with cls._lock:
            if instance_key in cls._instances:
                instance = cls._instances[instance_key]
                # Close the session before removing
                try:
                    instance.close()
                except Exception:
                    pass  # Ignore errors during cleanup
                
                del cls._instances[instance_key]
                return True
            return False
    
    @classmethod
    def clear_all_instances(cls) -> int:
        """
        Remove all instances (for cleanup/testing).
        
        Returns:
            Number of instances that were removed
        """
        prefix = f"{cls.__name__}_"
        count = 0
        
        with cls._lock:
            keys_to_remove = [key for key in cls._instances.keys() if key.startswith(prefix)]
            
            for key in keys_to_remove:
                instance = cls._instances[key]
                # Close the session before removing
                try:
                    instance.close()
                except Exception:
                    pass  # Ignore errors during cleanup
                
                del cls._instances[key]
                count += 1
        
        return count


# Create a global instance that can be imported and used like the requests module
# This maintains backward compatibility
requests_singleton = SingletonRequests('default')

# Export the main HTTP methods at module level for drop-in replacement
get = requests_singleton.get
post = requests_singleton.post
put = requests_singleton.put
patch = requests_singleton.patch
delete = requests_singleton.delete
head = requests_singleton.head
options = requests_singleton.options
request = requests_singleton.request

# Convenience functions for creating named instances
def get_client(name: str, **kwargs) -> SingletonRequests:
    """
    Get or create a named singleton requests client.
    
    Args:
        name: Name of the client instance
        **kwargs: Configuration arguments for the client (only used on first creation)
        
    Returns:
        Named singleton requests client
    """
    return SingletonRequests(name, **kwargs)

def list_clients() -> Dict[str, SingletonRequests]:
    """
    List all existing named singleton clients.
    
    Returns:
        Dictionary mapping client names to instances
    """
    return SingletonRequests.list_instances()

def remove_client(name: str) -> bool:
    """
    Remove a named client instance.
    
    Args:
        name: Name of the client to remove
        
    Returns:
        True if client was removed, False if it didn't exist
    """
    return SingletonRequests.remove_instance(name)

def clear_all_clients() -> int:
    """
    Remove all client instances.
    
    Returns:
        Number of clients that were removed
    """
    return SingletonRequests.clear_all_instances()

# Export common requests objects and exceptions for compatibility
Session = requests.Session
HTTPError = requests.exceptions.HTTPError
ConnectionError = requests.exceptions.ConnectionError
Timeout = requests.exceptions.Timeout
RequestException = requests.exceptions.RequestException
