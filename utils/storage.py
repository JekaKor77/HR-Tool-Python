import json
from app_config import settings
import time
import redis


class EvaluationStore:
    def __init__(self, ttl_seconds: int = 24 * 3600):
        self.ttl = ttl_seconds
        self._use_redis = False
        try:
            r = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0, decode_responses=True)
            r.ping()
            self.r = r
            self._use_redis = True
        except redis.exceptions.ConnectionError:
            self._mem = {}

    def set(self, key: str, value: dict):
        payload = json.dumps(value)
        if self._use_redis:
            self.r.setex(key, self.ttl, payload)
        else:
            expire_at = time.time() + self.ttl
            self._mem[key] = (expire_at, payload)

    def get(self, key: str):
        if self._use_redis:
            raw = self.r.get(key)
            return json.loads(raw) if raw else None
        else:
            item = self._mem.get(key)
            if not item:
                return None
            expire_at, payload = item
            if time.time() > expire_at:
                del self._mem[key]
                return None
            return json.loads(payload)

    def delete(self, key: str):
        if self._use_redis:
            self.r.delete(key)
        else:
            self._mem.pop(key, None)
