import os
import redis

redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')

try:
    redis_client = redis.from_url(redis_url, decode_responses=True)
    redis_client.ping()
except Exception:
    redis_client = None

def blacklist_token(token: str, expires_in_seconds: int = 86400):
    """Guarda el token en la lista negra con un tiempo de vida (TTL)"""
    if redis_client:
        try:
            redis_client.setex(f"token_blacklist:{token}", expires_in_seconds, "revoked")
        except Exception:
            pass

def is_token_blacklisted(token: str) -> bool:
    """Verifica si el token ha sido revocado"""
    if redis_client:
        try:
            return redis_client.exists(f"token_blacklist:{token}") == 1
        except Exception:
            return False
    return False
