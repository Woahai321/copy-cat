<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="page-header">
      <div>
        <h1 class="page-header-title flex items-center gap-3">
          <UIcon name="i-heroicons-chart-pie" class="page-header-icon" />
          Statistics
        </h1>
        <p class="page-header-subtitle">Insights into your library and system activity</p>
      </div>
      <button 
        @click="loadStats"
        class="btn-ghost"
      >
        <UIcon name="i-heroicons-arrow-path" class="w-4 h-4" />
        <span>Refresh</span>
      </button>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex items-center justify-center py-20">
      <div class="flex flex-col items-center gap-3">
        <UIcon name="i-heroicons-arrow-path" class="w-8 h-8 text-[var(--win-accent)] animate-spin" />
        <p class="text-sm text-gray-400">Crunching the numbers...</p>
      </div>
    </div>

    <div v-else-if="stats" class="space-y-8 animate-in fade-in duration-500">
      
      <!-- KPI Cards -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <!-- Library Size -->
          <div class="glass-panel p-6 flex flex-col gap-2">
             <div class="text-xs font-bold text-gray-500 uppercase tracking-widest flex items-center gap-2">
                 <UIcon name="i-heroicons-server" class="w-4 h-4" />
                 Total Size
             </div>
             <div class="text-3xl font-black text-white font-mono uppercase">
                 {{ formatBytes(stats.library_stats.total_size_bytes) }}
             </div>
             <div class="text-xs text-gray-400">
                 Across {{ stats.library_stats.total_items }} items
             </div>
          </div>

          <!-- Total Transferred -->
          <div class="glass-panel p-6 flex flex-col gap-2">
             <div class="text-xs font-bold text-gray-500 uppercase tracking-widest flex items-center gap-2">
                 <UIcon name="i-heroicons-arrow-down-tray" class="w-4 h-4" />
                 Total Transferred
             </div>
             <div class="text-3xl font-black text-[var(--win-accent)] font-mono uppercase">
                 {{ formatBytes(stats.job_stats.total_transferred_bytes) }}
             </div>
             <div class="text-xs text-gray-400">
                 Lifetime volume
             </div>
          </div>
          
          <!-- Library Split -->
          <div class="glass-panel p-6 flex flex-col gap-2">
             <div class="text-xs font-bold text-gray-500 uppercase tracking-widest flex items-center gap-2">
                 <UIcon name="i-heroicons-film" class="w-4 h-4" />
                 Library Split
             </div>
             <div class="flex items-end gap-2">
                 <div class="text-3xl font-black text-white font-mono">
                     {{ stats.library_stats.movies_count }}
                 </div>
                 <div class="text-xs text-gray-400 font-bold mb-1.5 uppercase">Movies</div>
             </div>
             <div class="text-xs text-gray-400 flex items-center gap-1">
                 <span class="text-white font-bold">{{ stats.library_stats.tv_count }}</span> TV Shows
             </div>
          </div>

          <!-- Success Rate -->
          <div class="glass-panel p-6 flex flex-col gap-2 group">
             <div class="text-xs font-bold text-gray-500 uppercase tracking-widest flex items-center gap-2">
                 <UIcon name="i-heroicons-check-circle" class="w-4 h-4" />
                 Success Rate
             </div>
             <div class="text-3xl font-black font-mono relative">
                 <span :class="stats.job_stats.success_rate > 90 ? 'text-emerald-400' : 'text-yellow-400'">{{ stats.job_stats.success_rate }}%</span>
             </div>
             <div class="text-xs text-gray-400">
                 {{ stats.job_stats.failed_count }} failed out of {{ stats.job_stats.completed_count + stats.job_stats.failed_count }}
             </div>
          </div>
      </div>

      <!-- Detail Row -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
          
          <!-- Activity Chart -->
          <div class="lg:col-span-2 glass-panel p-6">
              <h3 class="text-xs font-bold text-gray-500 uppercase tracking-widest mb-6 flex items-center gap-2">
                  <UIcon name="i-heroicons-chart-bar" class="w-4 h-4" />
                  Transfer Activity (Last 14 Days)
              </h3>
              
              <div class="h-64 flex items-end gap-2 relative mt-4">
                  <div 
                    v-for="(bytes, date) in stats.charts.activity" 
                    :key="date"
                    class="flex-1 flex flex-col items-center gap-2 group relative"
                  >
                      <!-- Tooltip -->
                      <div class="absolute bottom-full mb-2 bg-black/80 backdrop-blur text-xs px-2 py-1 rounded border border-white/10 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap z-10">
                          <div class="font-bold text-white">{{ date }}</div>
                          <div class="text-[var(--win-accent)]">{{ formatBytes(bytes) }}</div>
                      </div>
                      
                      <!-- Bar -->
                      <div 
                        class="w-full bg-[var(--win-accent)]/20 hover:bg-[var(--win-accent)]/40 rounded-t transition-colors relative overflow-hidden"
                        :style="{ height: `${Math.max((bytes / maxActivityBytes) * 100, 4)}%` }"
                      >
                         <div class="absolute bottom-0 left-0 right-0 h-1 bg-[var(--win-accent)]/50"></div>
                      </div>
                      
                      <!-- Label -->
                      <div class="text-[9px] text-gray-500 font-mono -rotate-45 origin-top-left translate-y-2 truncate w-full text-right opacity-50 group-hover:opacity-100">
                          {{ formatDateShort(date) }}
                      </div>
                  </div>
              </div>
          </div>

          <!-- Top Genres (Simple Bar List) -->
          <div class="glass-panel p-6">
              <h3 class="text-xs font-bold text-gray-500 uppercase tracking-widest mb-6 flex items-center gap-2">
                  <UIcon name="i-heroicons-tag" class="w-4 h-4" />
                  Top Genres
              </h3>
              <div class="space-y-4">
                  <div v-for="(count, genre) in stats.charts.genres" :key="genre" class="group">
                      <div class="flex justify-between text-xs mb-1">
                          <span class="font-bold text-gray-300 group-hover:text-white">{{ genre }}</span>
                          <span class="font-mono text-[var(--win-accent)]">{{ count }}</span>
                      </div>
                      <div class="h-1.5 bg-white/5 rounded-full overflow-hidden">
                          <div 
                            class="h-full bg-gradient-to-r from-purple-500 to-indigo-500" 
                            :style="{ width: `${(count / maxGenreCount) * 100}%` }"
                          ></div>
                      </div>
                  </div>
              </div>
          </div>
      </div>

      <!-- Lists Row -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <!-- Largest Files -->
          <div class="glass-panel p-0 overflow-hidden">
              <div class="p-6 border-b border-white/5 bg-black/20">
                  <h3 class="text-xs font-bold text-gray-500 uppercase tracking-widest flex items-center gap-2">
                      <UIcon name="i-heroicons-document" class="w-4 h-4" />
                      Largest Files
                  </h3>
              </div>
              <div class="divide-y divide-white/5">
                  <div 
                    v-for="file in stats.top_lists.largest_files" 
                    :key="file.path"
                    class="p-4 hover:bg-white/5 transition-colors flex items-center justify-between gap-4 group"
                  >
                      <div class="min-w-0">
                          <div class="text-sm font-bold text-white truncate">{{ file.title }}</div>
                          <div class="text-xs text-gray-500 truncate font-mono opacity-50">{{ file.path }}</div>
                      </div>
                      <div class="text-sm font-bold text-[var(--win-accent)] font-mono whitespace-nowrap">
                          {{ file.size }}
                      </div>
                  </div>
              </div>
          </div>

          <!-- Highest Rated -->
          <div class="glass-panel p-0 overflow-hidden">
              <div class="p-6 border-b border-white/5 bg-black/20">
                  <h3 class="text-xs font-bold text-gray-500 uppercase tracking-widest flex items-center gap-2">
                      <UIcon name="i-heroicons-star" class="w-4 h-4" />
                      Highest Rated
                  </h3>
              </div>
              <div class="divide-y divide-white/5">
                   <div 
                    v-for="item in stats.top_lists.highest_rated" 
                    :key="item.title"
                    class="p-4 hover:bg-white/5 transition-colors flex items-center justify-between gap-4"
                  >
                      <div class="flex items-center gap-3 min-w-0">
                          <div class="w-8 h-8 rounded-full bg-amber-500/10 flex items-center justify-center font-bold text-amber-500 text-xs border border-amber-500/20">
                              {{ item.rating?.toFixed(1) || '?' }}
                          </div>
                          <div class="min-w-0">
                              <div class="text-sm font-bold text-white truncate">{{ item.title }}</div>
                              <div class="text-xs text-gray-500 font-mono">{{ item.year }}</div>
                          </div>
                      </div>
                  </div>
              </div>
          </div>
      </div>
      
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  middleware: 'auth'
})

const { token } = useAuth()
const config = useRuntimeConfig()
const apiBase = config.public.apiBase

const loading = ref(true)
const stats = ref<any>(null)

// Computed for scaling charts
const maxActivityBytes = computed(() => {
    if (!stats.value) return 1
    const values = Object.values(stats.value.charts.activity) as number[]
    return Math.max(...values, 1)
})

const maxGenreCount = computed(() => {
    if (!stats.value) return 1
    const values = Object.values(stats.value.charts.genres) as number[]
    return Math.max(...values, 1)
})

const formatBytes = (bytes: number) => {
    if (!bytes) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`
}

const formatDateShort = (dateStr: string) => {
    const d = new Date(dateStr)
    return `${d.getMonth()+1}/${d.getDate()}`
}

const loadStats = async () => {
    loading.value = true
    try {
         const data = await $fetch(`${apiBase}/api/stats/full`, {
            headers: { 'Authorization': `Bearer ${token.value}` }
        })
        stats.value = data
    } catch (e) {
        console.error("Failed to load stats", e)
    } finally {
        loading.value = false
    }
}

onMounted(() => {
    loadStats()
})
</script>
