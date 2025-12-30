interface CacheEntry<T> {
  data: T
  timestamp: number
}

interface CacheOptions {
  ttl?: number // Time to live in milliseconds (default: 5 minutes)
}

export const useCache = <T = any>(key: string, options: CacheOptions = {}) => {
  const ttl = options.ttl || 5 * 60 * 1000 // Default 5 minutes

  // Use a Map for better performance than reactive objects
  const cache = useState<Map<string, CacheEntry<T>>>(
    `cache_${key}`,
    () => new Map()
  )

  const get = (cacheKey: string): T | null => {
    const entry = cache.value.get(cacheKey)
    
    if (!entry) {
      return null
    }

    // Check if entry is expired
    if (Date.now() - entry.timestamp > ttl) {
      cache.value.delete(cacheKey)
      return null
    }

    return entry.data
  }

  const set = (cacheKey: string, data: T): void => {
    cache.value.set(cacheKey, {
      data,
      timestamp: Date.now()
    })
  }

  const has = (cacheKey: string): boolean => {
    const entry = cache.value.get(cacheKey)
    
    if (!entry) {
      return false
    }

    // Check if entry is expired
    if (Date.now() - entry.timestamp > ttl) {
      cache.value.delete(cacheKey)
      return false
    }

    return true
  }

  const invalidate = (cacheKey?: string): void => {
    if (cacheKey) {
      cache.value.delete(cacheKey)
    } else {
      cache.value.clear()
    }
  }

  const invalidatePattern = (pattern: string): void => {
    const keysToDelete: string[] = []
    
    cache.value.forEach((_, key) => {
      if (key.includes(pattern)) {
        keysToDelete.push(key)
      }
    })

    keysToDelete.forEach(key => cache.value.delete(key))
  }

  return {
    get,
    set,
    has,
    invalidate,
    invalidatePattern
  }
}

