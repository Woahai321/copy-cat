export const useItemsCache = () => {
    interface CacheEntry {
        data: any
        timestamp: number
        isStale: boolean
    }

    // Singleton cache state (persists across component mounts within session)
    const cache = useState<Map<string, CacheEntry>>('items-cache', () => new Map())
    const CACHE_TTL = 5 * 60 * 1000      // 5 minutes fresh

    // Key generator
    const getCacheKey = (page: number, limit: number, filters: string = '') => {
        return `items_p${page}_l${limit}_${filters}`
    }

    const clearCache = () => {
        cache.value.clear()
    }

    const getCached = (page: number, limit: number, filters: string = '') => {
        const key = getCacheKey(page, limit, filters)
        const entry = cache.value.get(key)

        if (!entry) return null

        const age = Date.now() - entry.timestamp
        entry.isStale = age > CACHE_TTL

        return entry
    }

    const setCache = (page: number, limit: number, filters: string, data: any) => {
        const key = getCacheKey(page, limit, filters)
        cache.value.set(key, {
            data,
            timestamp: Date.now(),
            isStale: false
        })
    }

    return {
        getCached,
        setCache,
        clearCache
    }
}
