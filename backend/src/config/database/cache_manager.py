
"""Simple pluggable cache manager.

Provides a small async-compatible in-memory cache backend with TTL and
an easy-to-replace backend interface so the implementation can be swapped
for Redis or another distributed cache later.

Usage:
	from .config.database.cache_manager import cache_manager
	await cache_manager.connect()
	await cache_manager.set("key", "value", ttl=60)
	v = await cache_manager.get("key")
	await cache_manager.disconnect()
"""

from __future__ import annotations

import asyncio
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Tuple


class CacheBackend(ABC):
	@abstractmethod
	async def connect(self) -> None:
		raise NotImplementedError

	@abstractmethod
	async def disconnect(self) -> None:
		raise NotImplementedError

	@abstractmethod
	async def get(self, key: str) -> dict:
		raise NotImplementedError

	@abstractmethod
	async def set(self, key: str, value: dict, ttl: Optional[float] = None) -> None:
		raise NotImplementedError

	@abstractmethod
	async def delete(self, key: str) -> None:
		raise NotImplementedError

	@abstractmethod
	async def clear(self) -> None:
		raise NotImplementedError


class InMemoryCacheBackend(CacheBackend):
	def __init__(self, cleanup_interval: float = 5.0) -> None:
		self._store: Dict[str, Tuple[Any, Optional[float]]] = {}
		self._lock = asyncio.Lock()
		self._cleanup_interval = cleanup_interval
		self._cleanup_task: Optional[asyncio.Task[None]] = None
		self._closing = False

	async def connect(self) -> None:
		self._closing = False
		if self._cleanup_task is None:
			loop = asyncio.get_running_loop()
			self._cleanup_task = loop.create_task(self._cleanup_loop())

	async def disconnect(self) -> None:
		self._closing = True
		task = self._cleanup_task
		self._cleanup_task = None
		if task:
			task.cancel()
			with contextlib.suppress(asyncio.CancelledError):
				await task

	async def get(self, key: str) -> dict:
		async with self._lock:
			entry = self._store.get(key)
			if not entry:
				return {}
			value, expire_at = entry
			if expire_at is not None and expire_at <= time.time():
				# expired
				del self._store[key]
				return {}
			return value

	async def set(self, key: str, value: dict, ttl: Optional[float] = None) -> None:
		expire_at = None
		if ttl is not None:
			expire_at = time.time() + float(ttl)
		async with self._lock:
			self._store[key] = (value, expire_at)

	async def delete(self, key: str) -> None:
		async with self._lock:
			self._store.pop(key, None)

	async def clear(self) -> None:
		async with self._lock:
			self._store.clear()

	async def _cleanup_loop(self) -> None:
		try:
			while not self._closing:
				now = time.time()
				async with self._lock:
					expired = [k for k, (_, exp) in self._store.items() if exp is not None and exp <= now]
					for k in expired:
						self._store.pop(k, None)
				await asyncio.sleep(self._cleanup_interval)
		except asyncio.CancelledError:
			return


import contextlib


class CacheManager:
	"""Facade around an underlying CacheBackend.

	The facade exposes a consistent async API so the app code doesn't have
	to change when swapping backend implementations (e.g. Redis).
	"""

	def __init__(self, backend: CacheBackend) -> None:
		self._backend = backend

	async def connect(self) -> None:
		await self._backend.connect()

	async def disconnect(self) -> None:
		await self._backend.disconnect()

	async def get(self, key: str) -> dict:
		return await self._backend.get(key)

	async def set(self, key: str, value: dict, ttl: Optional[float] = None) -> None:
		await self._backend.set(key, value, ttl=ttl)

	async def delete(self, key: str) -> None:
		await self._backend.delete(key)

	async def clear(self) -> None:
		await self._backend.clear()


# Default process-local cache instance. Swap the backend later to use Redis.
cache_manager = CacheManager(InMemoryCacheBackend())

__all__ = ["CacheBackend", "InMemoryCacheBackend", "CacheManager", "cache_manager"]
