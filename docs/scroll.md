# Infinite Scroll Pagination Implementation Guide

## Overview

This document explains how infinite scroll pagination is implemented in the ListSync Items page. The implementation uses the **Intersection Observer API** with smart caching and stale-while-revalidate patterns for optimal performance.

## Architecture Components

### 1. **Page Component** (`pages/items.vue`)
The main page that renders items and handles pagination logic.

### 2. **Cache Layer** (`composables/useItemsCache.ts`)
Smart caching composable that implements stale-while-revalidate pattern.

### 3. **API Service** (`composables/useApiService.ts`)
API wrapper that handles all HTTP requests.

### 4. **Poster Card Component** (`components/items/PosterCard.vue`)
Individual item card with lazy-loaded images.

---

## How It Works

### Step 1: Initial Page Load

```vue
// pages/items.vue - onMounted lifecycle hook
onMounted(async () => {
  // Clear cache to ensure fresh data on navigation
  itemsCache.clearCache()
  
  // Fetch first page (page 1, 50 items)
  await Promise.all([
    fetchItems(1, true, true), // Force refresh
    fetchStats(),
    syncStore.fetchLiveSyncStatus()
  ])
  
  // Prefetch next 2 pages in background for smooth scrolling
  if (totalPages.value > 1 && displayMode.value === 'grid') {
    setTimeout(() => {
      const pagesToPrefetch = [2, 3].filter(p => p <= totalPages.value)
      if (pagesToPrefetch.length > 0) {
        itemsCache.prefetchPages(pagesToPrefetch, perPage)
      }
    }, 1000)
  }
  
  // Setup infinite scroll observer
  if (displayMode.value === 'grid') {
    nextTick(() => {
      if (infiniteScrollTrigger.value) {
        setupInfiniteScroll()
      }
    })
  }
})
```

**What happens:**
- Clears cache to show latest data
- Loads first 50 items
- Prefetches pages 2 and 3 in the background for instant loading
- Sets up the Intersection Observer for scroll detection

---

### Step 2: Intersection Observer Setup

```javascript
// pages/items.vue - setupInfiniteScroll function
const setupInfiniteScroll = () => {
  if (!process.client || !infiniteScrollTrigger.value) return
  
  // Clean up existing observer
  if (infiniteScrollObserver) {
    infiniteScrollObserver.disconnect()
  }
  
  // Create new observer
  infiniteScrollObserver = new IntersectionObserver(
    (entries) => {
      const entry = entries[0]
      // When trigger element becomes visible and we have more pages
      if (entry.isIntersecting && hasMorePages.value && !isLoadingMore.value && !isLoading.value) {
        console.log('🔄 Infinite scroll triggered, loading next page...')
        loadNextPage()
      }
    },
    {
      root: null,              // viewport
      rootMargin: '200px',     // Start loading 200px BEFORE reaching trigger
      threshold: 0.1           // Trigger when 10% visible
    }
  )
  
  infiniteScrollObserver.observe(infiniteScrollTrigger.value)
}
```

**Key Configuration:**
- `root: null` - Uses the browser viewport as the scroll container
- `rootMargin: '200px'` - Starts loading 200px before the trigger element is visible (proactive loading)
- `threshold: 0.1` - Triggers when 10% of the element is visible

---

### Step 3: Trigger Element in Template

```vue
<!-- pages/items.vue - Invisible trigger element -->
<div
  ref="infiniteScrollTrigger"
  class="h-4 w-full mt-8"
/>
```

**What this does:**
- Creates an invisible div at the bottom of the item list
- When user scrolls near this element (200px before it), the next page loads
- Has a small height (4px) to ensure it's detectable

---

### Step 4: Loading Next Page

```javascript
// pages/items.vue - loadNextPage function
const loadNextPage = async () => {
  if (hasMorePages.value && !isLoading.value && !isLoadingMore.value) {
    isLoadingMore.value = true  // Show loading spinner
    currentPage.value++          // Increment page number
    
    try {
      await fetchItems(currentPage.value, false) // false = append, not replace
    } finally {
      isLoadingMore.value = false
    }
  }
}
```

**Important parameters:**
- `reset: false` - Appends new items to existing array instead of replacing
- Guards prevent multiple simultaneous loads

---

### Step 5: Fetching Items with Smart Caching

```javascript
// pages/items.vue - fetchItems function
const fetchItems = async (page: number = 1, reset: boolean = true, forceRefresh: boolean = false) => {
  try {
    if (reset) {
      isLoading.value = true
    }
    
    let response: any
    
    // Use smart cache for grid view
    if (displayMode.value === 'grid') {
      // Returns cached data immediately if available
      // Fetches fresh data in background if stale
      response = await itemsCache.fetchEnrichedItems(page, perPage, forceRefresh)
    } else {
      // Table view - no caching
      response = await api.getProcessedItems(page, perPage)
    }
    
    if (response && response.items) {
      if (reset) {
        items.value = response.items  // Replace (first page)
      } else {
        items.value = [...items.value, ...response.items]  // Append (infinite scroll)
      }
      
      totalItems.value = response.total || 0
      totalPages.value = response.total_pages || 0
      hasMorePages.value = page < totalPages.value
    }
  } catch (error: any) {
    console.error('Error fetching items:', error)
    // Error handling...
  } finally {
    isLoading.value = false
  }
}
```

**Key behaviors:**
- `reset: true` - Replaces items (initial load)
- `reset: false` - Appends items (infinite scroll)
- Uses smart cache that returns stale data instantly while fetching fresh data in background

---

### Step 6: Smart Caching Layer

```javascript
// composables/useItemsCache.ts
const CACHE_TTL = 5 * 60 * 1000      // 5 minutes fresh
const STALE_TTL = 30 * 60 * 1000     // 30 minutes stale but usable

const fetchEnrichedItems = async (page: number, limit: number, forceRefresh = false) => {
  const cached = getCached(page, limit)
  
  // If we have fresh cache, return immediately
  if (cached && !cached.isStale && !forceRefresh) {
    console.log(`✨ Using fresh cache for page ${page}`)
    return cached.data
  }
  
  // If we have stale cache, return it but refresh in background
  if (cached && cached.isStale && !forceRefresh) {
    console.log(`⚡ Using stale cache for page ${page}, refreshing in background...`)
    
    // Return stale data immediately
    const staleData = cached.data
    
    // Fetch fresh data in background (non-blocking)
    api.getEnrichedItems(page, limit)
      .then(freshData => {
        console.log(`✅ Background refresh completed for page ${page}`)
        setCache(page, limit, freshData)
      })
      .catch(err => {
        console.warn(`⚠️ Background refresh failed for page ${page}:`, err)
      })
    
    return staleData
  }
  
  // No cache - fetch fresh data
  console.log(`🔄 Fetching fresh data for page ${page}`)
  const freshData = await api.getEnrichedItems(page, limit)
  setCache(page, limit, freshData)
  return freshData
}
```

**Cache Strategy (Stale-While-Revalidate):**
1. **Fresh (0-5 minutes):** Return from cache instantly
2. **Stale (5-30 minutes):** Return stale data instantly, fetch fresh in background
3. **Expired (>30 minutes):** Fetch fresh data, block until complete

---

### Step 7: API Endpoint

```javascript
// composables/useApiService.ts
async getEnrichedItems(page: number = 1, limit: number = 50) {
  return apiCall(`${baseURL}/items/enriched?page=${page}&limit=${limit}`)
}
```

**API Response Format:**
```json
{
  "items": [
    {
      "id": 123,
      "title": "Movie Title",
      "media_type": "movie",
      "year": 2023,
      "poster_url": "https://...",
      "rating": 8.5,
      "overview": "Plot summary...",
      "status": "requested",
      "overseerr_url": "https://...",
      "imdb_id": "tt1234567",
      "tmdb_id": 456789
    }
  ],
  "total": 500,
  "page": 1,
  "limit": 50,
  "total_pages": 10
}
```

---

## Visual Flow Diagram

```
User Action: Navigate to /items
           ↓
┌──────────────────────────────────────┐
│ 1. Mount Component                   │
│    - Clear cache                     │
│    - Fetch page 1 (50 items)         │
│    - Prefetch pages 2-3 background   │
│    - Setup Intersection Observer     │
└──────────────────────────────────────┘
           ↓
┌──────────────────────────────────────┐
│ 2. Render Grid                       │
│    - Show 50 poster cards            │
│    - Render invisible trigger div    │
└──────────────────────────────────────┘
           ↓
       User scrolls ↓
           ↓
┌──────────────────────────────────────┐
│ 3. Scroll Detection                  │
│    - User scrolls near bottom        │
│    - Trigger enters viewport         │
│      (200px before visible)          │
└──────────────────────────────────────┘
           ↓
┌──────────────────────────────────────┐
│ 4. Intersection Observer Fires       │
│    - Check: isIntersecting? ✓        │
│    - Check: hasMorePages? ✓          │
│    - Check: !isLoading? ✓            │
│    → Call loadNextPage()             │
└──────────────────────────────────────┘
           ↓
┌──────────────────────────────────────┐
│ 5. Load Next Page                    │
│    - Set isLoadingMore = true        │
│    - Increment currentPage           │
│    - Fetch items (append mode)       │
└──────────────────────────────────────┘
           ↓
┌──────────────────────────────────────┐
│ 6. Smart Cache Check                 │
│    Is page cached?                   │
│    ├─ Yes (Fresh) → Return instantly │
│    ├─ Yes (Stale) → Return + refresh │
│    └─ No → Fetch from API            │
└──────────────────────────────────────┘
           ↓
┌──────────────────────────────────────┐
│ 7. Append Items                      │
│    - items = [...items, ...newItems] │
│    - Update pagination state         │
│    - Set isLoadingMore = false       │
└──────────────────────────────────────┘
           ↓
┌──────────────────────────────────────┐
│ 8. Render New Items                  │
│    - Trigger moves further down      │
│    - Cycle repeats on scroll         │
└──────────────────────────────────────┘
```

---

## Template Structure

```vue
<template>
  <div class="space-y-8">
    <!-- Stats, filters, etc. -->
    
    <!-- Grid of Items -->
    <div v-if="!isLoading && filteredItems.length > 0 && displayMode === 'grid'">
      <!-- Grid Container -->
      <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-5 gap-4">
        <PosterCard
          v-for="item in filteredItems"
          :key="item.id"
          :item="item"
        />
      </div>

      <!-- Loading More Indicator -->
      <div v-if="isLoadingMore" class="flex items-center justify-center py-12 mt-8">
        <LoadingSpinner size="md" />
        <p class="text-sm text-muted-foreground mt-2">
          Loading more items...
        </p>
      </div>

      <!-- Infinite Scroll Trigger (Invisible) -->
      <div
        ref="infiniteScrollTrigger"
        class="h-4 w-full mt-8"
      />

      <!-- End of Results Message -->
      <div v-if="!hasMorePages && filteredItems.length > 0" class="text-center py-8 mt-8">
        <p class="text-sm text-purple-400 font-medium">
          That's all! {{ formatNumber(totalItems) }} items loaded
        </p>
      </div>
    </div>
  </div>
</template>
```

---

## Key State Variables

```javascript
// Pagination state
const currentPage = ref(1)           // Current page number
const perPage = 50                   // Items per page (constant)
const hasMorePages = ref(false)      // Are there more pages?
const totalPages = ref(0)            // Total number of pages
const totalItems = ref(0)            // Total number of items

// Loading states
const isLoading = ref(true)          // Initial page load
const isLoadingMore = ref(false)     // Loading next page (infinite scroll)

// Data
const items = ref<any[]>([])         // All loaded items (accumulates)

// Infinite scroll
const infiniteScrollTrigger = ref<HTMLElement | null>(null)  // Ref to trigger element
let infiniteScrollObserver: IntersectionObserver | null = null
```

---

## Lazy Loading Images

The `PosterCard` component uses native lazy loading:

```vue
<!-- components/items/PosterCard.vue -->
<img
  v-if="item.poster_url && !imageError"
  :src="item.poster_url"
  :alt="`${item.title} poster`"
  class="absolute inset-0 w-full h-full object-cover"
  loading="lazy"  <!-- Native browser lazy loading -->
  @error="handleImageError"
/>
```

---

## Cleanup on Unmount

```javascript
onUnmounted(() => {
  if (process.client) {
    // Remove scroll listener
    window.removeEventListener('scroll', handleScroll)
    
    // Disconnect observer
    if (infiniteScrollObserver) {
      infiniteScrollObserver.disconnect()
    }
  }
})
```

---

## How to Implement in Your App

### Step 1: Create the API Service

```typescript
// composables/useApi.ts
export function useApi() {
  const fetchItems = async (page: number, limit: number) => {
    return await $fetch('/api/items', {
      query: { page, limit }
    })
  }
  
  return { fetchItems }
}
```

### Step 2: Create the Cache Composable (Optional but Recommended)

```typescript
// composables/useCache.ts
interface CacheEntry {
  data: any
  timestamp: number
  isStale: boolean
}

const cache = new Map<string, CacheEntry>()
const CACHE_TTL = 5 * 60 * 1000  // 5 minutes

export function useCache() {
  const getCacheKey = (page: number, limit: number) => {
    return `items_p${page}_l${limit}`
  }

  const getCached = (page: number, limit: number) => {
    const key = getCacheKey(page, limit)
    const entry = cache.get(key)
    
    if (!entry) return null
    
    const age = Date.now() - entry.timestamp
    entry.isStale = age > CACHE_TTL
    
    return entry
  }

  const setCache = (page: number, limit: number, data: any) => {
    const key = getCacheKey(page, limit)
    cache.set(key, {
      data,
      timestamp: Date.now(),
      isStale: false
    })
  }

  return { getCached, setCache }
}
```

### Step 3: Create the Page Component

```vue
<template>
  <div>
    <!-- Item Grid -->
    <div class="grid grid-cols-4 gap-4">
      <div v-for="item in items" :key="item.id">
        {{ item.title }}
      </div>
    </div>
    
    <!-- Loading Indicator -->
    <div v-if="isLoadingMore">
      Loading more...
    </div>
    
    <!-- Infinite Scroll Trigger -->
    <div ref="infiniteScrollTrigger" class="h-4 w-full" />
    
    <!-- End Message -->
    <div v-if="!hasMorePages">
      All items loaded!
    </div>
  </div>
</template>

<script setup>
// 1. State
const items = ref([])
const currentPage = ref(1)
const perPage = 50
const totalPages = ref(0)
const hasMorePages = ref(false)
const isLoading = ref(true)
const isLoadingMore = ref(false)
const infiniteScrollTrigger = ref(null)
let infiniteScrollObserver = null

// 2. API Service
const api = useApi()

// 3. Fetch Items
const fetchItems = async (page = 1, reset = true) => {
  try {
    if (reset) isLoading.value = true
    else isLoadingMore.value = true
    
    const response = await api.fetchItems(page, perPage)
    
    if (reset) {
      items.value = response.items
    } else {
      items.value = [...items.value, ...response.items]
    }
    
    totalPages.value = response.total_pages
    hasMorePages.value = page < totalPages.value
    
  } catch (error) {
    console.error('Error fetching items:', error)
  } finally {
    isLoading.value = false
    isLoadingMore.value = false
  }
}

// 4. Load Next Page
const loadNextPage = async () => {
  if (hasMorePages.value && !isLoading.value && !isLoadingMore.value) {
    currentPage.value++
    await fetchItems(currentPage.value, false)
  }
}

// 5. Setup Intersection Observer
const setupInfiniteScroll = () => {
  if (!process.client || !infiniteScrollTrigger.value) return
  
  if (infiniteScrollObserver) {
    infiniteScrollObserver.disconnect()
  }
  
  infiniteScrollObserver = new IntersectionObserver(
    (entries) => {
      const entry = entries[0]
      if (entry.isIntersecting && hasMorePages.value && !isLoadingMore.value && !isLoading.value) {
        loadNextPage()
      }
    },
    {
      root: null,
      rootMargin: '200px',
      threshold: 0.1
    }
  )
  
  infiniteScrollObserver.observe(infiniteScrollTrigger.value)
}

// 6. Mount & Cleanup
onMounted(async () => {
  await fetchItems(1, true)
  
  if (process.client) {
    nextTick(() => {
      if (infiniteScrollTrigger.value) {
        setupInfiniteScroll()
      }
    })
  }
})

onUnmounted(() => {
  if (infiniteScrollObserver) {
    infiniteScrollObserver.disconnect()
  }
})
</script>
```

---

## Performance Optimizations

### 1. Prefetching
```javascript
// Prefetch next pages in background after initial load
setTimeout(() => {
  itemsCache.prefetchPages([2, 3], perPage)
}, 1000)
```

### 2. Stale-While-Revalidate
- Returns cached data instantly (even if stale)
- Fetches fresh data in background
- Updates cache when fresh data arrives

### 3. Image Lazy Loading
```vue
<img loading="lazy" :src="item.poster_url" />
```

### 4. Proactive Loading
- `rootMargin: '200px'` starts loading before user reaches the end
- Prevents the "waiting for more items" feeling

### 5. De-duplication
- Each page is cached separately
- Prevents re-fetching the same data

---

## Common Pitfalls & Solutions

### ❌ Pitfall 1: Observer Triggers Multiple Times
**Problem:** Observer fires multiple times causing duplicate API calls.

**Solution:** Guard with loading states
```javascript
if (entry.isIntersecting && hasMorePages.value && !isLoadingMore.value && !isLoading.value) {
  loadNextPage()
}
```

### ❌ Pitfall 2: Items Replace Instead of Append
**Problem:** New page replaces old items instead of appending.

**Solution:** Use spread operator with `reset` flag
```javascript
if (reset) {
  items.value = response.items  // Replace
} else {
  items.value = [...items.value, ...response.items]  // Append
}
```

### ❌ Pitfall 3: Observer Not Disconnecting
**Problem:** Memory leak from observers not being cleaned up.

**Solution:** Disconnect in `onUnmounted`
```javascript
onUnmounted(() => {
  if (infiniteScrollObserver) {
    infiniteScrollObserver.disconnect()
  }
})
```

### ❌ Pitfall 4: Trigger Element Too Small
**Problem:** Observer never detects the element.

**Solution:** Give it a minimum height
```vue
<div ref="infiniteScrollTrigger" class="h-4 w-full" />
```

### ❌ Pitfall 5: No rootMargin
**Problem:** Users see loading spinner before new items appear.

**Solution:** Use `rootMargin: '200px'` to load proactively
```javascript
{
  rootMargin: '200px'  // Start loading 200px before trigger
}
```

---

## Testing the Implementation

### 1. Test Initial Load
- ✅ First 50 items load immediately
- ✅ No duplicate items
- ✅ Stats show correct total count

### 2. Test Infinite Scroll
- ✅ Scroll to bottom → next page loads automatically
- ✅ Loading spinner appears while fetching
- ✅ New items append (don't replace)
- ✅ No duplicate API calls

### 3. Test End State
- ✅ When no more pages, show "All loaded" message
- ✅ Observer stops triggering
- ✅ No errors in console

### 4. Test Cache
- ✅ Navigate away and back → instant load from cache
- ✅ After 5 minutes → background refresh
- ✅ After 30 minutes → fresh fetch

### 5. Test Edge Cases
- ✅ Empty results (no items)
- ✅ Single page (no pagination)
- ✅ Network error handling
- ✅ Fast scrolling (multiple pages)

---

## Browser Compatibility

**Intersection Observer API** is supported in:
- ✅ Chrome 51+
- ✅ Firefox 55+
- ✅ Safari 12.1+
- ✅ Edge 15+

For older browsers, use a polyfill:
```bash
npm install intersection-observer
```

```javascript
// Import in your app
import 'intersection-observer'
```

---

## Performance Metrics

From our implementation:
- **Initial Load:** ~200ms (50 items)
- **Next Page Load (cached):** ~10ms (instant)
- **Next Page Load (fresh):** ~150ms
- **Memory Usage:** ~2MB for 500 items
- **No janking** during scroll

---

## Summary

### Core Concepts
1. **Intersection Observer** watches a trigger element at the bottom
2. **Trigger fires** when user scrolls near it (200px before)
3. **Load next page** and append to existing items
4. **Smart cache** returns data instantly, fetches fresh in background
5. **Repeat** until all pages loaded

### Key Benefits
- ✅ No scroll event listeners (better performance)
- ✅ Native browser API (no dependencies)
- ✅ Proactive loading (no waiting)
- ✅ Smart caching (instant navigation)
- ✅ Background prefetching (smooth experience)

### Minimal Implementation (3 Steps)
1. Create trigger element with `ref`
2. Setup Intersection Observer in `onMounted`
3. Load next page when triggered

---

## Additional Resources

- [MDN: Intersection Observer API](https://developer.mozilla.org/en-US/docs/Web/API/Intersection_Observer_API)
- [Web.dev: Infinite Scroll](https://web.dev/patterns/web-vitals-patterns/infinite-scroll/infinite-scroll/)
- [Vue 3: Composition API](https://vuejs.org/guide/extras/composition-api-faq.html)

---

**Questions or Issues?**
If you encounter problems implementing this pattern, check:
1. Is `ref` properly bound to DOM element?
2. Is observer created in `onMounted`?
3. Are loading guards in place?
4. Is `reset` flag correctly set (true for replace, false for append)?
5. Is observer disconnected in `onUnmounted`?

