<template>
  <div class="space-y-8 pb-20">
    <!-- Header -->
    <div class="page-header">
      <div>
        <h1 class="page-header-title flex items-center gap-3">
          <UIcon name="i-heroicons-chart-pie" class="page-header-icon" />
          Statistics
        </h1>
        <p class="page-header-subtitle">Deep insights into your library and system performance.</p>
      </div>
      <button 
        @click="loadStats"
        class="btn-ghost"
        :disabled="loading"
      >
        <UIcon name="i-heroicons-arrow-path" class="w-4 h-4" :class="{ 'animate-spin': loading }" />
        <span>Refresh</span>
      </button>
    </div>

    <!-- Loading State -->
    <div v-if="loading && !stats" class="flex items-center justify-center py-40">
      <div class="flex flex-col items-center gap-4">
        <UIcon name="i-heroicons-arrow-path" class="w-10 h-10 text-[var(--win-accent)] animate-spin" />
        <p class="text-sm font-medium text-[var(--win-text-muted)] animate-pulse">Analyzing Library Data...</p>
      </div>
    </div>

    <div v-else-if="stats" class="space-y-8 animate-in fade-in duration-700 slide-in-from-bottom-4">
      
      <!-- Primary Metrics Grid -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <!-- Total Time to Watch -->
          <div class="glass-panel p-6 flex flex-col justify-between relative overflow-hidden group hover:border-[var(--win-accent)]/30 transition-colors">
             <div class="absolute -right-4 -top-4 w-24 h-24 bg-[var(--win-accent)]/5 rounded-full blur-2xl group-hover:bg-[var(--win-accent)]/10 transition-colors"></div>
             
             <div class="text-xs font-bold text-[var(--win-text-muted)] uppercase tracking-widest flex items-center gap-2 mb-2">
                 <UIcon name="i-heroicons-clock" class="w-4 h-4" />
                 Time to Watch
             </div>
             <div>
                 <div class="text-3xl font-black text-[var(--win-text-primary)] font-mono tracking-tight flex items-baseline gap-1">
                     {{ formatDuration(stats.library_stats.total_runtime_minutes).value }}
                     <span class="text-sm font-bold text-[var(--win-text-muted)] uppercase">{{ formatDuration(stats.library_stats.total_runtime_minutes).unit }}</span>
                 </div>
                 <div class="text-xs text-[var(--win-text-muted)] mt-1">Non-stop entertainment</div>
             </div>
          </div>

          <!-- Total Size -->
          <div class="glass-panel p-6 flex flex-col justify-between relative overflow-hidden group hover:border-[var(--win-accent)]/30 transition-colors">
             <div class="text-xs font-bold text-[var(--win-text-muted)] uppercase tracking-widest flex items-center gap-2 mb-2">
                 <UIcon name="i-heroicons-server" class="w-4 h-4" />
                 Library Size
             </div>
             <div>
                 <div class="text-3xl font-black text-[var(--win-accent)] font-mono tracking-tight">
                     {{ formatBytes(stats.library_stats.total_size_bytes) }}
                 </div>
                 <div class="text-xs text-[var(--win-text-muted)] mt-1 flex items-center gap-1">
                    <span class="font-bold text-[var(--win-text-primary)]">{{ stats.library_stats.total_items }}</span> Total Items
                 </div>
             </div>
          </div>
          
          <!-- Avg File Size -->
          <div class="glass-panel p-6 flex flex-col justify-between relative overflow-hidden group hover:border-[var(--win-accent)]/30 transition-colors">
             <div class="text-xs font-bold text-[var(--win-text-muted)] uppercase tracking-widest flex items-center gap-2 mb-2">
                 <UIcon name="i-heroicons-scale" class="w-4 h-4" />
                 Avg Quality
             </div>
             <div>
                 <div class="text-3xl font-black text-[var(--win-text-primary)] font-mono tracking-tight">
                     {{ formatBytes(stats.library_stats.avg_file_size) }}
                 </div>
                 <div class="text-xs text-[var(--win-text-muted)] mt-1">Per media item</div>
             </div>
          </div>

          <!-- Success Rate -->
          <div class="glass-panel p-6 flex flex-col justify-between relative overflow-hidden group hover:border-[var(--win-accent)]/30 transition-colors">
             <div class="text-xs font-bold text-[var(--win-text-muted)] uppercase tracking-widest flex items-center gap-2 mb-2">
                 <UIcon name="i-heroicons-check-badge" class="w-4 h-4" />
                 Copy Health
             </div>
             <div>
                 <div class="text-3xl font-black font-mono tracking-tight"
                    :class="stats.job_stats.success_rate >= 95 ? 'text-emerald-400' : stats.job_stats.success_rate >= 80 ? 'text-amber-400' : 'text-red-400'"
                 >
                     {{ stats.job_stats.success_rate }}%
                 </div>
                 <div class="text-xs text-[var(--win-text-muted)] mt-1">
                     {{ stats.job_stats.completed_count }} jobs completed
                 </div>
             </div>
          </div>
      </div>

      <!-- Main Visualizations Row -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
          
          <!-- Activity Chart (Area Graph) -->
          <div class="lg:col-span-2 glass-panel p-6 flex flex-col">
              <div class="flex items-center justify-between mb-6">
                  <h3 class="text-xs font-bold text-[var(--win-text-muted)] uppercase tracking-widest flex items-center gap-2">
                      <UIcon name="i-heroicons-presentation-chart-line" class="w-4 h-4" />
                      Transfer Volume (14 Days)
                  </h3>
                  <div class="text-xs font-mono text-[var(--win-accent)] bg-[var(--win-accent)]/10 px-2 py-1 rounded">
                      Total: {{ formatBytes(stats.job_stats.total_transferred_bytes) }}
                  </div>
              </div>
              
              <!-- SVG Chart -->
              <div class="flex-1 min-h-[250px] relative w-full flex items-end gap-1">
                   <div v-for="(bytes, date, idx) in stats.charts.activity" :key="date" 
                        class="flex-1 flex flex-col justify-end group relative h-full"
                        @mouseenter="hoveredDate = date"
                        @mouseleave="hoveredDate = null"
                   >
                        <!-- Hover Line -->
                        <div class="absolute inset-x-0 bottom-0 top-0 bg-white/5 opacity-0 group-hover:opacity-100 transition-opacity rounded-sm"></div>

                        <!-- Bar -->
                        <div 
                           class="w-full bg-gradient-to-t from-[var(--win-accent)]/20 to-[var(--win-accent)]/60 rounded-t relative transition-all duration-300 group-hover:from-[var(--win-accent)]/40 group-hover:to-[var(--win-accent)]"
                           :style="{ height: `${Math.max((bytes / maxActivityBytes) * 100, 2)}%` }"
                        ></div>
                        
                        <!-- X-Axis Label -->
                        <div class="mt-2 text-[10px] text-center text-[var(--win-text-muted)] font-mono transform -rotate-45 origin-top-left translate-y-2 opacity-50 group-hover:opacity-100 transition-opacity">
                            {{ formatDateShort(date) }}
                        </div>

                        <!-- Floating Tooltip -->
                        <div class="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 pointer-events-none opacity-0 group-hover:opacity-100 transition-all z-20 transform translate-y-2 group-hover:translate-y-0">
                            <div class="bg-[var(--win-bg-base)] border border-white/10 rounded-lg p-3 shadow-xl backdrop-blur-md">
                                <div class="text-xs font-bold text-[var(--win-text-primary)] whitespace-nowrap mb-1">{{ date }}</div>
                                <div class="text-sm font-black text-[var(--win-accent)] font-mono whitespace-nowrap">{{ formatBytes(bytes) }}</div>
                            </div>
                        </div>
                   </div>
              </div>
          </div>

          <!-- Decade Distribution -->
          <div class="glass-panel p-6 flex flex-col">
              <h3 class="text-xs font-bold text-[var(--win-text-muted)] uppercase tracking-widest mb-6 flex items-center gap-2">
                  <UIcon name="i-heroicons-calendar" class="w-4 h-4" />
                  Era Breakdown
              </h3>
              <div class="space-y-3 overflow-y-auto max-h-[250px] pr-2 custom-scrollbar">
                  <div v-for="(count, decade) in stats.charts.decades" :key="decade" class="group">
                      <div class="flex justify-between items-center text-xs mb-1.5">
                          <span class="font-bold text-[var(--win-text-secondary)] group-hover:text-[var(--win-text-primary)]">{{ decade }}</span>
                          <span class="font-mono text-[var(--win-accent)]">{{ count }}</span>
                      </div>
                      <div class="h-2 bg-white/5 rounded-full overflow-hidden">
                          <div 
                            class="h-full bg-gradient-to-r from-cyan-500 to-blue-500 rounded-full transition-all duration-1000 ease-out" 
                            :style="{ width: `${(count / maxDecadeCount) * 100}%` }"
                          ></div>
                      </div>
                  </div>
              </div>
          </div>
      </div>

      <!-- Secondary Metrics Row -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          
          <!-- Quality Distribution (Resolutions) -->
          <div class="glass-panel p-6">
              <h3 class="text-xs font-bold text-[var(--win-text-muted)] uppercase tracking-widest mb-6 flex items-center gap-2">
                  <UIcon name="i-heroicons-eye" class="w-4 h-4" />
                  Video Quality
              </h3>
              <div class="space-y-4">
                  <div v-for="res in sortedResolutions" :key="res.label" class="flex items-center gap-4">
                      <div class="w-12 text-xs font-bold text-[var(--win-text-secondary)]">{{ res.label }}</div>
                      <div class="flex-1 h-3 bg-white/5 rounded-full overflow-hidden relative">
                          <div class="absolute inset-y-0 left-0 bg-[var(--win-accent)] rounded-full transition-all duration-1000" :style="{ width: res.percent + '%' }"></div>
                      </div>
                      <div class="w-10 text-right text-xs font-mono opacity-60">{{ res.count }}</div>
                  </div>
              </div>
          </div>

          <!-- Audio Codecs -->
          <div class="glass-panel p-6">
              <h3 class="text-xs font-bold text-[var(--win-text-muted)] uppercase tracking-widest mb-6 flex items-center gap-2">
                  <UIcon name="i-heroicons-speaker-wave" class="w-4 h-4" />
                  Audio Tech
              </h3>
              <div class="flex flex-wrap gap-2">
                   <div 
                     v-for="(count, codec) in stats.charts.audio_codecs" 
                     :key="codec"
                     class="px-3 py-1.5 rounded-lg bg-[var(--glass-level-2-bg)] border border-white/5 flex items-center gap-2 hover:border-[var(--win-accent)]/50 transition-colors"
                   >
                      <span class="text-xs font-bold text-[var(--win-text-primary)] uppercase">{{ codec }}</span>
                      <span class="text-[10px] font-mono text-[var(--win-accent)] bg-[var(--win-accent)]/10 px-1 rounded">{{ count }}</span>
                   </div>
              </div>
          </div>

          <!-- Top Genres (Condensed) -->
          <div class="glass-panel p-6">
              <h3 class="text-xs font-bold text-[var(--win-text-muted)] uppercase tracking-widest mb-6 flex items-center gap-2">
                  <UIcon name="i-heroicons-tag" class="w-4 h-4" />
                  Top Genres
              </h3>
               <div class="space-y-3">
                  <div v-for="(count, genre) in stats.charts.genres" :key="genre" class="group">
                      <div class="flex justify-between text-xs mb-1">
                          <span class="font-bold text-[var(--win-text-secondary)] opacity-80 group-hover:text-[var(--win-text-primary)] group-hover:opacity-100">{{ genre }}</span>
                          <span class="font-mono text-[var(--win-text-muted)]">{{ count }}</span>
                      </div>
                      <div class="h-1.5 bg-white/5 rounded-full overflow-hidden">
                          <div 
                            class="h-full bg-[var(--win-text-primary)] opacity-40 group-hover:opacity-100 transition-opacity" 
                            :style="{ width: `${(count / maxGenreCount) * 100}%` }"
                          ></div>
                      </div>
                  </div>
              </div>
          </div>
      </div>

       <!-- Largest Files Table -->
       <div class="glass-panel p-0 overflow-hidden">
          <div class="p-6 border-b border-white/5 bg-[var(--glass-level-2-bg)] flex justify-between items-center">
              <h3 class="text-xs font-bold text-[var(--win-text-muted)] uppercase tracking-widest flex items-center gap-2">
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
                  <div class="flex items-center gap-3 min-w-0">
                      <div class="w-8 h-8 rounded-lg bg-white/5 flex items-center justify-center text-[var(--win-text-muted)]">
                          <UIcon name="i-heroicons-film" class="w-4 h-4" />
                      </div>
                      <div class="min-w-0">
                          <div class="text-sm font-bold text-[var(--win-text-primary)] truncate group-hover:text-[var(--win-accent)] transition-colors">{{ file.title }}</div>
                          <div class="text-[10px] text-[var(--win-text-muted)] truncate font-mono opacity-50">{{ file.path }}</div>
                      </div>
                  </div>
                  <div class="text-sm font-bold text-[var(--win-text-primary)] font-mono whitespace-nowrap bg-white/5 px-2 py-1 rounded">
                      {{ file.size }}
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
const hoveredDate = ref<string | null>(null)

// Max values for chart scaling
const maxActivityBytes = computed(() => {
    if (!stats.value?.charts?.activity) return 1
    const values = Object.values(stats.value.charts.activity) as number[]
    return Math.max(...values, 1)
})

const maxGenreCount = computed(() => {
    if (!stats.value?.charts?.genres) return 1
    const values = Object.values(stats.value.charts.genres) as number[]
    return Math.max(...values, 1)
})

const maxDecadeCount = computed(() => {
    if (!stats.value?.charts?.decades) return 1
    const values = Object.values(stats.value.charts.decades) as number[]
    return Math.max(...values, 1)
})

const sortedResolutions = computed(() => {
    if (!stats.value?.charts?.resolutions) return []
    const total = Object.values(stats.value.charts.resolutions).reduce((a: any, b: any) => a + b, 0) as number
    return Object.entries(stats.value.charts.resolutions)
        .map(([label, count]: [string, any]) => ({
            label,
            count,
            percent: total > 0 ? (count / total) * 100 : 0
        }))
        .sort((a, b) => b.count - a.count)
})

// Format Helpers
const formatDuration = (minutes: number) => {
    if (!minutes) return { value: 0, unit: 'Mins' }
    if (minutes < 60) return { value: minutes, unit: 'Mins' }
    const hours = Math.floor(minutes / 60)
    if (hours < 24) return { value: hours, unit: 'Hours' }
    const days = (hours / 24).toFixed(1)
    return { value: days, unit: 'Days' }
}

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

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 4px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.02);
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 10px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.2);
}
</style>
